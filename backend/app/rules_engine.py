import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict
from pydantic import BaseModel
from .log_parser import LogEntry
from .config import settings


class IncidentAlert(BaseModel):
    alert_id: str
    rule_name: str
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    mitre_technique: str
    mitre_tactic: str
    source_ip: str
    target_user: str
    timestamp: str
    event_count: int
    evidence_logs: List[Dict[str, Any]]
    suggested_investigation_query: str


def parse_dt(ts_str: str) -> Optional[datetime]:
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%b %d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(ts_str.split(".")[0].replace("Z", ""), fmt)
            if dt.year == 1900:  # syslog without year
                dt = dt.replace(year=datetime.utcnow().year)
            return dt
        except ValueError:
            continue
    return None


class SecurityRulesEngine:
    """Deterministic, high-throughput security correlation engine for log analysis."""

    def __init__(self):
        self.brute_force_threshold = settings.BRUTE_FORCE_THRESHOLD
        self.brute_force_window = settings.BRUTE_FORCE_WINDOW_SECONDS
        self.port_scan_threshold = settings.PORT_SCAN_THRESHOLD

    def analyze(self, logs: List[LogEntry]) -> List[IncidentAlert]:
        alerts: List[IncidentAlert] = []
        
        # Correlate Rules
        alerts.extend(self._detect_brute_force(logs))
        alerts.extend(self._detect_privilege_escalation(logs))
        alerts.extend(self._detect_web_command_injection(logs))
        alerts.extend(self._detect_port_scans(logs))
        alerts.extend(self._detect_credential_stuffing_multi_account(logs))
        
        # Sort by severity priority: CRITICAL > HIGH > MEDIUM > LOW
        priority = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        alerts.sort(key=lambda a: (priority.get(a.severity, 4), a.timestamp), reverse=False)
        return alerts

    def _detect_brute_force(self, logs: List[LogEntry]) -> List[IncidentAlert]:
        """Detect repeated failed authentications from the same source IP."""
        alerts: List[IncidentAlert] = []
        ip_failures = defaultdict(list)

        for log in logs:
            is_fail = (
                log.action == "LOGIN_FAILED" or 
                log.status == "FAILURE" or 
                "failed" in log.raw_message.lower() or 
                "authentication failure" in log.raw_message.lower()
            )
            if is_fail and log.source_ip != "N/A":
                ip_failures[log.source_ip].append(log)

        for ip, fail_logs in ip_failures.items():
            if len(fail_logs) >= self.brute_force_threshold:
                # Check if attacker eventually succeeded (very critical)
                success_logs = [
                    l for l in logs 
                    if l.source_ip == ip and (l.action == "LOGIN_SUCCESS" or l.status == "SUCCESS")
                ]
                has_success = len(success_logs) > 0
                
                severity = "CRITICAL" if has_success else "HIGH"
                desc = (
                    f"Observed {len(fail_logs)} failed login attempts from source IP {ip}."
                    + (f" WARNING: A successful login was subsequent detected for user '{success_logs[0].user}'!" if has_success else " No subsequent successful login detected yet.")
                )
                
                target_user = fail_logs[0].user if fail_logs[0].user != "N/A" else "multiple_targets"
                
                alerts.append(IncidentAlert(
                    alert_id=f"ALERT-BF-{ip.replace('.', '_')}",
                    rule_name="RULE_BRUTE_FORCE_AUTH",
                    title=f"Brute-Force Login Campaign ({ip})" + (" [COMPROMISED]" if has_success else ""),
                    description=desc,
                    severity=severity,
                    mitre_technique="T1110 - Brute Force",
                    mitre_tactic="Credential Access",
                    source_ip=ip,
                    target_user=target_user,
                    timestamp=fail_logs[-1].timestamp,
                    event_count=len(fail_logs) + len(success_logs),
                    evidence_logs=[l.model_dump() for l in (fail_logs[:10] + success_logs[:2])],
                    suggested_investigation_query=f"Analyze failed login attempts from IP {ip} and verify if account {target_user} was breached."
                ))
        return alerts

    def _detect_privilege_escalation(self, logs: List[LogEntry]) -> List[IncidentAlert]:
        """Detect unauthorized sudo escalation, suspicious su, or dangerous admin binaries."""
        alerts: List[IncidentAlert] = []
        suspicious_cmds = [
            "/bin/bash", "/bin/sh", "chmod +s", "visudo", "/etc/shadow", 
            "useradd", "chown", "curl", "wget", "nc ", "ncat", "socat"
        ]

        for log in logs:
            raw_l = log.raw_message.lower()
            is_priv = (
                log.action == "SUDO_EXEC" or 
                "sudo:" in raw_l or 
                "session opened for user root" in raw_l
            )
            has_suspicious_bin = any(cmd in raw_l for cmd in suspicious_cmds)

            if is_priv and (has_suspicious_bin or "not in sudoers" in raw_l):
                severity = "HIGH" if "not in sudoers" not in raw_l else "MEDIUM"
                alerts.append(IncidentAlert(
                    alert_id=f"ALERT-PE-{log.id}",
                    rule_name="RULE_PRIVILEGE_ESCALATION",
                    title=f"Suspicious Privilege Escalation by {log.user}",
                    description=f"User '{log.user}' executed elevated command or attempted unauthorized root access: {log.raw_message}",
                    severity=severity,
                    mitre_technique="T1548.003 - Sudo and Sudo Caching",
                    mitre_tactic="Privilege Escalation",
                    source_ip=log.source_ip,
                    target_user=log.user,
                    timestamp=log.timestamp,
                    event_count=1,
                    evidence_logs=[log.model_dump()],
                    suggested_investigation_query=f"Investigate sudo execution by user {log.user} and check MITRE T1548 containment recommendations."
                ))
        return alerts

    def _detect_web_command_injection(self, logs: List[LogEntry]) -> List[IncidentAlert]:
        """Detect SQL injection, Remote Code Execution (RCE), and Path Traversal payloads."""
        alerts: List[IncidentAlert] = []
        patterns = [
            (r'(\.\./|\.\.\\)', "T1083 - File and Directory Discovery", "Path Traversal attempt"),
            (r'(\bunion\b.*\bselect\b|\bor\b\s+1=1|\bdrop\b\s+\btable\b)', "T1190 - Exploit Public-Facing Application", "SQL Injection payload"),
            (r'(;|\||`|\$\().*(bash|sh|cmd\.exe|powershell|cat\s+/etc/passwd|whoami)', "T1059 - Command and Scripting Interpreter", "Command Injection / Web Shell trigger"),
            (r'(<script|javascript:|alert\()', "T1189 - Drive-by Compromise", "Cross-Site Scripting (XSS) attempt")
        ]

        for log in logs:
            for regex, tech, name in patterns:
                if re.search(regex, log.raw_message, re.IGNORECASE):
                    alerts.append(IncidentAlert(
                        alert_id=f"ALERT-WEB-{log.id}",
                        rule_name="RULE_WEB_EXPLOITATION",
                        title=f"Web Exploit Payload Detected ({name})",
                        description=f"Host or Web server logged an active exploit attempt from {log.source_ip}: {log.raw_message}",
                        severity="CRITICAL",
                        mitre_technique=tech,
                        mitre_tactic="Initial Access / Execution",
                        source_ip=log.source_ip,
                        target_user=log.user,
                        timestamp=log.timestamp,
                        event_count=1,
                        evidence_logs=[log.model_dump()],
                        suggested_investigation_query=f"Investigate exploit payload from {log.source_ip} and review web application firewall guidelines."
                    ))
                    break
        return alerts

    def _detect_port_scans(self, logs: List[LogEntry]) -> List[IncidentAlert]:
        """Detect port reconnaissance or sweeping from an external host."""
        alerts: List[IncidentAlert] = []
        scan_events = defaultdict(list)

        for log in logs:
            raw_l = log.raw_message.lower()
            if "port" in raw_l and ("scan" in raw_l or "connection refused" in raw_l or "reset" in raw_l or "drop" in raw_l):
                if log.source_ip != "N/A":
                    scan_events[log.source_ip].append(log)

        for ip, ev_list in scan_events.items():
            if len(ev_list) >= self.port_scan_threshold:
                alerts.append(IncidentAlert(
                    alert_id=f"ALERT-SCAN-{ip.replace('.', '_')}",
                    rule_name="RULE_RECON_PORT_SCAN",
                    title=f"Reconnaissance Port Scan Probe ({ip})",
                    description=f"Observed {len(ev_list)} connection attempts to multiple ports from source {ip}.",
                    severity="MEDIUM",
                    mitre_technique="T1046 - Network Service Discovery",
                    mitre_tactic="Discovery",
                    source_ip=ip,
                    target_user="N/A",
                    timestamp=ev_list[-1].timestamp,
                    event_count=len(ev_list),
                    evidence_logs=[l.model_dump() for l in ev_list[:10]],
                    suggested_investigation_query=f"Review port scan from IP {ip} and verify firewall block rules."
                ))
        return alerts

    def _detect_credential_stuffing_multi_account(self, logs: List[LogEntry]) -> List[IncidentAlert]:
        """Detect single IP attempting authentication across multiple distinct usernames."""
        alerts: List[IncidentAlert] = []
        ip_to_users = defaultdict(set)
        ip_logs = defaultdict(list)

        for log in logs:
            if (log.action == "LOGIN_FAILED" or log.status == "FAILURE") and log.source_ip != "N/A" and log.user != "N/A":
                ip_to_users[log.source_ip].add(log.user)
                ip_logs[log.source_ip].append(log)

        for ip, users in ip_to_users.items():
            if len(users) >= 4:  # 4 or more distinct usernames tested from 1 IP
                alerts.append(IncidentAlert(
                    alert_id=f"ALERT-STUFF-{ip.replace('.', '_')}",
                    rule_name="RULE_CREDENTIAL_STUFFING",
                    title=f"Credential Stuffing / Password Spray ({ip})",
                    description=f"Source IP {ip} targeted {len(users)} different user accounts: {', '.join(list(users)[:6])}.",
                    severity="HIGH",
                    mitre_technique="T1110.003 - Password Spraying",
                    mitre_tactic="Credential Access",
                    source_ip=ip,
                    target_user="multiple",
                    timestamp=ip_logs[ip][-1].timestamp,
                    event_count=len(ip_logs[ip]),
                    evidence_logs=[l.model_dump() for l in ip_logs[ip][:10]],
                    suggested_investigation_query=f"Evaluate password spraying pattern from {ip} across target accounts {', '.join(list(users)[:4])}."
                ))
        return alerts


# Singleton instance
rules_engine = SecurityRulesEngine()
