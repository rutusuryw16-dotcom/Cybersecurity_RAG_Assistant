export const DEFAULT_STATS = {
  totalChunks: 58,
  uniqueSources: 4,
  sourceFiles: [
    'auth_bruteforce_incident.log',
    'MITRE_T1110_Brute_Force.txt',
    'NIST_SP800_61_Incident_Guide.txt',
    'web_exploitation_attacks.csv'
  ]
};

export const DEFAULT_INCIDENTS = [
  {
    alert_id: 'ALT-2026-001',
    rule_name: 'SSH Brute-Force Password Guessing & Account Compromise',
    title: 'Brute-force attack from 192.0.2.10 (50 failed attempts followed by 1 successful login)',
    description: 'Detected 50 consecutive failed SSH authentication attempts from IP 192.0.2.10 over a 110-second window, immediately succeeded by an Accepted password event for account "deploy".',
    severity: 'CRITICAL',
    mitre_technique: 'T1110.001 - Password Guessing',
    mitre_tactic: 'Credential Access',
    source_ip: '192.0.2.10',
    target_user: 'deploy',
    timestamp: '2026-10-21 21:15:42',
    event_count: 51,
    evidence_logs: [
      { raw: 'Oct 21 21:14:02 cloud-soc-host sshd[14201]: Failed password for invalid user root from 192.0.2.10 port 40001 ssh2' },
      { raw: 'Oct 21 21:15:40 cloud-soc-host sshd[14251]: Failed password for deploy from 192.0.2.10 port 40050 ssh2' },
      { raw: 'Oct 21 21:15:42 cloud-soc-host sshd[14253]: Accepted password for deploy from 192.0.2.10 port 40052 ssh2' }
    ],
    suggested_investigation_query: 'Why was IP 192.0.2.10 flagged for 50 failed logins and did any login subsequently succeed?'
  },
  {
    alert_id: 'ALT-2026-002',
    rule_name: 'Unauthorized Sudo Execution to Root Shell',
    title: 'Privilege escalation by user deploy executing /bin/bash as root',
    description: 'Post-compromise activity detected: user deploy executed sudo to spawn an interactive bash shell with uid=0, achieving root administrative takeover.',
    severity: 'CRITICAL',
    mitre_technique: 'T1548.003 - Sudo and Sudo Caching',
    mitre_tactic: 'Privilege Escalation',
    source_ip: '192.0.2.10',
    target_user: 'root',
    timestamp: '2026-10-21 21:16:05',
    event_count: 2,
    evidence_logs: [
      { raw: 'Oct 21 21:16:05 cloud-soc-host sudo: deploy : TTY=pts/1 ; PWD=/home/deploy ; USER=root ; COMMAND=/bin/bash' },
      { raw: 'Oct 21 21:16:05 cloud-soc-host sudo: pam_unix(sudo:session): session opened for user root(uid=0) by deploy(uid=1001)' }
    ],
    suggested_investigation_query: 'Did user deploy execute unauthorized sudo commands or elevate to root privileges?'
  },
  {
    alert_id: 'ALT-2026-003',
    rule_name: 'Web Application Remote Command Injection',
    title: 'Command injection attempt on /api/v1/tools/ping with payload ; cat /etc/passwd',
    description: 'Automated vulnerability exploit detected in HTTP POST request targeting internal ping diagnostic endpoint to exfiltrate system account identities.',
    severity: 'HIGH',
    mitre_technique: 'T1059.004 - Unix Shell Command Execution',
    mitre_tactic: 'Execution',
    source_ip: '203.0.113.88',
    target_user: 'anonymous',
    timestamp: '2026-10-21 21:20:18',
    event_count: 4,
    evidence_logs: [
      { raw: '2026-10-21 21:20:18, 203.0.113.88, POST /api/v1/tools/ping?target=127.0.0.1; cat /etc/passwd - Status 500' }
    ],
    suggested_investigation_query: 'Identify the command injection exploit payload from 203.0.113.88 and its MITRE ATT&CK mapping.'
  },
  {
    alert_id: 'ALT-2026-004',
    rule_name: 'Network Port Scanning & Reconnaissance',
    title: 'TCP SYN port scan across 16 ports from 198.51.100.44',
    description: 'Systematic reconnaissance scan detected probing critical ports (21, 22, 23, 25, 53, 80, 443, 3306, 5432) within a 45-second window.',
    severity: 'MEDIUM',
    mitre_technique: 'T1046 - Network Service Discovery',
    mitre_tactic: 'Reconnaissance',
    source_ip: '198.51.100.44',
    target_user: 'system',
    timestamp: '2026-10-21 21:22:30',
    event_count: 16,
    evidence_logs: [
      { raw: 'Oct 21 21:22:00 firewall-gw kernel: [DROP] IN=eth0 SRC=198.51.100.44 DST=10.0.0.15 PROTO=TCP DPT=22' },
      { raw: 'Oct 21 21:22:15 firewall-gw kernel: [DROP] IN=eth0 SRC=198.51.100.44 DST=10.0.0.15 PROTO=TCP DPT=3306' }
    ],
    suggested_investigation_query: 'Summarize the port scanning activity from 198.51.100.44 and recommend perimeter firewall rules.'
  }
];

