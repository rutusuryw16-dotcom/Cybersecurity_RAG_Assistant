import React, { useState } from 'react';
import { Terminal, Send, Sparkles, BookOpen, CheckCircle, Clock, FileText, AlertCircle, ArrowUpRight } from 'lucide-react';

export default function InvestigationChat({
  query,
  setQuery,
  incidentContext,
  setIncidentContext,
  onInvestigate,
  response,
  loading,
}) {
  const [selectedCitation, setSelectedCitation] = useState(null);

  const sampleQuestions = [
    {
      label: '50 Failed Logins (192.0.2.10)',
      q: 'Why was IP 192.0.2.10 flagged for 50 failed logins and did any login subsequently succeed?',
      ctx: 'Brute-force SSH alert from IP 192.0.2.10 over 2-minute duration',
    },
    {
      label: 'Sudo Abuse & PrivEsc',
      q: 'Did user deploy execute unauthorized sudo commands or elevate to root privileges?',
      ctx: 'Suspicious sudo execution event logged for user deploy',
    },
    {
      label: 'Web Command Injection',
      q: 'Identify the command injection exploit payload from 203.0.113.88 and its MITRE ATT&CK mapping.',
      ctx: 'HTTP POST exploit logged on web ping endpoint',
    },
    {
      label: 'NIST Containment Playbook',
      q: 'What are the recommended NIST SP 800-61 containment and eradication steps for this brute force incident?',
      ctx: 'NIST Incident Handling Guide reference',
    },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    onInvestigate(query, incidentContext);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Query Terminal Panel */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
          <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(0, 240, 255, 0.1)', color: 'var(--cyan)' }}>
            <Terminal style={{ width: '18px', height: '18px' }} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.2rem', color: '#fff' }}>RAG Cybersecurity Investigation Terminal</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Ask questions about security logs, suspicious IPs, or incident procedures. The assistant retrieves evidence and grounds findings with citations.
            </p>
          </div>
        </div>

        {/* Preset Prompt Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-dim)', alignSelf: 'center', marginRight: '4px' }}>
            Quick Prompts:
          </span>
          {sampleQuestions.map((sq, i) => (
            <button
              key={i}
              onClick={() => {
                setQuery(sq.q);
                setIncidentContext(sq.ctx);
                onInvestigate(sq.q, sq.ctx);
              }}
              style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-dim)',
                color: '#cbd5e1',
                padding: '5px 10px',
                borderRadius: '6px',
                fontSize: '11px',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--cyan)';
                e.currentTarget.style.color = '#fff';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-dim)';
                e.currentTarget.style.color = '#cbd5e1';
              }}
            >
              <Sparkles style={{ width: '12px', height: '12px', color: 'var(--cyan)' }} />
              {sq.label}
            </button>
          ))}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', gap: '12px' }}>
            <textarea
              rows={3}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. What does the repeated failed login alert from 192.0.2.10 mean, and what log entries support it?"
              style={{
                flex: '1',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border-dim)',
                borderRadius: '8px',
                padding: '12px 16px',
                color: '#fff',
                fontSize: '0.9rem',
                fontFamily: 'inherit',
                outline: 'none',
                resize: 'none',
              }}
              onFocus={(e) => (e.currentTarget.style.borderColor = 'var(--cyan)')}
              onBlur={(e) => (e.currentTarget.style.borderColor = 'var(--border-dim)')}
            />

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="btn-cyber-primary"
              style={{
                minWidth: '140px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                gap: '6px',
                opacity: loading || !query.trim() ? 0.6 : 1,
              }}
            >
              <Send style={{ width: '18px', height: '18px' }} />
              <span>{loading ? 'Retrieving...' : 'Investigate'}</span>
            </button>
          </div>

          {incidentContext && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
              <span style={{ color: 'var(--cyan)', fontWeight: '600' }}>Active Incident Context:</span>
              <span style={{ backgroundColor: 'var(--bg-elevated)', padding: '2px 8px', borderRadius: '4px' }}>
                {incidentContext}
              </span>
              <button
                type="button"
                onClick={() => setIncidentContext('')}
                style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer', textDecoration: 'underline' }}
              >
                Clear
              </button>
            </div>
          )}
        </form>
      </div>

      {/* RAG Investigation Output */}
      {response && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Metrics Status Strip */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '12px',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 18px',
              backgroundColor: '#0a1020',
              borderRadius: '8px',
              border: '1px solid var(--border-dim)',
            }}
          >
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                <CheckCircle style={{ width: '15px', height: '15px', color: 'var(--green)' }} />
                <span style={{ color: 'var(--text-muted)' }}>Groundedness:</span>
                <strong style={{ color: 'var(--green)' }}>{(response.groundedness_score * 100).toFixed(1)}%</strong>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                <BookOpen style={{ width: '15px', height: '15px', color: 'var(--cyan)' }} />
                <span style={{ color: 'var(--text-muted)' }}>Retrieved Evidence Chunks:</span>
                <strong style={{ color: 'var(--cyan)' }}>{response.retrieved_count}</strong>
              </div>

              {response.mitre_technique && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
                  <AlertCircle style={{ width: '15px', height: '15px', color: 'var(--amber)' }} />
                  <span style={{ color: 'var(--text-muted)' }}>MITRE Technique:</span>
                  <strong style={{ color: 'var(--amber)' }}>{response.mitre_technique}</strong>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-dim)' }}>
              <Clock style={{ width: '14px', height: '14px' }} />
              <span>Response Latency: <strong style={{ color: '#fff' }}>{response.latency_ms} ms</strong></span>
            </div>
          </div>

          {/* Structured Grounded Findings */}
          <div className="glass-panel" style={{ padding: '28px' }}>
            <div className="prose-cyber" style={{ whiteSpace: 'pre-wrap' }}>
              {response.grounded_answer}
            </div>

            {/* Citations Section */}
            <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid var(--border-dim)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <FileText style={{ width: '16px', height: '16px', color: 'var(--cyan)' }} />
                <h4 style={{ fontSize: '0.9rem', color: '#fff', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Retrieved Evidence Sources & Citations
                </h4>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
                {response.citations.map((c, i) => (
                  <div
                    key={i}
                    onClick={() => setSelectedCitation(c)}
                    style={{
                      backgroundColor: 'var(--bg-input)',
                      border: '1px solid var(--border-dim)',
                      borderRadius: '6px',
                      padding: '10px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--cyan)')}
                    onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-dim)')}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--cyan)', fontWeight: '600' }}>
                        {c.source_file}
                      </span>
                      <span style={{ fontSize: '10px', color: 'var(--green)', backgroundColor: 'rgba(0,255,136,0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                        {(c.score * 100).toFixed(0)}% match
                      </span>
                    </div>
                    <p style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: '1.4', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebKitLineClamp: 2, WebKitBoxOrient: 'vertical' }}>
                      {c.snippet}
                    </p>
                    <span style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '4px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      View evidence snippet <ArrowUpRight style={{ width: '10px', height: '10px' }} />
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Citation Detail Modal */}
      {selectedCitation && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.75)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '20px',
          }}
          onClick={() => setSelectedCitation(null)}
        >
          <div
            className="glass-panel"
            style={{ maxWidth: '640px', width: '100%', padding: '24px', backgroundColor: '#090e1c' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div>
                <h3 style={{ fontSize: '1.1rem', color: '#fff' }}>Evidence Inspector</h3>
                <p style={{ fontSize: '11px', color: 'var(--cyan)', fontFamily: 'var(--font-mono)' }}>
                  Source: {selectedCitation.source_file} (Chunk {selectedCitation.chunk_index})
                </p>
              </div>
              <button
                onClick={() => setSelectedCitation(null)}
                style={{ background: 'none', border: 'none', color: '#fff', fontSize: '1.2rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ backgroundColor: '#040711', padding: '16px', borderRadius: '6px', border: '1px solid var(--border-dim)', marginBottom: '16px' }}>
              <pre style={{ color: '#e2e8f0', fontSize: '12px', fontFamily: 'var(--font-mono)', whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                {selectedCitation.snippet}
              </pre>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px', color: 'var(--text-dim)' }}>
              <span>Category: <strong>{selectedCitation.category}</strong></span>
              <span>Relevance Score: <strong>{(selectedCitation.score * 100).toFixed(1)}%</strong></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
