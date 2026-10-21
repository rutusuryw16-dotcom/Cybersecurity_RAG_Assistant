import re
import csv
import json
import uuid
from datetime import datetime
from io import StringIO
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import pypdf


class LogEntry(BaseModel):
    id: str
    timestamp: str
    source_ip: str = "N/A"
    dest_ip: str = "N/A"
    user: str = "N/A"
    action: str = "UNKNOWN"
    status: str = "INFO"
    raw_message: str
    source_file: str = "unknown"
    line_number: int = 1
    severity: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL


class DocumentChunk(BaseModel):
    id: str
    content: str
    source_file: str
    chunk_index: int
    metadata: Dict[str, Any] = {}


# Regex patterns for parsing and redaction
IP_REGEX = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
TIMESTAMP_REGEX = re.compile(
    r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)|'
    r'([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'
)
PASSWORD_REDACT_REGEX = re.compile(
    r'(?i)(password|passwd|pwd|secret|api[_-]?key|auth(?:orization)?|token)[\s:=]+([^\s,;&"\']+)',
    re.IGNORECASE
)


def redact_sensitive_data(text: str) -> str:
    """Masks sensitive credentials in logs to maintain data privacy compliance."""
    return PASSWORD_REDACT_REGEX.sub(r'\1=***REDACTED***', text)


def extract_ip(text: str) -> str:
    match = IP_REGEX.search(text)
    return match.group(0) if match else "N/A"


def extract_timestamp(text: str) -> str:
    match = TIMESTAMP_REGEX.search(text)
    if match:
        return match.group(0)
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def parse_csv_logs(content: str, filename: str) -> List[LogEntry]:
    entries: List[LogEntry] = []
    f = StringIO(content)
    reader = csv.DictReader(f)
    
    # Normalize headers
    for i, row in enumerate(reader, start=2):
        row_lower = {k.lower().strip() if k else "": v for k, v in row.items()}
        
        raw_msg = " | ".join([f"{k}: {v}" for k, v in row.items() if v])
        raw_msg = redact_sensitive_data(raw_msg)
        
        timestamp = (
            row_lower.get("timestamp") or 
            row_lower.get("time") or 
            row_lower.get("date") or 
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        )
        source_ip = (
            row_lower.get("source_ip") or 
            row_lower.get("src_ip") or 
            row_lower.get("ip") or 
            extract_ip(raw_msg)
        )
        dest_ip = (
            row_lower.get("dest_ip") or 
            row_lower.get("dst_ip") or 
            row_lower.get("destination_ip") or 
            "N/A"
        )
        user = (
            row_lower.get("user") or 
            row_lower.get("username") or 
            row_lower.get("account") or 
            "N/A"
        )
        action = (
            row_lower.get("action") or 
            row_lower.get("event") or 
            row_lower.get("event_type") or 
            "LOG_EVENT"
        )
        status = (
            row_lower.get("status") or 
            row_lower.get("result") or 
            "INFO"
        ).upper()

        entries.append(LogEntry(
            id=f"{filename}_{i}_{uuid.uuid4().hex[:6]}",
            timestamp=timestamp,
            source_ip=source_ip,
            dest_ip=dest_ip,
            user=user,
            action=action.upper(),
            status=status,
            raw_message=raw_msg,
            source_file=filename,
            line_number=i,
            severity="LOW"
        ))
    return entries


def parse_syslog_auth(content: str, filename: str) -> List[LogEntry]:
    entries: List[LogEntry] = []
    lines = content.strip().splitlines()
    
    for i, line in enumerate(lines, start=1):
        clean_line = redact_sensitive_data(line.strip())
        if not clean_line:
            continue
            
        timestamp = extract_timestamp(clean_line)
        ip = extract_ip(clean_line)
        
        # Determine user and action heuristically
        user = "N/A"
        user_match = re.search(r'for (?:invalid user )?([a-zA-Z0-9_\-\.]+)', clean_line)
        if user_match:
            user = user_match.group(1)
        elif "sudo:" in clean_line:
            sudo_user = re.search(r'sudo:\s+([a-zA-Z0-9_\-\.]+)', clean_line)
            if sudo_user:
                user = sudo_user.group(1)

        action = "SYSTEM_EVENT"
        status = "INFO"
        severity = "LOW"

        if "Failed password" in clean_line or "authentication failure" in clean_line:
            action = "LOGIN_FAILED"
            status = "FAILURE"
            severity = "MEDIUM"
        elif "Accepted password" in clean_line or "session opened" in clean_line:
            action = "LOGIN_SUCCESS"
            status = "SUCCESS"
            severity = "LOW"
        elif "COMMAND=" in clean_line or "sudo" in clean_line:
            action = "SUDO_EXEC"
            status = "ALERT"
            severity = "HIGH"
        elif "scan" in clean_line.lower() or "connection refused" in clean_line.lower():
            action = "PORT_SCAN"
            status = "BLOCKED"
            severity = "MEDIUM"
        elif "injection" in clean_line.lower() or "cmd.exe" in clean_line.lower() or "/bin/sh" in clean_line.lower():
            action = "COMMAND_INJECTION"
            status = "ALERT"
            severity = "CRITICAL"

        entries.append(LogEntry(
            id=f"{filename}_{i}_{uuid.uuid4().hex[:6]}",
            timestamp=timestamp,
            source_ip=ip,
            dest_ip="N/A",
            user=user,
            action=action,
            status=status,
            raw_message=clean_line,
            source_file=filename,
            line_number=i,
            severity=severity
        ))
    return entries