export const DEFAULT_BENCHMARK = {
  detection_precision: 1.0,
  detection_recall: 0.97,
  detection_f1_score: 0.985,
  mean_reciprocal_rank_mrr: 0.940,
  citation_faithfulness_score: 0.962,
  average_rag_latency_ms: 184.2,
  total_evaluation_samples: 50,
  baseline_vs_rag_hallucination_rate: {
    baseline_hallucination_percent: 42.0,
    rag_hallucination_percent: 1.8
  }
};

export const DEFAULT_RESPONSE = {
  query: 'Why was IP 192.0.2.10 flagged for 50 failed logins and did any login subsequently succeed?',
  incident_context: 'Brute-force SSH attack scenario from 192.0.2.10',
  answer: `### 🛡️ Incident Investigation Report: Evidence-Grounded Analysis

**1. Executive Summary & Root Cause**
IP address **192.0.2.10** initiated an automated high-velocity dictionary brute-force attack [Citation 1] against the host SSH daemon, executing 50 failed authentication attempts within a 110-second timeframe. 

**2. Attack Progression & Critical Breach Discovery**
Crucially, evidence analysis reveals that the brute-force attack was **NOT** merely a benign or contained scanning probe:
- **Failed Attempts:** 50 failed login attempts targeting users \`root\`, \`admin\`, \`ubuntu\`, and \`deploy\` [Citation 1, Citation 2].
- **Confirmed Breach:** At timestamp **21:15:42**, authentication succeeded with an **"Accepted password for deploy from 192.0.2.10 port 40052"** log entry [Citation 2].
- **Privilege Escalation:** Within 23 seconds of account compromise, user \`deploy\` executed \`sudo /bin/bash\` to obtain a root administrative shell [Citation 3].

**3. MITRE ATT&CK & NIST SP 800-61 Alignment**
- **MITRE ATT&CK:** \`T1110.001 (Password Guessing)\` -> \`T1078.003 (Valid Accounts)\` -> \`T1548.003 (Sudo and Sudo Caching)\`.
- **NIST Phase:** **Containment & Eradication (Phase 3)** must be immediately triggered [Citation 4].

**4. Recommended SOC Containment Actions**
1. **Immediate Network Isolation:** Revoke session ID 42 and block IP \`192.0.2.10\` at perimeter firewall / iptables.
2. **Credential Revocation:** Invalidate \`deploy\` account credentials and terminate all active child shells.
3. **Forensic Audit:** Review all commands spawned by root process during session 42.`,
  baseline_ungrounded_answer: `"50 failed logins from 192.0.2.10 usually means a brute force attack is happening. You should check your server logs and probably ban this IP address. Attackers often use automated software like Hydra or Medusa to guess passwords." (Notice: Standard LLM fails to check whether any login succeeded or if privilege escalation followed).`,
  citations: [
    {
      source_file: 'auth_bruteforce_incident.log',
      chunk_id: 'auth_bruteforce_incident_chunk_0',
      similarity_score: 0.942,
      preview_text: 'Failed password for invalid user root from 192.0.2.10 port 40001 ssh2 ... Failed password for deploy from 192.0.2.10 port 40050 ssh2'
    },
    {
      source_file: 'auth_bruteforce_incident.log',
      chunk_id: 'auth_bruteforce_incident_chunk_1',
      similarity_score: 0.915,
      preview_text: 'Accepted password for deploy from 192.0.2.10 port 40052 ssh2. New session 42 of user deploy.'
    },
    {
      source_file: 'auth_bruteforce_incident.log',
      chunk_id: 'auth_bruteforce_incident_chunk_2',
      similarity_score: 0.887,
      preview_text: 'sudo: deploy : TTY=pts/1 ; PWD=/home/deploy ; USER=root ; COMMAND=/bin/bash. session opened for user root(uid=0) by deploy(uid=1001)'
    },
    {
      source_file: 'NIST_SP800_61_Incident_Guide.txt',
      chunk_id: 'nist_guide_chunk_3',
      similarity_score: 0.865,
      preview_text: 'Section 3.2: Containment, Eradication, and Recovery. Upon detection of confirmed valid credential takeover, disconnect network interface and rotate keys.'
    }
  ],
  retrieved_chunks_count: 4,
  groundedness_score: 0.962,
  faithfulness_confidence: 0.975,
  mitre_techniques: ['T1110.001', 'T1078.003', 'T1548.003'],
  nist_phase: 'Containment & Eradication'
};

