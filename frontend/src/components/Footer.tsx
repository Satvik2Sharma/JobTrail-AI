import React from 'react';
import { Compass, ShieldAlert, Cpu, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-950 border-t border-slate-900 mt-20 text-slate-400 text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-brand-500/20 text-brand-400 border border-brand-500/30 flex items-center justify-center">
                <Compass className="w-4 h-4" />
              </div>
              <span className="font-bold text-white text-base tracking-tight">JobTrail<span className="text-brand-400">-AI</span></span>
            </div>
            <p className="text-xs text-slate-400 max-w-md leading-relaxed">
              AI-powered job and internship recommendation platform featuring an Explainable Career Matching Engine,
              transparent four-dimensional scoring, and targeted skill-gap analysis.
            </p>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-300">
              <Cpu className="w-3.5 h-3.5 text-brand-400" />
              <span>Sentence-Transformers (all-MiniLM-L6-v2) + PyMuPDF + FastAPI</span>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-3">Architecture</h4>
            <ul className="space-y-2 text-xs">
              <li className="text-slate-400">Semantic Cosine Vector Space (50%)</li>
              <li className="text-slate-400">Normalized Skill Overlap (25%)</li>
              <li className="text-slate-400">Eligibility & Degree Match (15%)</li>
              <li className="text-slate-400">Workplace Preferences (10%)</li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-3">Academic & Demo</h4>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1.5">
              <div className="flex items-center gap-1.5 text-amber-400 font-semibold">
                <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
                <span>Prototype Disclaimer</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                The included jobs are synthetic prototype/demo records and are not live employment listings.
              </p>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div>
            &copy; 2026 JobTrail-AI. Built for genuine, transparent, explainable recommendations.
          </div>
          <div className="text-slate-500">
            Pretrained Sentence Transformer embedding pipeline with deterministic scoring.
          </div>
        </div>
      </div>
    </footer>
  );
};
