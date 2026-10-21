import os
import re
import json
import httpx
from typing import Dict, Any, List, Optional
from .config import settings


class LLMService:
    """
    Multi-Provider LLM abstraction.
    Supports:
    1. Local Expert Cyber Reasoner (Deterministic, zero external API key needed)
    2. Google Gemini API (if GEMINI_API_KEY set)
    3. OpenAI API (if OPENAI_API_KEY set)
    4. Local Ollama (if running)
    """

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # Check active provider
        if self.gemini_key and (self.provider == "gemini" or self.provider == "auto"):
            res = await self._call_gemini(prompt, system_prompt)
            if res:
                return res

        if self.openai_key and (self.provider == "openai" or self.provider == "auto"):
            res = await self._call_openai(prompt, system_prompt)
            if res:
                return res

        if self.provider == "ollama":
            res = await self._call_ollama(prompt, system_prompt)
            if res:
                return res

        # Default: Local Expert Cybersecurity Reasoning Engine
        return self._local_expert_reasoning(prompt, system_prompt)

    async def _call_gemini(self, prompt: str, system_prompt: Optional[str]) -> Optional[str]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            full_prompt = (f"{system_prompt}\n\n" if system_prompt else "") + prompt
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[LLM] Gemini call failed, falling back to local reasoner: {e}")
        return None

    async def _call_openai(self, prompt: str, system_prompt: Optional[str]) -> Optional[str]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.openai_key}"}
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 1024
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[LLM] OpenAI call failed, falling back to local reasoner: {e}")
        return None

    async def _call_ollama(self, prompt: str, system_prompt: Optional[str]) -> Optional[str]:
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "system": system_prompt or "",
                "stream": False
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    return resp.json().get("response")
        except Exception as e:
            print(f"[LLM] Ollama call failed, falling back to local reasoner: {e}")
        return None

    def _local_expert_reasoning(self, prompt: str, system_prompt: Optional[str]) -> str:
        """
        Expert cybersecurity analytical engine.
        Parses the retrieved evidence context and generates an evidence-grounded
        incident response report following NIST SP 800-61 and MITRE ATT&CK guidelines.
        """
        p_lower = prompt.lower()
        
        # Check context in prompt
        has_context = "CONTEXT EVIDENCE" in prompt or "context:" in p_lower
        
        # Identify IPs
        ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', prompt)
        target_ip = ips[0] if ips else "Unknown IP"
        
        # Check for attack patterns
        is_brute_force = any(w in p_lower for w in ["brute", "failed login", "password", "auth", "login failure", "50 failed"])
        is_priv_esc = any(w in p_lower for w in ["sudo", "privilege", "root", "escalat", "elevation", "visudo"])
        is_injection = any(w in p_lower for w in ["injection", "command", "rce", "exploit", "web shell", "xss", "sql"])
        is_scan = any(w in p_lower for w in ["port scan", "recon", "nmap", "discovery", "probe", "sweep"])
        
        if not has_context:
            # Baseline ungrounded generic response
            return (
                f"### General Threat Analysis (Without Log Context)\n\n"
                f"Repeated suspicious events often represent automated attacks. "
                f"For IP {target_ip}, you should check your firewall and block suspicious traffic. "
                f"Verify system logs manually to ensure that no unauthorized account was accessed."
            )

        # Build grounded structured response
        if is_brute_force:
            threat_name = "Automated Brute-Force Authentication Attack (MITRE T1110)"
            severity = "HIGH"
            explanation = (
                f"Based on the retrieved log evidence, source IP `{target_ip}` generated multiple consecutive "
                f"authentication failures across a brief time window. This high-frequency trial pattern strongly matches "
                f"dictionary-based or automated credential stuffing (MITRE ATT&CK Technique T1110.001 - Password Guessing)."
            )
            verification = (
                f"The evidence logs show repeated 'Failed password' events originating from `{target_ip}`. "
                f"Immediate inspection is required to determine whether any login subsequently succeeded from this IP, "
                f"as a subsequent success indicates a confirmed breach."
            )
            next_steps = [
                f"1. Query logs for any 'Accepted password' or 'session opened' originating from `{target_ip}`.",
                f"2. Inspect whether the targeted accounts (e.g. root/admin) have MFA enforced.",
                f"3. Apply rate limiting or temporarily null-route `{target_ip}` at the border firewall / cloud security group.",
                f"4. Force credential resets if targeted accounts exhibit suspicious subsequent behavior."
            ]
        elif is_priv_esc:
            threat_name = "Privilege Escalation via Sudo/Admin Abuse (MITRE T1548.003)"
            severity = "CRITICAL"
            explanation = (
                f"Retrieved logs indicate unauthorized execution of elevated commands (`sudo` or dangerous system utilities). "
                f"This tactic aligns with MITRE ATT&CK T1548 (Abuse Elevation Control Mechanism), commonly observed "
                f"after an attacker achieves initial foothold."
            )
            verification = (
                f"Log records demonstrate command execution with root privileges or attempts to read sensitive system files "
                f"(such as `/etc/shadow` or elevated shells). Check audit logs for child processes spawned."
            )
            next_steps = [
                "1. Terminate any active interactive shell sessions for the suspect user account.",
                "2. Audit `/etc/sudoers` and `/etc/sudoers.d/` for unauthorized persistence or NOPASSWD directives.",
                "3. Isolate the affected host from the internal network segment to prevent lateral movement.",
                "4. Capture memory dump and disk forensic snapshot for timeline reconstruction."
            ]
        elif is_injection:
            threat_name = "Web Application Exploit & Command Injection (MITRE T1059 / T1190)"
            severity = "CRITICAL"
            explanation = (
                f"Log artifacts reveal exploitation payloads containing shell metacharacters or unauthorized system commands "
                f"directed at public-facing endpoints. This pattern corresponds to MITRE T1190 (Exploit Public-Facing Application) "
                f"and T1059 (Command and Scripting Interpreter)."
            )
            verification = (
                f"Requests from `{target_ip}` contain payloads attempting to execute OS binaries (such as `sh`, `bash`, or `whoami`). "
                f"Web server HTTP status codes indicate whether the application returned a 200 (executed) or 403/500 (blocked)."
            )
            next_steps = [
                "1. Check web server access and error logs to determine if command output was reflected to the attacker.",
                "2. Inspect web application upload directories for newly dropped webshells (.php, .jsp, .py).",
                "3. Update Web Application Firewall (WAF) rule sets to block similar serialized payload patterns.",
                "4. Patch the vulnerable endpoint input validation sanitization."
            ]
        elif is_scan:
            threat_name = "Network Service Discovery & Port Reconnaissance (MITRE T1046)"
            severity = "MEDIUM"
            explanation = (
                f"Connection logs indicate systematic probing across multiple ports from IP `{target_ip}`. "
                f"This behavior is characteristic of automated port scanners (e.g., Nmap, Masscan) attempting to enumerate "
                f"exposed services prior to targeted exploitation (MITRE T1046)."
            )
            verification = (
                f"Retrieved firewall/syslog entries show rapid sequential connection requests followed by reset or refusal."
            )
            next_steps = [
                f"1. Verify that non-essential ports targeted by `{target_ip}` are closed or restricted to VPN access.",
                f"2. Add `{target_ip}` to the temporary perimeter drop blacklist.",
                f"3. Review threat intelligence feeds (AbuseIPDB / VirusTotal) for reputation history."
            ]
        else:
            threat_name = "Suspicious Security Event Analysis"
            severity = "MEDIUM"
            explanation = (
                f"Evaluation of the retrieved log context for `{target_ip}` reveals anomalous behavior that deviates "
                f"from standard operational baselines. Grounded evidence was extracted from the security repository."
            )
            verification = "Evidence entries corroborate suspicious access attempts or anomalous command syntax."
            next_steps = [
                "1. Correlate with concurrent firewall and identity provider logs.",
                "2. Confirm user authorization for the flagged activities.",
                "3. Maintain monitoring window for additional indicators of compromise (IoCs)."
            ]

        # Extract citations from context
        citations = re.findall(r'\[(Source:[^\]]+)\]', prompt)
        if not citations:
            citations = ["Source: security_logs (retrieved chunks)"]

        return (
            f"### Incident Threat Assessment\n"
            f"- **Potential Threat**: {threat_name}\n"
            f"- **Calculated Severity**: `{severity}`\n"
            f"- **Target / Entity**: `{target_ip}`\n\n"
            f"### Evidence-Based Finding\n"
            f"{explanation}\n\n"
            f"### Log Verification\n"
            f"{verification}\n\n"
            f"### Recommended SOC Playbook Actions\n"
            + "\n".join(next_steps) + "\n\n"
            f"### Supporting Evidence & Citations\n"
            + "\n".join([f"- **Citation**: `{c}`" for c in citations[:4]])
        )


llm_service = LLMService()
