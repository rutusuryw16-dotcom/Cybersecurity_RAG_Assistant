import React from 'react';
import { Shield, Terminal, Database, FileText, Layers, CheckCircle2, RefreshCw } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, stats, onReloadBenchmarks, loading }) {
  const tabs = [
    { id: 'radar', label: 'Threat Radar & Incidents', icon: Shield },
    { id: 'assistant', label: 'AI Investigation Assistant', icon: Terminal },
    { id: 'compare', label: 'RAG vs Normal LLM', icon: Layers },
    { id: 'logs', label: 'Log & Knowledge Ingestion', icon: Database },
    { id: 'evaluation', label: 'Evaluation & Benchmarks', icon: CheckCircle2 },
  ];

  return (
    <header className="border-b border-[var(--border-dim)] bg-[#070b16]/90 backdrop-blur-md sticky top-0 z-50">
      {/* Top SOC Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-600/30 border border-cyan-500/40 flex items-center justify-center shadow-[0_0_15px_rgba(0,240,255,0.3)]">
            <Shield className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-white">CYBERSOC RAG ASSISTANT</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                Cloud v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Evidence-Based Cybersecurity Threat Investigation & Reasoning System
            </p>
          </div>
        </div>

        {/* Right Status Badges */}
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#0e1628] border border-[var(--border-dim)]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300 font-mono">SOC Active</span>
            <span className="text-slate-500">|</span>
            <span className="text-cyan-400 font-mono">{stats.totalChunks || 0} Chunks</span>
          </div>

          <button
            onClick={onReloadBenchmarks}
            disabled={loading}
            className="btn-cyber-outline py-1 px-3 text-xs"
            title="Reload 50-failed-logins scenario and MITRE knowledge base"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span className="hidden md:inline">Reset Benchmarks</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex overflow-x-auto gap-1 border-t border-[var(--border-dim)]/50">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold whitespace-nowrap transition-all border-b-2 ${
                isActive
                  ? 'border-cyan-400 text-cyan-300 bg-cyan-950/20'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
              {tab.label}
            </button>
          );
        })}
      </div>
    </header>
  );
}
