import React, { useState } from 'react';
import { AlertTriangle, ShieldAlert, Terminal, Eye, ExternalLink, Filter, Clock, Search, ArrowRight } from 'lucide-react';

export default function IncidentFeed({ incidents, onInvestigate, loading }) {
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIncident, setSelectedIncident] = useState(null);

  const filtered = incidents.filter((inc) => {
    const matchSev = filterSeverity === 'ALL' || inc.severity === filterSeverity;
    const matchQ =
      inc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.source_ip.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inc.mitre_technique.toLowerCase().includes(searchQuery.toLowerCase());
    return matchSev && matchQ;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Banner & Quick Stats */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span className="pulse-indicator" style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--red)' }}></span>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#fff' }}>Correlated Incident Alerts</h2>
              <span className="badge-critical" style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: '700' }}>
                {incidents.filter(i => i.severity === 'CRITICAL').length} Critical
              </span>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              Automated correlation rules running on ingested logs. Click <strong>Investigate with RAG</strong> to query evidence via LLM.
            </p>
          </div>

          {/* Severity Counters */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => {
              const count = incidents.filter((i) => i.severity === sev).length;
              const badgeClass = `badge-${sev.toLowerCase()}`;
              return (
                <div
                  key={sev}
                  onClick={() => setFilterSeverity(filterSeverity === sev ? 'ALL' : sev)}
                  className={badgeClass}
                  style={{
                    padding: '8px 14px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    transition: 'all 0.2s ease',
                    opacity: filterSeverity === 'ALL' || filterSeverity === sev ? 1 : 0.4
                  }}
                >
                  <span style={{ fontWeight: '800', fontSize: '1rem' }}>{count}</span>
                  <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{sev}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Filter Bar */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-dim)' }}>
          <div style={{ position: 'relative', flex: '1', minWidth: '220px' }}>
            <Search style={{ position: 'absolute', left: '12px', top: '10px', width: '16px', height: '16px', color: 'var(--text-dim)' }} />
            <input
              type="text"
              placeholder="Search by IP, title, or MITRE technique..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border-dim)',
                borderRadius: '6px',
                padding: '8px 12px 8px 36px',
                color: '#fff',
                fontSize: '0.85rem',
                outline: 'none'
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '6px' }}>
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((s) => (
              <button
                key={s}
                onClick={() => setFilterSeverity(s)}
                style={{
                  backgroundColor: filterSeverity === s ? 'var(--cyan)' : 'transparent',
                  color: filterSeverity === s ? '#000' : 'var(--text-muted)',
                  border: '1px solid var(--border-dim)',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  fontSize: '11px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Incidents Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '16px' }}>
        {filtered.map((inc) => {
          const isCrit = inc.severity === 'CRITICAL';
          const isHigh = inc.severity === 'HIGH';
          const badgeClass = `badge-${inc.severity.toLowerCase()}`;

          return (
            <div
              key={inc.alert_id}
              className={`glass-panel ${isCrit ? 'glass-panel-glow-red' : ''}`}
              style={{
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              {/* Top Row: Severity & MITRE */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <span className={badgeClass} style={{ padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: '700' }}>
                    {inc.severity}
                  </span>
                  <span
                    style={{
                      fontSize: '11px',
                      color: 'var(--cyan)',
                      fontFamily: 'var(--font-mono)',
                      backgroundColor: 'rgba(0, 240, 255, 0.08)',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      border: '1px solid rgba(0, 240, 255, 0.2)'
                    }}
                  >
                    {inc.mitre_technique.split('-')[0].trim()}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.05rem', color: '#fff', marginBottom: '8px', lineHeight: '1.4' }}>
                  {inc.title}
                </h3>

                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.5', marginBottom: '16px' }}>
                  {inc.description}
                </p>

                {/* Entity Chips */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
                  <div style={{ backgroundColor: 'var(--bg-elevated)', padding: '4px 8px', borderRadius: '4px', fontSize: '11px' }}>
                    <span style={{ color: 'var(--text-dim)' }}>Source IP: </span>
                    <strong style={{ color: 'var(--cyan)', fontFamily: 'var(--font-mono)' }}>{inc.source_ip}</strong>
                  </div>
                  <div style={{ backgroundColor: 'var(--bg-elevated)', padding: '4px 8px', borderRadius: '4px', fontSize: '11px' }}>
                    <span style={{ color: 'var(--text-dim)' }}>Target: </span>
                    <strong style={{ color: '#e2e8f0' }}>{inc.target_user}</strong>
                  </div>
                  <div style={{ backgroundColor: 'var(--bg-elevated)', padding: '4px 8px', borderRadius: '4px', fontSize: '11px' }}>
                    <span style={{ color: 'var(--text-dim)' }}>Events: </span>
                    <strong style={{ color: 'var(--green)' }}>{inc.event_count}</strong>
                  </div>
                </div>
              </div>

              {/* Bottom Actions */}
              <div style={{ display: 'flex', gap: '10px', borderTop: '1px solid var(--border-dim)', paddingTop: '14px' }}>
                <button
                  onClick={() => onInvestigate(inc.suggested_investigation_query, inc.description)}
                  className="btn-cyber-primary"
                  style={{ flex: '1', justifyContent: 'center', fontSize: '0.8rem', padding: '8px 12px' }}
                >
                  <Terminal style={{ width: '14px', height: '14px' }} />
                  Investigate with RAG
                </button>
                <button
                  onClick={() => setSelectedIncident(selectedIncident?.alert_id === inc.alert_id ? null : inc)}
                  className="btn-cyber-outline"
                  style={{ padding: '8px 12px', fontSize: '0.8rem' }}
                  title="View Raw Evidence Logs"
                >
                  <Eye style={{ width: '14px', height: '14px' }} />
                </button>
              </div>

              {/* Collapsible Evidence Log Drawer */}
              {selectedIncident?.alert_id === inc.alert_id && (
                <div style={{ marginTop: '14px', backgroundColor: 'var(--bg-input)', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-dim)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--cyan)' }}>RAW LOG EVIDENCE ({inc.evidence_logs.length})</span>
                    <span style={{ fontSize: '10px', color: 'var(--text-dim)' }}>Last seen: {inc.timestamp}</span>
                  </div>
                  <div style={{ maxHeight: '140px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {inc.evidence_logs.map((log, idx) => (
                      <div key={idx} style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: '#cbd5e1', backgroundColor: '#070c18', padding: '6px', borderRadius: '4px' }}>
                        <span style={{ color: 'var(--cyan)' }}>[{log.timestamp}]</span> {log.raw_message}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="glass-panel" style={{ padding: '48px', textAlign: 'center' }}>
          <ShieldAlert style={{ width: '48px', height: '48px', color: 'var(--cyan)', margin: '0 auto 16px' }} />
          <h3 style={{ color: '#fff', marginBottom: '8px' }}>No Incidents Matched Filter</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Try selecting a different severity level or reset benchmark datasets using the top bar button.
          </p>
        </div>
      )}
    </div>
  );
}