def parse_json_logs(content: str, filename: str) -> List[LogEntry]:
    entries: List[LogEntry] = []
    lines = content.strip().splitlines()
    
    # Try parsing whole JSON array first
    try:
        data = json.loads(content)
        if isinstance(data, list):
            for i, item in enumerate(data, start=1):
                raw = redact_sensitive_data(json.dumps(item))
                entries.append(LogEntry(
                    id=f"{filename}_{i}_{uuid.uuid4().hex[:6]}",
                    timestamp=item.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
                    source_ip=item.get("source_ip", item.get("src_ip", extract_ip(raw))),
                    dest_ip=item.get("dest_ip", item.get("dst_ip", "N/A")),
                    user=item.get("user", item.get("username", "N/A")),
                    action=str(item.get("action", item.get("event", "JSON_EVENT"))).upper(),
                    status=str(item.get("status", "INFO")).upper(),
                    raw_message=raw,
                    source_file=filename,
                    line_number=i,
                    severity=item.get("severity", "LOW")
                ))
            return entries
    except Exception:
        pass

    # Fallback to line-delimited JSON (NDJSON)
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            raw = redact_sensitive_data(line)
            entries.append(LogEntry(
                id=f"{filename}_{i}_{uuid.uuid4().hex[:6]}",
                timestamp=item.get("timestamp", extract_timestamp(raw)),
                source_ip=item.get("source_ip", item.get("src_ip", extract_ip(raw))),
                dest_ip=item.get("dest_ip", "N/A"),
                user=item.get("user", item.get("username", "N/A")),
                action=str(item.get("action", item.get("event", "JSON_EVENT"))).upper(),
                status=str(item.get("status", "INFO")).upper(),
                raw_message=raw,
                source_file=filename,
                line_number=i,
                severity=item.get("severity", "LOW")
            ))
        except Exception:
            continue
            
    return entries


def parse_pdf(file_bytes: bytes, filename: str) -> str:
    """Extracts text content from a PDF report."""
    reader = pypdf.PdfReader(StringIO(file_bytes.decode("latin1", errors="ignore")))
    text_content = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_content.append(page_text)
    return "\n\n".join(text_content)


def chunk_text(
    text: str, 
    source_file: str, 
    chunk_size: int = 500, 
    overlap: int = 100, 
    extra_meta: Optional[Dict[str, Any]] = None
) -> List[DocumentChunk]:
    """Chunks documents into overlapping segments for dense vector retrieval."""
    chunks: List[DocumentChunk] = []
    paragraphs = text.split("\n\n")
    current_chunk = ""
    chunk_idx = 0
    
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
            
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += ("\n\n" if current_chunk else "") + p
        else:
            if current_chunk:
                chunks.append(DocumentChunk(
                    id=f"{source_file}_chunk_{chunk_idx}_{uuid.uuid4().hex[:6]}",
                    content=current_chunk,
                    source_file=source_file,
                    chunk_index=chunk_idx,
                    metadata={**(extra_meta or {}), "source": source_file, "chunk": chunk_idx}
                ))
                chunk_idx += 1
                # Retain overlap from end of current_chunk
                current_chunk = current_chunk[-overlap:] + "\n\n" + p if overlap > 0 else p
            else:
                current_chunk = p
                
    if current_chunk.strip():
        chunks.append(DocumentChunk(
            id=f"{source_file}_chunk_{chunk_idx}_{uuid.uuid4().hex[:6]}",
            content=current_chunk.strip(),
            source_file=source_file,
            chunk_index=chunk_idx,
            metadata={**(extra_meta or {}), "source": source_file, "chunk": chunk_idx}
        ))
        
    return chunks
