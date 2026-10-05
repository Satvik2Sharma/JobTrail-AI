import React from 'react';
import { ExplainableMatch } from '../types';
import { CheckCircle2, CircleDashed, Info, Sparkles, Brain, Award, GraduationCap, MapPin } from 'lucide-react';

interface MatchBreakdownCardProps {
  match: ExplainableMatch;
  className?: string;
  compact?: boolean;
}

export const MatchBreakdownCard: React.FC<MatchBreakdownCardProps> = ({ match, className = '', compact = false }) => {
  const scoreMetrics = [
    {
      label: 'Semantic Similarity',
      score: match.semantic_match,
      weight: '50% weight',
      icon: Brain,
      color: 'from-blue-500 to-indigo-500',
      bgColor: 'bg-blue-500/10',
      textColor: 'text-blue-400',
    },
    {
      label: 'Skill Overlap',
      score: match.skill_match,
      weight: '25% weight',
      icon: Award,
      color: 'from-emerald-500 to-teal-500',
      bgColor: 'bg-emerald-500/10',
      textColor: 'text-emerald-400',
    },
    {
      label: 'Eligibility & Degree',
      score: match.eligibility_match,
      weight: '15% weight',
      icon: GraduationCap,
      color: 'from-amber-500 to-orange-500',
      bgColor: 'bg-amber-500/10',
      textColor: 'text-amber-400',
    },
    {
      label: 'Preferences Alignment',
      score: match.preference_match,
      weight: '10% weight',
      icon: MapPin,
      color: 'from-purple-500 to-pink-500',
      bgColor: 'bg-purple-500/10',
      textColor: 'text-purple-400',
    },
  ];

  return (
    <div className={`bg-slate-900/90 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between pb-5 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-brand-400 mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            Explainable Career Matching Engine
          </div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <span>Compatibility Breakdown</span>
          </h3>
        </div>
        <div className="text-right">
          <div className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-emerald-300">
            {match.overall_match}%
          </div>
          <div className="text-xs text-slate-400 font-medium">Overall Hybrid Match</div>
        </div>
      </div>

      {/* 4 Score Bars */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 my-6">
        {scoreMetrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div key={idx} className="bg-slate-950/60 border border-slate-800/60 rounded-xl p-3.5">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`p-1.5 rounded-lg ${m.bgColor} ${m.textColor}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-200">{m.label}</div>
                    <div className="text-[11px] text-slate-500">{m.weight}</div>
                  </div>
                </div>
                <div className="text-base font-bold text-slate-100">{m.score}%</div>
              </div>
              <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${m.color} transition-all duration-700 ease-out`}
                  style={{ width: `${m.score}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Matching & Missing Skills */}
      <div className="space-y-4 pt-2">
        {/* Matching skills */}
        <div>
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Matching Skills ({match.matching_skills.length})</span>
          </div>
          {match.matching_skills.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {match.matching_skills.map((s, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
                >
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  {s}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No matching skills detected in profile.</p>
          )}
        </div>

        {/* Missing skills */}
        {match.missing_skills.length > 0 && (
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <CircleDashed className="w-4 h-4 text-amber-400" />
              <span>Skills to Bridge / Missing ({match.missing_skills.length})</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {match.missing_skills.map((s, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800/80 text-amber-300/90 border border-amber-500/20"
                >
                  <CircleDashed className="w-3 h-3 text-amber-400" />
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Why This Job? - Evidence-Based Explanation */}
      {!compact && match.explanation.length > 0 && (
        <div className="mt-6 pt-5 border-t border-slate-800/80">
          <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <Info className="w-4 h-4 text-blue-400" />
            <span>Why this opportunity matches you:</span>
          </div>
          <ul className="space-y-2">
            {match.explanation.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-300 leading-relaxed">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-400 mt-1.5 shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
