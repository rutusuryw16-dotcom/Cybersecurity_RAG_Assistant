import React, { useState } from 'react';
import { UploadCloud, FileText, Database, CheckCircle, RefreshCw, AlertCircle, Search, Filter } from 'lucide-react';

export default function LogUploader({ logs, onUpload, onReload, loading, stats }) {
  const [dragOver, setDragOver] = useState(false);
  const [category, setCategory] = useState('logs');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadStatus, setUploadStatus] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await doUpload(file);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    await doUpload(file);
  };

  const doUpload = async (file) => {
    setUploadStatus('uploading');
    try {
      await onUpload(file, category);
      setUploadStatus('success');
      setTimeout(() => setUploadStatus(null), 4000);
    } catch (err) {
      setUploadStatus('error');
    }
  };

  const filteredLogs = logs.filter((l) => {
    const q = searchTerm.toLowerCase();
    return (
      l.source_ip.toLowerCase().includes(q) ||
      l.user.toLowerCase().includes(q) ||
      l.action.toLowerCase().includes(q) ||
      l.raw_message.toLowerCase().includes(q)
    );
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Upload Zone & Vector Store Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        {/* Upload Card */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <UploadCloud style={{ width: '20px', height: '20px', color: 'var(--cyan)' }} />
              <h3 style={{ fontSize: '1.1rem', color: '#fff' }}>Ingest Security Logs & Documents</h3>
            </div>
            
            {/* Category Toggle */}
            <div style={{ display: 'flex', backgroundColor: 'var(--bg-input)', padding: '2px', borderRadius: '6px', border: '1px solid var(--border-dim)' }}>
              <button
                type="button"
                onClick={() => setCategory('logs')}
                style={{
                  backgroundColor: category === 'logs' ? 'var(--cyan)' : 'transparent',
                  color: category === 'logs' ? '#000' : 'var(--text-muted)',
                  border: 'none',
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: '700',
                  cursor: 'pointer'
                }}
              >
                Security Logs
              </button>
              <button
                type="button"
                onClick={() => setCategory('knowledge_base')}
                style={{
                  backgroundColor: category === 'knowledge_base' ? 'var(--cyan)' : 'transparent',
                  color: category === 'knowledge_base' ? '#000' : 'var(--text-muted)',
                  border: 'none',
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: '700',
                  cursor: 'pointer'
                }}
              >
                Guides / Playbooks
              </button>
            </div>
          </div>

          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
            Supports <code>.csv</code>, <code>.log</code>, <code>.txt</code>, <code>.json</code>, and <code>.pdf</code>.
            Automatic PII credential redaction and chunking applied before vector indexing.
          </p>

          {/* Drag & Drop Area */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragOver ? 'var(--cyan)' : 'var(--border-dim)'}`,
              borderRadius: '8px',
              padding: '32px 20px',
              textAlign: 'center',
              backgroundColor: dragOver ? 'rgba(0, 240, 255, 0.05)' : 'var(--bg-input)',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onClick={() => document.getElementById('log-file-input')?.click()}
          >
            <input
              id="log-file-input"
              type="file"
              accept=".csv,.log,.txt,.json,.pdf"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            <FileText style={{ width: '36px', height: '36px', color: dragOver ? 'var(--cyan)' : 'var(--text-dim)', margin: '0 auto 10px' }} />
            <p style={{ color: '#fff', fontSize: '0.9rem', fontWeight: '600', marginBottom: '4px' }}>
              Drag & drop files here or click to browse
            </p>
            <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
              Target Category: <strong style={{ color: 'var(--cyan)' }}>{category}</strong>
            </span>
          </div>

          {uploadStatus === 'uploading' && (
            <p style={{ color: 'var(--cyan)', fontSize: '0.8rem', marginTop: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <RefreshCw className="animate-spin" style={{ width: '14px', height: '14px' }} /> Parsing, redacting PII, and vectorizing chunks...
            </p>
          )}
          {uploadStatus === 'success' && (
            <p style={{ color: 'var(--green)', fontSize: '0.8rem', marginTop: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle style={{ width: '14px', height: '14px' }} /> File successfully indexed into Chroma/Vector Store!
            </p>
          )}
        </div>

        {/* Knowledge Base & Vector Store Stats Card */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Database style={{ width: '20px', height: '20px', color: 'var(--cyan)' }} />
                <h3 style={{ fontSize: '1.1rem', color: '#fff' }}>Vector Store Status</h3>
              </div>
              <span className="badge-low" style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '4px' }}>
                ChromaDB / Persistent
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
              <div style={{ backgroundColor: 'var(--bg-elevated)', padding: '12px', borderRadius: '6px' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Total Embeddings</span>
                <p style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--cyan)', marginTop: '4px' }}>
                  {stats.totalChunks || 0}
                </p>
              </div>
              <div style={{ backgroundColor: 'var(--bg-elevated)', padding: '12px', borderRadius: '6px' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Unique Sources</span>
                <p style={{ fontSize: '1.5rem', fontWeight: '800', color: '#fff', marginTop: '4px' }}>
                  {stats.uniqueSources || 0}
                </p>
              </div>
            </div>

            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              <span style={{ fontWeight: '600', color: '#fff' }}>Indexed Sources:</span>
              <ul style={{ listStyle: 'none', paddingLeft: '0', marginTop: '6px', maxHeight: '100px', overflowY: 'auto' }}>
                {stats.sourceFiles?.map((sf, i) => (
                  <li key={i} style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#cbd5e1', padding: '2px 0' }}>
                    ▹ {sf}
                  </li>
                )) || <li style={{ color: 'var(--text-dim)' }}>None loaded</li>}
              </ul>
            </div>
          </div>

          <button
            onClick={onReload}
            disabled={loading}
            className="btn-cyber-outline"
            style={{ width: '100%', justifyContent: 'center', marginTop: '16px' }}
          >
            <RefreshCw className={loading ? 'animate-spin' : ''} style={{ width: '14px', height: '14px' }} />
            Reload 50-Failed-Logins Benchmark Dataset
          </button>
        </div>
      </div>

      {/* Ingested Log Entries Explorer */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', color: '#fff' }}>Ingested Security Log Records ({filteredLogs.length})</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              Normalized logs parsed from syslog, auth.log, and CSV sources.
            </p>
          </div>

          <div style={{ position: 'relative', width: '280px' }}>
            <Search style={{ position: 'absolute', left: '10px', top: '9px', width: '15px', height: '15px', color: 'var(--text-dim)' }} />
            <input
              type="text"
              placeholder="Filter logs by IP, user, or action..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border-dim)',
                borderRadius: '6px',
                padding: '6px 12px 6px 32px',
                color: '#fff',
                fontSize: '0.8rem',
                outline: 'none'
              }}
            />
          </div>
        </div>

        {/* Table */}
        <div style={{ overflowX: 'auto', maxHeight: '420px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-dim)', textAlign: 'left', backgroundColor: 'var(--bg-elevated)', position: 'sticky', top: 0 }}>
                <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Timestamp</th>
                <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Source IP</th>
                <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>User</th>
                <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Action</th>
                <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Severity</th>
                <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Raw Log Message</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.slice(0, 100).map((log, i) => {
                const badgeClass = `badge-${log.severity.toLowerCase()}`;
                return (
                  <tr key={log.id || i} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                    <td style={{ padding: '8px 12px', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>
                      {log.timestamp}
                    </td>
                    <td style={{ padding: '8px 12px', fontFamily: 'var(--font-mono)', color: 'var(--cyan)' }}>
                      {log.source_ip}
                    </td>
                    <td style={{ padding: '8px 12px', color: '#e2e8f0', fontWeight: '500' }}>
                      {log.user}
                    </td>
                    <td style={{ padding: '8px 12px', color: '#cbd5e1' }}>
                      {log.action}
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <span className={badgeClass} style={{ padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: '700' }}>
                        {log.severity}
                      </span>
                    </td>
                    <td style={{ padding: '8px 12px', fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#94a3b8', maxWidth: '380px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={log.raw_message}>
                      {log.raw_message}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
