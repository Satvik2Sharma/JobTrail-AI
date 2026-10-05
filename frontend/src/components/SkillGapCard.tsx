import React from 'react';
import { SkillGapResponse } from '../types';
import { TrendingUp, CheckCircle, AlertTriangle, Lightbulb, ArrowUpRight } from 'lucide-react';

interface SkillGapCardProps {
  data: SkillGapResponse;
  className?: string;
}

export const SkillGapCard: React.FC<SkillGapCardProps> = ({ data, className = '' }) => {
  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-2xl p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Skill-Gap Intelligence</h3>
            <p className="text-xs text-slate-400">
              {data.target_job_title ? `Target: ${data.target_job_title}` : 'Target Career Overview'}
            </p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-2xl font-black text-brand-400">{data.readiness_score}%</div>
          <div className="text-[11px] text-slate-500 font-medium">Readiness Index</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="my-4">
        <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-brand-500 to-emerald-400 rounded-full transition-all duration-500"
            style={{ width: `${data.readiness_score}%` }}
          />
        </div>
      </div>

      {/* Career Insight Box */}
      <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/20 mb-5 flex items-start gap-3">
        <Lightbulb className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
        <p className="text-xs text-blue-200 leading-relaxed font-medium">
          {data.career_insight}
        </p>
      </div>

      {/* Missing Skills with Priority */}
      <div className="space-y-4">
        <div>
          <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-amber-400">
              <AlertTriangle className="w-3.5 h-3.5" />
              High Impact Skill Gaps ({data.missing.length})
            </span>
          </div>

          {data.missing_details && data.missing_details.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {data.missing_details.slice(0, 6).map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/70 border border-slate-800"
                >
                  <div>
                    <div className="text-xs font-semibold text-slate-200">{item.skill}</div>
                    <div className="text-[10px] text-slate-500">{item.category || 'Technical'}</div>
                  </div>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${
                      item.priority === 'High'
                        ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}
                  >
                    {item.priority} Priority
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No significant missing skill gaps identified.</p>
          )}
        </div>

        {/* Acquired Skills */}
        <div>
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            <span>Skills You Already Have ({data.already_have.length})</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {data.already_have.map((s, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
              >
                {s}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
