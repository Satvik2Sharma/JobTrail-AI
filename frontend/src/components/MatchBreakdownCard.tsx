import React from 'react';
import { ExplainableMatch } from '../types';
import { Check, Circle, Sparkles, Brain, Award, GraduationCap, MapPin, HelpCircle } from 'lucide-react';

interface MatchBreakdownCardProps {
  match: ExplainableMatch;
  className?: string;
  compact?: boolean;
}

export const MatchBreakdownCard: React.FC<MatchBreakdownCardProps> = ({ match, className = '', compact = false }) => {
  const scoreMetrics = [
    {
      label: 'Semantic Match',
      score: match.semantic_match,
      weight: '50% weight',
      icon: Brain,
      color: 'from-blue-500 to-indigo-500',
      barColor: 'bg-blue-500',
      bgColor: 'bg-blue-500/10',
      textColor: 'text-blue-400',
    },
    {
      label: 'Skill Match',
      score: match.skill_match,
      weight: '25% weight',
      icon: Award,
      color: 'from-emerald-500 to-teal-500',
      barColor: 'bg-emerald-500',
      bgColor: 'bg-emerald-500/10',
      textColor: 'text-emerald-400',
    },
    {
      label: 'Eligibility',
      score: match.eligibility_match,
      weight: '15% weight',
      icon: GraduationCap,
      color: 'from-amber-500 to-orange-500',
      barColor: 'bg-amber-500',
      bgColor: 'bg-amber-500/10',
      textColor: 'text-amber-400',
    },
    {
      label: 'Preference',
      score: match.preference_match,
      weight: '10% weight',
      icon: MapPin,
      color: 'from-purple-500 to-pink-500',
      barColor: 'bg-purple-500',
      bgColor: 'bg-purple-500/10',
      textColor: 'text-purple-400',
    },
  ];

  return (
    <div className={`bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 backdrop-blur-sm shadow-xl ${className}`}>
      {/* Header Badge */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-6">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-brand-400">
          <Sparkles className="w-4 h-4" />
          <span>JobTrail-AI Explainable Matching Engine</span>
        </div>
        <div className="text-[11px] text-slate-500 font-mono hidden sm:inline">
          Hybrid Multi-Factor Vector Proximity
        </div>
      </div>

      {/* Prominent Overall Match Block */}
      <div className="text-center py-6 px-4 bg-slate-950/80 border border-slate-800/90 rounded-2xl mb-6 shadow-inner">
        <div className="text-5xl sm:text-6xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-brand-400 via-emerald-300 to-teal-200">
          {match.overall_match}%
        </div>
        <div className="text-sm font-bold uppercase tracking-widest text-slate-200 mt-1">
          Overall Match
        </div>
        <div className="text-xs text-slate-400 mt-2 flex items-center justify-center gap-2 flex-wrap">
          <span className="inline-flex items-center gap-1 font-medium text-blue-400">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400" /> 50% Semantic
          </span>
          <span className="text-slate-600">&bull;</span>
          <span className="inline-flex items-center gap-1 font-medium text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> 25% Skills
          </span>
          <span className="text-slate-600">&bull;</span>
          <span className="inline-flex items-center gap-1 font-medium text-amber-400">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" /> 15% Eligibility
          </span>
          <span className="text-slate-600">&bull;</span>
          <span className="inline-flex items-center gap-1 font-medium text-purple-400">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400" /> 10% Preference
          </span>
        </div>
      </div>

      {/* 4 Multi-Factor Score Bars */}
      <div className="space-y-3.5 mb-8">
        {scoreMetrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div key={idx} className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2.5">
                  <div className={`p-1.5 rounded-lg ${m.bgColor} ${m.textColor}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-sm font-semibold text-slate-200">{m.label}</span>
                    <span className="text-[11px] text-slate-500 ml-2 font-mono">({m.weight})</span>
                  </div>
                </div>
                <div className="text-sm sm:text-base font-extrabold text-white font-mono">
                  {m.score}%
                </div>
              </div>
              <div className="w-full bg-slate-800/80 rounded-full h-2.5 overflow-hidden">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${m.color} transition-all duration-700 ease-out`}
                  style={{ width: `${Math.max(2, Math.min(100, m.score))}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* MATCHING SKILLS & SKILL GAP */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800/80">
        {/* MATCHING SKILLS */}
        <div className="space-y-3">
          <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <span className="text-emerald-400 font-bold">&#10003;</span>
            <span>MATCHING SKILLS ({match.matching_skills.length})</span>
          </div>
          {match.matching_skills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {match.matching_skills.map((s, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 shadow-sm"
                >
                  <Check className="w-3.5 h-3.5 text-emerald-400 stroke-[3]" />
                  <span>{s}</span>
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic bg-slate-950/40 p-3 rounded-xl border border-slate-800/50">
              No direct technical skills overlap detected between candidate profile and job requirements.
            </p>
          )}
        </div>

        {/* SKILL GAP */}
        <div className="space-y-3">
          <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <span className="text-amber-400 font-bold">&#9675;</span>
            <span>SKILL GAP ({match.missing_skills.length})</span>
          </div>
          {match.missing_skills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {match.missing_skills.map((s, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-slate-950 text-amber-300/90 border border-amber-500/30 shadow-sm"
                >
                  <Circle className="w-3 h-3 text-amber-400" />
                  <span>{s}</span>
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-emerald-400/90 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20 font-medium">
              &#10003; Full technical skill coverage! You possess all required technical skills for this role.
            </p>
          )}
        </div>
      </div>

      {/* WHY THIS JOB? */}
      {!compact && match.explanation.length > 0 && (
        <div className="mt-8 pt-6 border-t border-slate-800/80 space-y-3">
          <div className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-brand-400" />
            <span>WHY THIS JOB?</span>
          </div>
          <div className="bg-slate-950/70 border border-slate-800/80 rounded-2xl p-4 sm:p-5">
            <ul className="space-y-2.5">
              {match.explanation.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-300 leading-relaxed">
                  <span className="w-2 h-2 rounded-full bg-brand-400 mt-1.5 shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
