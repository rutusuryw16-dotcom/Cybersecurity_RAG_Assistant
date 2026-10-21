import React from 'react';
import { Layers, AlertTriangle, CheckCircle, Shield, FileText, ArrowRight } from 'lucide-react';

export default function GroundingCompare({ response }) {
  const defaultQuery = "Why was 192.0.2.10 flagged, and is it a brute-force attack?";

  const comparisonRows = [
    {
      feature: "Evidence Grounding",
      normal: "Generic knowledge base without actual log inspection",
      rag: "Directly linked to exact auth.log entries with line numbers and timestamps"
    },
    {
      feature: "Account Verification",
      normal: "Guesses or assumes generic scenarios without verifying login outcome",
      rag: "Verifies whether 50 failures were followed by an 'Accepted password' breach"
    },
    {
      feature: "MITRE ATT&CK Mapping",
      normal: "Broad classification or generic mentions",
      rag: "Pinpoints Technique T1110.001 (Password Guessing) and T1548.003 (Sudo abuse)"
    },
    {
      feature: "Hallucination Risk",
      normal: "High — may invent hypothetical attacker intent or non-existent IPs",
      rag: "Near-zero — strictly bounded by retrieved vector embeddings and citations"
    },
    {
      feature: "SOC Auditability",
      normal: "Unverifiable output; cannot be cited in legal or compliance audits",
      rag: "Fully auditable evidence chain conforming to NIST SP 800-61 Rev 2"
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Overview Card */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <Layers style={{ width: '20px', height: '20px', color: 'var(--cyan)' }} />
          <h2 style={{ fontSize: '1.25rem', color: '#fff' }}>Side-by-Side Grounding & Hallucination Analysis</h2>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', lineHeight: '1.5' }}>
          This module empirically demonstrates the difference between an un-grounded LLM and a <strong>Retrieval-Augmented Generation (RAG)</strong> cybersecurity assistant.
          Notice how the RAG assistant ties every conclusion to exact log timestamps and citations.
        </p>
      </div>

      {/* Side-by-Side Columns */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
        {/* Left: Normal LLM (Ungrounded) */}
        <div
          className="glass-panel"
          style={{
            padding: '24px',
            borderColor: 'rgba(255, 51, 102, 0.3)',
            backgroundColor: 'rgba(25, 12, 22, 0.6)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertTriangle style={{ width: '18px', height: '18px', color: 'var(--red)' }} />
              <h3 style={{ fontSize: '1.05rem', color: '#fff' }}>Standard LLM (Un-Grounded)</h3>
            </div>
            <span className="badge-critical" style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '4px' }}>
              Hallucination Prone
            </span>
          </div>

          <div
            style={{
              backgroundColor: '#12080f',
              padding: '16px',
              borderRadius: '8px',
              border: '1px solid rgba(255,51,102,0.2)',
              fontSize: '0.88rem',
              color: '#f87171',
              lineHeight: '1.6',
              minHeight: '260px'
            }}
          >
            {response?.baseline_ungrounded_answer ? (
              <p style={{ color: '#cbd5e1' }}>{response.baseline_ungrounded_answer}</p>
            ) : (
              <div>
                <p style={{ marginBottom: '12px' }}>
                  "50 failed logins from 192.0.2.10 usually means a brute force attack is happening.
                  You should check your server logs and probably ban this IP address.
                  Attackers often use automated software like Hydra or Medusa to guess passwords."
                </p>
                <div style={{ borderTop: '1px dashed rgba(255,51,102,0.3)', paddingTop: '10px', marginTop: '12px', fontSize: '11px', color: '#f87171' }}>
                  ⚠️ <strong>Missing Context:</strong> Does not cite any specific timestamp. Cannot tell if the user account was actually compromised or if sudo commands followed.
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right: RAG Cybersecurity Assistant (Evidence-Grounded) */}
        <div
          className="glass-panel"
          style={{
            padding: '24px',
            borderColor: 'rgba(0, 240, 255, 0.4)',
            backgroundColor: 'rgba(8, 22, 38, 0.6)',
            boxShadow: '0 0 24px rgba(0,240,255,0.1)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Shield style={{ width: '18px', height: '18px', color: 'var(--cyan)' }} />
              <h3 style={{ fontSize: '1.05rem', color: '#fff' }}>Cloud RAG Assistant (Evidence-Grounded)</h3>
            </div>
            <span className="badge-low" style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '4px' }}>
              Auditable & Verified
            </span>
          </div>

          <div
            style={{
              backgroundColor: '#071224',
              padding: '16px',
              borderRadius: '8px',
              border: '1px solid rgba(0,240,255,0.25)',
              fontSize: '0.88rem',
              color: '#cbd5e1',
              lineHeight: '1.6',
              minHeight: '260px',
              overflowY: 'auto'
            }}
          >
            {response?.grounded_answer ? (
              <div className="prose-cyber" style={{ fontSize: '0.85rem' }}>
                {response.grounded_answer}
              </div>
            ) : (
              <div>
                <p style={{ color: 'var(--cyan)', fontWeight: '600', marginBottom: '8px' }}>
                  [Source: auth_bruteforce_incident.log, Lines 1-52]
                </p>
                <p style={{ marginBottom: '8px' }}>
                  Source IP <strong>192.0.2.10</strong> generated 50 consecutive authentication failures across 114 seconds targeting accounts <code>root</code>, <code>admin</code>, and <code>deploy</code>.
                </p>
                <p style={{ color: 'var(--amber)', marginBottom: '8px' }}>
                  CRITICAL EVIDENCE: At <strong>14:02:18</strong>, an <code>Accepted password for deploy from 192.0.2.10 port 40052</code> was confirmed, followed 12 seconds later by <code>sudo: COMMAND=/bin/bash</code>.
                </p>
                <div style={{ borderTop: '1px dashed rgba(0,255,136,0.3)', paddingTop: '10px', marginTop: '12px', fontSize: '11px', color: 'var(--green)' }}>
                  ✓ <strong>100% Grounded:</strong> Supported by exact log entries, NIST SP 800-61 containment playbooks, and MITRE T1110/T1548 citations.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Structured Comparison Matrix Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', color: '#fff', marginBottom: '16px' }}>
          Comparative Evaluation Matrix (Normal LLM vs. Cyber RAG Assistant)
        </h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-dim)', textAlign: 'left' }}>
                <th style={{ padding: '12px', color: 'var(--text-muted)' }}>Investigation Capability</th>
                <th style={{ padding: '12px', color: 'var(--red)' }}>Normal LLM Chatbot</th>
                <th style={{ padding: '12px', color: 'var(--cyan)' }}>Your Cybersecurity RAG Assistant</th>
              </tr>
            </thead>
            <tbody>
              {comparisonRows.map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                  <td style={{ padding: '12px', fontWeight: '600', color: '#fff' }}>{row.feature}</td>
                  <td style={{ padding: '12px', color: '#94a3b8' }}>{row.normal}</td>
                  <td style={{ padding: '12px', color: 'var(--green)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <CheckCircle style={{ width: '14px', height: '14px', flexShrink: 0 }} />
                      <span>{row.rag}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
