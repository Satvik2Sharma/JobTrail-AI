import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Sparkles,
  ChevronDown,
  ChevronUp,
  FileText,
  LayoutDashboard,
  Brain,
  TrendingUp,
  Search,
  Bookmark,
  Send,
  CheckCircle2,
} from 'lucide-react';

export const DemoGuideBar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const demoSteps = [
    { label: '1. Resume AI', path: '/resume-intelligence', icon: FileText },
    { label: '2. Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: '3. Top Match', path: '/jobs/9', icon: Brain },
    { label: '4. Match Analysis', path: '/jobs/9/match', icon: Sparkles },
    { label: '5. Skill Gap', path: '/dashboard#skill-gap', icon: TrendingUp },
    { label: '6. Semantic Search', path: '/jobs', icon: Search },
    { label: '7. Saved Jobs', path: '/saved', icon: Bookmark },
    { label: '8. Apply Tracker', path: '/applications', icon: Send },
  ];

  return (
    <div className="bg-slate-900/95 border-b border-slate-800 text-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
            </span>
            <span className="font-bold text-white">Evaluator Demo Tour:</span>
            <span className="text-slate-400 hidden sm:inline">
              Follow the academic workflow from Resume Parsing to Hybrid Recommendations and Application Tracking.
            </span>
          </div>

          <button
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-1 text-[11px] font-semibold text-brand-400 hover:text-brand-300 transition-colors"
          >
            <span>{isOpen ? 'Collapse Guide' : 'Show 8-Step Demo Tour'}</span>
            {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {isOpen && (
          <div className="pt-3 pb-2 border-t border-slate-800/80 mt-2">
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs scrollbar-none">
              {demoSteps.map((step, idx) => {
                const Icon = step.icon;
                const isActive = location.pathname === step.path;
                return (
                  <React.Fragment key={idx}>
                    <Link
                      to={step.path}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl whitespace-nowrap text-xs font-medium transition-colors ${
                        isActive
                          ? 'bg-brand-500 text-slate-950 font-bold shadow-md shadow-brand-500/20'
                          : 'bg-slate-950/80 hover:bg-slate-800 text-slate-300 border border-slate-800'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{step.label}</span>
                    </Link>
                    {idx < demoSteps.length - 1 && (
                      <span className="text-slate-600 text-xs px-0.5">&rarr;</span>
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
