import pytest
from app.log_parser import LogEntry, parse_syslog_auth
from app.rules_engine import rules_engine


def test_brute_force_detection():
    logs = []
    # 7 failed attempts from 192.0.2.10
    for i in range(7):
        logs.append(LogEntry(
            id=f"test_{i}",
            timestamp="2026-10-20 14:00:00",
            source_ip="192.0.2.10",
            user="admin",
            action="LOGIN_FAILED",
            status="FAILURE",
            raw_message="Failed password for admin from 192.0.2.10"
        ))

    alerts = rules_engine.analyze(logs)
    bf_alerts = [a for a in alerts if a.rule_name == "RULE_BRUTE_FORCE_AUTH"]
    assert len(bf_alerts) == 1
    assert bf_alerts[0].source_ip == "192.0.2.10"
    assert bf_alerts[0].severity in ["HIGH", "CRITICAL"]


def test_privilege_escalation_detection():
    log = LogEntry(
        id="sudo_test",
        timestamp="2026-10-20 14:05:00",
        source_ip="10.0.0.5",
        user="analyst_test",
        action="SUDO_EXEC",
        status="ALERT",
        raw_message="sudo:   analyst_test : TTY=pts/0 ; COMMAND=/bin/bash"
    )
    alerts = rules_engine.analyze([log])
    pe_alerts = [a for a in alerts if a.rule_name == "RULE_PRIVILEGE_ESCALATION"]
    assert len(pe_alerts) == 1
    assert pe_alerts[0].target_user == "analyst_test"
