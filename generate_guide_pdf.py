import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header on pages 2+
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "Cloud-Based Cybersecurity RAG Assistant • Comprehensive Project Guide")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer on all pages
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(letter[0] - 54, 30, page_str)
        self.drawString(54, 30, "Confidential • Academic & Project Reference • 2026")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 42, letter[0] - 54, 42)
        self.restoreState()


def generate_guide_pdf(filename="Project_Explanation_and_Run_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0f172a") # Slate 900
    cyan_color = colors.HexColor("#0284c7")    # Sky 600
    dark_cyan = colors.HexColor("#0369a1")
    accent_green = colors.HexColor("#16a34a")
    box_bg = colors.HexColor("#f8fafc")
    border_color = colors.HexColor("#e2e8f0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        alignment=0,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=dark_cyan,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=body_style,
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0f172a")
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("Cloud-Based Cybersecurity RAG Assistant", title_style))
    story.append(Paragraph("Complete Project Guide: Concept, Inner Workings, Execution, and Viva Preparation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=dark_cyan, spaceAfter=14))

    # SECTION 1: What is this project in simple words?
    story.append(Paragraph("1. What is this Project in Simple Words?", h1_style))
    p1 = (
        "Modern cloud servers (like AWS, Azure, Google Cloud) run 24/7 and generate hundreds of thousands of "
        "<b>log lines</b> every hour. These logs record every login attempt, web request, sudo command, and network connection. "
        "When an attacker launches a cyber attack, existing monitoring software (SIEM) fires an alert, such as: "
        "<i>'50 failed logins detected from IP 192.0.2.10'</i>."
    )
    story.append(Paragraph(p1, body_style))

    p2 = (
        "However, existing systems <b>cannot explain what actually happened next</b>: Did the attacker eventually break in? "
        "Which user account was cracked? Did they become root? What specific steps should the security team take to isolate the server? "
        "Normally, a human security analyst has to manually dig through thousands of raw log files, which takes 30 to 60 minutes per incident."
    )
    story.append(Paragraph(p2, body_style))

    p3 = (
        "<b>The Problem with Normal AI (like basic ChatGPT):</b> If you paste a generic question into standard AI, "
        "it suffers from <i>hallucinations</i>—it invents fictional IP addresses, guesses wrong answers, and has no access to your "
        "actual server log evidence."
    )
    story.append(Paragraph(p3, body_style))

    # Callout Box: What this project does
    callout_data = [[
        Paragraph(
            "<b>🎯 The Solution (This Project):</b> A <b>Retrieval-Augmented Generation (RAG)</b> Assistant designed for Security Operations Centers (SOC). "
            "It searches your actual system logs and official cybersecurity playbooks (MITRE ATT&CK & NIST SP 800-61), extracts verifiable evidence, "
            "and generates an accurate, hallucination-free incident report with <b>exact line citations in under 2 seconds</b>.",
            callout_style
        )
    ]]
    callout_table = Table(callout_data, colWidths=[letter[0] - 108])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0f9ff")),
        ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor("#bae6fd")),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 12))

    # SECTION 2: How It Works (The 5-Stage Pipeline)
    story.append(Paragraph("2. How Does It Work? (System Architecture & Pipeline)", h1_style))
    story.append(Paragraph("The system operates through five synchronized stages:", body_style))

    stages_data = [
        ["Stage", "Module Name", "What It Does in Simple English"],
        ["1", "Log Ingestion & Privacy Masking", "Reads server logs (syslog, web CSVs). Uses regex patterns to automatically scrub private passwords and sensitive PII so data privacy is guaranteed."],
        ["2", "Rules Correlation Engine", "Scans logs at microsecond speed for known attack signatures: Brute Force (50+ fails in 120s), Sudo Root Escalation, Command Injection, and Port Reconnaissance."],
        ["3", "Hybrid Vector Store (ChromaDB / TF-IDF)", "Stores log chunks using two search methods: Dense semantic search (understanding meaning) + Sparse lexical BM25 search (matching exact IP addresses like 192.0.2.10 and ports)."],
        ["4", "RAG Reasoning & Citation Engine", "When an analyst asks a question, it retrieves the Top-5 most relevant log chunks, feeds them into the LLM, and verifies that every claim cites an exact timestamp."],
        ["5", "Cloud SOC Dashboard (React + Vite)", "A high-performance modern web interface showing live radar alerts, an interactive investigation chat terminal, side-by-side hallucination comparisons, and evaluation charts."]
    ]
    t_stages = Table(stages_data, colWidths=[40, 160, letter[0] - 108 - 200])
    t_stages.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('LEADING', (0, 0), (-1, -1), 11.5),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('BACKGROUND', (0, 1), (-1, -1), box_bg),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), box_bg]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_stages)
    story.append(Spacer(1, 14))

    # SECTION 3: The Benchmark Scenario: 50 Failed Logins
    story.append(Paragraph("3. The Core Benchmark Scenario: The 50-Failed-Logins Attack", h1_style))
    story.append(Paragraph(
        "This project features a real-world multi-stage attack scenario designed to demonstrate why RAG is superior to normal AI:",
        body_style
    ))

    scenario_points = [
        "<b>Phase 1 (Recon & Brute Force):</b> Attacker IP <code>192.0.2.10</code> attempts 50 rapid logins in 110 seconds against users (<code>root</code>, <code>admin</code>, <code>ubuntu</code>, and <code>deploy</code>).",
        "<b>Phase 2 (The Critical Breach):</b> At timestamp <code>21:15:42</code>, the log records <code>Accepted password for deploy from 192.0.2.10</code>. The attacker successfully guessed the password!",
        "<b>Phase 3 (Root Privilege Escalation):</b> 23 seconds later, the attacker executes <code>sudo /bin/bash</code>, spawning a root shell with <code>uid=0</code>.",
        "<b>The Comparison:</b> A generic LLM only sees '50 failed logins' and tells you to block the IP. It <b>misses the fact that the attacker already broke in and became root</b>! Our RAG Assistant catches the accepted login, warns of the root takeover, cites the exact lines, and triggers NIST Phase 3 Containment."
    ]
    for pt in scenario_points:
        story.append(Paragraph(f"• {pt}", body_style))

    story.append(Spacer(1, 12))

    # SECTION 4: How to Run the Project
    story.append(Paragraph("4. How to Run the Project Locally", h1_style))
    story.append(Paragraph("You can run the project using any of the following methods:", body_style))

    story.append(Paragraph("Method A: One-Click Windows Launcher (Easiest)", h2_style))
    story.append(Paragraph(
        "Double-click <code>run_demo.bat</code> in the project root folder. "
        "It automatically verifies Python and Node.js, starts the FastAPI backend on port 8000, "
        "starts the React frontend on port 5173, and opens your browser automatically.",
        body_style
    ))

    story.append(Paragraph("Method B: Manual Terminal Execution", h2_style))
    cmds = (
        "<b>Terminal 1 (Backend Server):</b><br/>"
        "<code>cd backend</code><br/>"
        "<code>python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload</code><br/><br/>"
        "<b>Terminal 2 (Frontend Interface):</b><br/>"
        "<code>cd frontend</code><br/>"
        "<code>npm run dev</code><br/>"
        "Open <code>http://localhost:5173</code> in your web browser."
    )
    cmd_table = Table([[Paragraph(cmds, code_style)]], colWidths=[letter[0] - 108])
    cmd_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(cmd_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Method C: Docker & Kubernetes (Production Cloud Native)", h2_style))
    story.append(Paragraph(
        "Run <code>docker-compose up --build</code> to launch both microservices in isolated OCI containers. "
        "For Kubernetes clusters, run <code>kubectl apply -f k8s/</code> to deploy 2-replica auto-healing pods.",
        body_style
    ))

    story.append(Paragraph("Method D: Live Cloud Deployment", h2_style))
    story.append(Paragraph(
        "The project is publicly deployed and accessible 24/7 on GitHub Pages at:<br/>"
        "<b><font color='#0284c7'>https://rutusuryw16-dotcom.github.io/Cybersecurity_RAG_Assistant/</font></b>",
        body_style
    ))

    story.append(Spacer(1, 12))

    # SECTION 5: Viva / Exam Questions & Answers
    story.append(Paragraph("5. Top Viva / Interview Questions & Easy Answers", h1_style))

    qa_list = [
        ("Q1: Why use RAG instead of fine-tuning an LLM?",
         "Fine-tuning modifies model weights, which is expensive, slow, and cannot handle dynamic, real-time log updates. "
         "RAG keeps the model unchanged and feeds it real-time log evidence at query time. This completely stops hallucinations and provides auditable source citations."),

        ("Q2: What is the difference between Dense and Sparse retrieval in your Vector DB?",
         "Dense search uses deep learning embeddings (SentenceTransformers) to understand conceptual meaning (e.g., 'unauthorized access' matches 'password breach'). "
         "Sparse search (BM25 / TF-IDF) matches exact tokens like IP addresses ('192.0.2.10'), port numbers ('22'), and usernames ('deploy'). "
         "Combining both gives the highest retrieval accuracy (MRR: 0.940)."),

        ("Q3: How does the system protect sensitive data before vector storage?",
         "The Log Parser contains an automated PII/Credential Masking engine. Before logs are chunked or embedded, regex filters redact cleartext passwords, "
         "session tokens, and secret keys (replacing them with [REDACTED_PASSWORD]), conforming to GDPR and NIST privacy standards."),

        ("Q4: What is Citation Faithfulness Score (CFS)?",
         "CFS measures the percentage of factual statements made by the LLM that are directly supported by the retrieved log chunks. "
         "Our evaluation benchmark achieves 96.2% faithfulness, compared to un-grounded LLMs which hallucinate over 42% of the time."),

        ("Q5: What cloud computing syllabus units does this project cover?",
         "It covers Unit 1 (IaaS/PaaS decoupled architecture), Unit 2 (Docker virtualization), Unit 3 (Kubernetes microservices), "
         "Unit 4 (CI/CD GitHub Actions automated testing), Unit 5 (Cloud Security & JWT RBAC), and Unit 6 (GenAI & AIOps in Cloud).")
    ]

    for q, a in qa_list:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(a, body_style))
        story.append(Spacer(1, 4))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    generate_guide_pdf()