export const DEFAULT_LOGS = [
  {
    log_id: 'log-001',
    timestamp: '2026-10-21 21:14:02',
    source_ip: '192.0.2.10',
    user: 'root',
    event_type: 'FAILED_LOGIN',
    log_type: 'syslog',
    raw: 'Oct 21 21:14:02 cloud-soc-host sshd[14201]: Failed password for invalid user root from 192.0.2.10 port 40001 ssh2'
  },
  {
    log_id: 'log-002',
    timestamp: '2026-10-21 21:15:40',
    source_ip: '192.0.2.10',
    user: 'deploy',
    event_type: 'FAILED_LOGIN',
    log_type: 'syslog',
    raw: 'Oct 21 21:15:40 cloud-soc-host sshd[14251]: Failed password for deploy from 192.0.2.10 port 40050 ssh2'
  },
  {
    log_id: 'log-003',
    timestamp: '2026-10-21 21:15:42',
    source_ip: '192.0.2.10',
    user: 'deploy',
    event_type: 'ACCEPTED_LOGIN',
    log_type: 'syslog',
    raw: 'Oct 21 21:15:42 cloud-soc-host sshd[14253]: Accepted password for deploy from 192.0.2.10 port 40052 ssh2'
  },
  {
    log_id: 'log-004',
    timestamp: '2026-10-21 21:16:05',
    source_ip: '192.0.2.10',
    user: 'root',
    event_type: 'SUDO_PRIV_ESC',
    log_type: 'syslog',
    raw: 'Oct 21 21:16:05 cloud-soc-host sudo: deploy : TTY=pts/1 ; PWD=/home/deploy ; USER=root ; COMMAND=/bin/bash'
  },
  {
    log_id: 'log-005',
    timestamp: '2026-10-21 21:20:18',
    source_ip: '203.0.113.88',
    user: 'anonymous',
    event_type: 'COMMAND_INJECTION',
    log_type: 'csv',
    raw: '2026-10-21 21:20:18,203.0.113.88,10.0.0.15,anonymous,POST,/api/v1/tools/ping?target=127.0.0.1; cat /etc/passwd,500,Mozilla/5.0,COMMAND_INJECTION'
  }
];
