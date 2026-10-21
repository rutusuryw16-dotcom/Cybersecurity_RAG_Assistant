import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .config import settings
from .log_parser import (
    parse_syslog_auth, parse_csv_logs, chunk_text, DocumentChunk
)
from .vector_store import vector_store


def generate_benchmark_datasets():
    """Generates realistic test incident logs and reference cybersecurity documentation."""
    base_time = datetime.utcnow() - timedelta(minutes=45)
    
    # 1. SAMPLE AUTH BRUTE FORCE LOG (50 failed logins from 192.0.2.10 in 2 minutes)
    auth_lines = []
    attacker_ip = "192.0.2.10"
    target_users = ["root", "admin", "ubuntu", "test", "deploy", "guest", "oracle", "postgres"]
    
    t = base_time
    # 48 failed attempts in 110 seconds
    for i in range(1, 49):
        t += timedelta(seconds=2.2)
        user = target_users[i % len(target_users)]
        ts_str = t.strftime("%b %d %H:%M:%S")
        port = 40000 + i
        auth_lines.append(
            f"{ts_str} cloud-soc-host sshd[{14200+i}]: Failed password for invalid user {user} from {attacker_ip} port {port} ssh2"
        )
    
    # 2 more failed attempts
    t += timedelta(seconds=2)
    auth_lines.append(f"{t.strftime('%b %d %H:%M:%S')} cloud-soc-host sshd[14251]: Failed password for deploy from {attacker_ip} port 40050 ssh2")
    t += timedelta(seconds=2)
    auth_lines.append(f"{t.strftime('%b %d %H:%M:%S')} cloud-soc-host sshd[14252]: Failed password for deploy from {attacker_ip} port 40051 ssh2")
    
    # Critical evidence: One subsequent success!
    t += timedelta(seconds=5)
    auth_lines.append(f"{t.strftime('%b %d %H:%M:%S')} cloud-soc-host sshd[14253]: Accepted password for deploy from {attacker_ip} port 40052 ssh2")
    auth_lines.append(f"{t.strftime('%b %d %H:%M:%S')} cloud-soc-host systemd-logind[910]: New session 42 of user deploy.")

    # Subsequent sudo abuse by the compromised user
    t += timedelta(seconds=12)
    auth_lines.append(f"{t.strftime('%b %d %H:%M:%S')} cloud-soc-host sudo:   deploy : TTY=pts/1 ; PWD=/home/deploy ; USER=root ; COMMAND=/bin/bash")
    auth_lines.append(f"{t.strftime('%b %d %H:%M:%S')} cloud-soc-host sudo: pam_unix(sudo:session): session opened for user root(uid=0) by deploy(uid=1001)")

    auth_log_content = "\n".join(auth_lines)
    auth_file_path = settings.LOGS_DIR / "auth_bruteforce_incident.log"
    with open(auth_file_path, "w", encoding="utf-8") as f:
        f.write(auth_log_content)

    # 2. SAMPLE WEB APPLICATION ATTACKS CSV
    web_csv_lines = [
        "timestamp,source_ip,dest_ip,user,method,uri,status_code,user_agent,action",
        f"{(base_time + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')},203.0.113.88,10.0.0.15,anonymous,GET,/api/products?id=1' UNION SELECT 1,username,password FROM users--,403,sqlmap/1.6,SQL_INJECTION",
        f"{(base_time + timedelta(minutes=6)).strftime('%Y-%m-%d %H:%M:%S')},203.0.113.88,10.0.0.15,anonymous,POST,/api/v1/tools/ping?target=127.0.0.1; cat /etc/passwd,500,Mozilla/5.0,COMMAND_INJECTION",
        f"{(base_time + timedelta(minutes=7)).strftime('%Y-%m-%d %H:%M:%S')},203.0.113.88,10.0.0.15,anonymous,GET,/static/../../../../etc/shadow,403,curl/7.88.1,PATH_TRAVERSAL",
        f"{(base_time + timedelta(minutes=8)).strftime('%Y-%m-%d %H:%M:%S')},203.0.113.88,10.0.0.15,anonymous,POST,/upload/shell.php,201,python-requests/2.31,WEBSHELL_UPLOAD"
    ]
    web_csv_content = "\n".join(web_csv_lines)
    web_file_path = settings.LOGS_DIR / "web_exploitation_attacks.csv"
    with open(web_file_path, "w", encoding="utf-8") as f:
        f.write(web_csv_content)

    # 3. SAMPLE PORT SCAN LOGS
    scan_lines = []
    scanner_ip = "198.51.100.44"
    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 1433, 3306, 3389, 5432, 8080, 8443]
    for i, port in enumerate(ports):
        st = base_time + timedelta(seconds=i * 3)
        scan_lines.append(
            f"{st.strftime('%b %d %H:%M:%S')} edge-firewall kernel: [UFW BLOCK] IN=eth0 OUT= SRC={scanner_ip} DST=10.0.0.50 PROTO=TCP SPT={50000+i} DPT={port} connection refused"
        )
    scan_log_content = "\n".join(scan_lines)
    scan_file_path = settings.LOGS_DIR / "port_scan_reconnaissance.log"
    with open(scan_file_path, "w", encoding="utf-8") as f:
        f.write(scan_log_content)

    # 4. MITRE ATT&CK KNOWLEDGE BASE DOCUMENTS
    mitre_t1110 = """MITRE ATT&CK Technique T1110: Brute Force
Tactic: Credential Access (TA0006)
Sub-techniques:
- T1110.001: Password Guessing (systematically guessing passwords for an account)
- T1110.002: Password Cracking
- T1110.003: Password Spraying (using a few common passwords against many accounts)
- T1110.004: Credential Stuffing (using stolen credentials from other breaches)

Description:
Adversaries may use brute force techniques to gain access to accounts when passwords are unknown or when password hashes are obtained. Repeated authentication failures within a brief duration from a common IP address indicate automated password guessing or credential stuffing tools (e.g. Hydra, Medusa).

Detection Guidelines:
1. Monitor authentication logs (such as /var/log/auth.log or Windows Event ID 4625).
2. Establish thresholds for failed logon attempts (e.g., more than 5 failures within 2 minutes).
3. Check for geographic or network velocity anomalies.
4. Most crucially, verify if a sequence of failed authentications is immediately followed by an Event ID 4624 (Successful Logon) or SSH 'Accepted password', which confirms the attack successfully breached the credential.

Mitigation:
- M1036 Account Use Policies: Enforce account lockout thresholds (e.g. 5 failed attempts locks for 15 minutes).
- M1032 Multi-Factor Authentication: Require MFA on all externally exposed endpoints.
- M1018 User Account Management: Disable root and default administrator logins over SSH.
- M1037 Filter Network Traffic: Implement rate limiting and automatic IP banning with Fail2Ban or cloud security groups.
"""
    with open(settings.KB_DIR / "MITRE_T1110_Brute_Force.txt", "w", encoding="utf-8") as f:
        f.write(mitre_t1110)

    # 5. NIST SP 800-61 REV 2 INCIDENT HANDLING GUIDE
    nist_guide = """NIST Special Publication 800-61 Revision 2: Computer Security Incident Handling Guide
Phase 1: Preparation
Organizations must maintain log management infrastructures, forensic toolkits, and clear incident response communication channels.

Phase 2: Detection and Analysis
Signs of an Incident:
- Precursors: Network port scans, vulnerability scans, audit log alerts.
- Indicators: High volume of failed authentications, unexpected file modifications, unauthorized privilege escalation, anomalous outbound connections.
Investigation Steps:
1. Identify the scope of compromised accounts and hosts.
2. Determine the attack vector (brute-force, unpatched web vulnerability, compromised credential).
3. Validate evidence integrity by preserving original timestamps and cryptographic hashes.

Phase 3: Containment, Eradication, and Recovery
1. Short-Term Containment: Isolate the affected subnet or null-route malicious source IP addresses.
2. Eradication: Terminate unauthorized background processes, delete uploaded web shells, revoke compromised SSH keys and API tokens.
3. Recovery: Restore affected systems from clean backups, reset user credentials, and restore connectivity under enhanced monitoring.

Phase 4: Post-Incident Activity (Lessons Learned)
Conduct post-mortem analysis within two weeks. Update intrusion detection signatures and rules to prevent recurrence.
"""
    with open(settings.KB_DIR / "NIST_SP800_61_Incident_Guide.txt", "w", encoding="utf-8") as f:
        f.write(nist_guide)

    # 6. MITRE ATT&CK T1548 PRIVILEGE ESCALATION
    mitre_t1548 = """MITRE ATT&CK Technique T1548: Abuse Elevation Control Mechanism
Tactic: Privilege Escalation (TA0004), Defense Evasion (TA0005)
Sub-technique: T1548.003 - Sudo and Sudo Caching

Description:
Adversaries may execute commands with elevated root privileges using sudo without requiring authorization, or exploit misconfigurations in the /etc/sudoers file (such as NOPASSWD or dangerous binaries like vi, bash, find, tar).

Detection:
1. Audit sudo execution events in /var/log/auth.log or /var/log/secure.
2. Flag instances where non-administrative accounts execute interactive shells (/bin/bash, /bin/sh).
3. Review auditd rules monitoring writes to /etc/sudoers and /etc/sudoers.d/.

Mitigation:
- Adhere strictly to the Principle of Least Privilege (PoLP).
- Restrict sudoers permissions to specific, necessary utility arguments instead of ALL=(ALL:ALL) ALL.
- Maintain immutable audit logging for root-level session executions.
"""
    with open(settings.KB_DIR / "MITRE_T1548_Privilege_Escalation.txt", "w", encoding="utf-8") as f:
        f.write(mitre_t1548)

    # Ingest into Vector Store
    # 1. Ingest Knowledge Base Chunks
    kb_files = [
        ("MITRE_T1110_Brute_Force.txt", mitre_t1110),
        ("NIST_SP800_61_Incident_Guide.txt", nist_guide),
        ("MITRE_T1548_Privilege_Escalation.txt", mitre_t1548),
    ]
    all_chunks = []
    for fname, text in kb_files:
        chunks = chunk_text(text, source_file=fname, chunk_size=400, overlap=60, extra_meta={"type": "standard"})
        for c in chunks:
            c.metadata["category"] = "knowledge_base"
        vector_store.add_chunks(chunks, category="knowledge_base")

    # 2. Ingest Log Chunks
    parsed_auth = parse_syslog_auth(auth_log_content, "auth_bruteforce_incident.log")
    # Group logs in windows of 5 entries
    for i in range(0, len(parsed_auth), 5):
        slice_logs = parsed_auth[i:i+5]
        slice_text = "\n".join([f"[{l.timestamp}] {l.raw_message}" for l in slice_logs])
        chunk = DocumentChunk(
            id=f"auth_log_chunk_{i//5}",
            content=slice_text,
            source_file="auth_bruteforce_incident.log",
            chunk_index=i//5,
            metadata={"source": "auth_bruteforce_incident.log", "category": "logs", "lines": f"{i+1}-{i+len(slice_logs)}"}
        )
        vector_store.add_chunks([chunk], category="logs")

    parsed_web = parse_csv_logs(web_csv_content, "web_exploitation_attacks.csv")
    for i, w in enumerate(parsed_web):
        chunk = DocumentChunk(
            id=f"web_log_chunk_{i}",
            content=f"[{w.timestamp}] Method: {w.action} from {w.source_ip} - Status: {w.status}\nPayload: {w.raw_message}",
            source_file="web_exploitation_attacks.csv",
            chunk_index=i,
            metadata={"source": "web_exploitation_attacks.csv", "category": "logs", "line": w.line_number}
        )
        vector_store.add_chunks([chunk], category="logs")

    print("[DataGenerator] Successfully preloaded benchmark incident logs & cybersecurity knowledge base!")
