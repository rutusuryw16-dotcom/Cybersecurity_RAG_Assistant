import React, { useState } from 'react';
import { Cloud, Server, Box, GitBranch, Lock, Cpu, Check, Terminal, ExternalLink } from 'lucide-react';

export default function CloudArchitecture() {
  const [activeTab, setActiveTab] = useState('syllabus');

  const syllabusUnits = [
    {
      unit: "Unit 1: Cloud Computing Architecture",
      topics: "NIST Cloud Model, Service Models (IaaS, PaaS, SaaS), Deployment Models (Public, Private, Hybrid)",
      demonstrated: "Cloud-hosted RESTful API architecture decoupling frontend client, backend inference server, and vector database persistence."
    },
    {
      unit: "Unit 2: Virtualization & Isolation",
      topics: "Container vs. Hypervisor Virtualization, Resource namespaces, cgroups, Storage isolation",
      demonstrated: "OCI-compliant Docker container isolation separating FastAPI runtime from persistent volume mounts (/data/vector_db)."
    },
    {
      unit: "Unit 3: Cloud-Native Technologies",
      topics: "Docker Containerization, Microservices, Kubernetes Architecture, Ingress Controllers",
      demonstrated: "Multi-container Docker Compose and production Kubernetes manifests with Deployments, ClusterIP Services, ConfigMaps, and Readiness/Liveness probes."
    },
    {
      unit: "Unit 4: Cloud Deployment & CI/CD",
      topics: "Infrastructure as Code (Terraform), Automated Build & Test Pipelines, Cloud Hosting",
      demonstrated: "GitHub Actions automated CI/CD pipeline running Pytest automated test suites, Docker image packaging, and security vulnerability scanning."
    },
    {
      unit: "Unit 5: Cloud Security & Governance",
      topics: "Identity & Access Management (IAM), Role-Based Access Control (RBAC), Data Privacy, Encryption",
      demonstrated: "OAuth2 with JWT authentication, granular Analyst vs. Admin role permissions, and regex-driven PII credential redaction in ingested logs."
    },
    {
      unit: "Unit 6: Intelligent Cloud & AIOps",
      topics: "Generative AI in Cloud Operations, Vector Retrieval, Predictive Threat Intelligence",
      demonstrated: "Dense semantic vector retrieval combined with rule-based heuristics to provide automated root-cause analysis and threat containment playbooks."
    }
  ];

  const k8sCode = `apiVersion: apps/v1
kind: Deployment
metadata:
  name: cyber-rag-backend
  labels:
    app: cyber-soc-assistant
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cyber-rag-backend
  template:
    metadata:
      labels:
        app: cyber-rag-backend
    spec:
      containers:
      - name: backend
        image: cybersoc/rag-assistant:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: cyber-rag-config
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
          requests:
            cpu: "500m"
            memory: "1Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: cyber-rag-service
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
  selector:
    app: cyber-rag-backend`;

  const cicdCode = `name: CyberSoc RAG CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-and-lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt
    - name: Run Pytest Test Suite
      run: |
        python -m pytest backend/tests -v

  docker-build:
    needs: test-and-lint
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build Docker Container Image
      run: |
        docker build -t cybersoc-rag-assistant:latest ./backend
    - name: Run Trivy Security Vulnerability Scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'cybersoc-rag-assistant:latest'
        format: 'table'
        exit-code: '0'
        severity: 'CRITICAL,HIGH'`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <Cloud style={{ width: '22px', height: '22px', color: 'var(--cyan)' }} />
          <h2 style={{ fontSize: '1.25rem', color: '#fff' }}>Cloud Architecture & Academic Syllabus Mapping</h2>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          Demonstrates how the project comprehensively satisfies all 6 Units of the 3rd-Year CSE Cloud Computing Curriculum.
        </p>

        {/* Sub-Tabs */}
        <div style={{ display: 'flex', gap: '10px', marginTop: '16px', borderTop: '1px solid var(--border-dim)', paddingTop: '14px' }}>
          {[
            { id: 'syllabus', label: 'Curriculum Syllabus Mapping (Units 1-6)' },
            { id: 'k8s', label: 'Kubernetes Manifests (k8s/)' },
            { id: 'cicd', label: 'CI/CD Pipeline (.github/workflows)' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                backgroundColor: activeTab === tab.id ? 'var(--cyan)' : 'transparent',
                color: activeTab === tab.id ? '#000' : 'var(--text-muted)',
                border: '1px solid var(--border-dim)',
                padding: '6px 14px',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: '700',
                cursor: 'pointer'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab: Syllabus Mapping */}
      {activeTab === 'syllabus' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '16px' }}>
          {syllabusUnits.map((u, i) => (
            <div key={i} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                  <span style={{ backgroundColor: 'rgba(0,240,255,0.15)', color: 'var(--cyan)', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: '800' }}>
                    UNIT {i + 1}
                  </span>
                  <h4 style={{ fontSize: '1rem', color: '#fff' }}>{u.unit.split(':')[1]}</h4>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Syllabus Concepts:</span>
                  <p style={{ fontSize: '0.82rem', color: '#cbd5e1', marginTop: '2px' }}>{u.topics}</p>
                </div>
              </div>

              <div style={{ backgroundColor: 'var(--bg-input)', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-dim)' }}>
                <span style={{ fontSize: '11px', color: 'var(--green)', fontWeight: '700' }}>✓ Implemented in Project:</span>
                <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '4px', lineHeight: '1.4' }}>
                  {u.demonstrated}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab: K8s Manifests */}
      {activeTab === 'k8s' && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ color: '#fff', fontSize: '1rem' }}>Production Kubernetes Orchestration (`k8s/deployment.yaml`)</h3>
            <span className="badge-medium" style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '4px' }}>
              Cloud-Native / Ready
            </span>
          </div>
          <pre style={{ backgroundColor: '#050914', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-dim)', color: '#a5f3fc', fontSize: '12px', fontFamily: 'var(--font-mono)', overflowX: 'auto', lineHeight: '1.5' }}>
            {k8sCode}
          </pre>
        </div>
      )}

      {/* Tab: CI/CD Pipeline */}
      {activeTab === 'cicd' && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ color: '#fff', fontSize: '1rem' }}>GitHub Actions CI/CD Pipeline (`.github/workflows/ci-cd.yml`)</h3>
            <span className="badge-low" style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '4px' }}>
              Automated Testing & Scanning
            </span>
          </div>
          <pre style={{ backgroundColor: '#050914', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-dim)', color: '#86efac', fontSize: '12px', fontFamily: 'var(--font-mono)', overflowX: 'auto', lineHeight: '1.5' }}>
            {cicdCode}
          </pre>
        </div>
      )}
    </div>
  );
}
