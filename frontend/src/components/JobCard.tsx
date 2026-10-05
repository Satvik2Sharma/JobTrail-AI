import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Job, ExplainableMatch } from '../types';
import { MatchBadge } from './MatchBadge';
import { api } from '../services/api';
import {
  MapPin,
  Building2,
  Bookmark,
  ExternalLink,
  Sparkles,
  ChevronRight,
  Briefcase,
  Check,
} from 'lucide-react';

interface JobCardProps {
  job: Job;
  match?: ExplainableMatch;
  onSavedChange?: (isSaved: boolean) => void;
}

export const JobCard: React.FC<JobCardProps> = ({ job, match, onSavedChange }) => {
  const [isSaved, setIsSaved] = useState<boolean>(job.is_saved);
  const [isSaving, setIsSaving] = useState<boolean>(false);

  const toggleSave = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsSaving(true);
    try {
      if (isSaved) {
        await api.unsaveJob(job.id);
        setIsSaved(false);
        onSavedChange?.(false);
      } else {
        await api.saveJob(job.id);
        setIsSaved(true);
        onSavedChange?.(true);
      }
    } catch (err) {
      console.error('Failed to toggle save job:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="group relative bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-slate-700/80 rounded-2xl p-5 transition-all duration-200 shadow-sm hover:shadow-md flex flex-col justify-between">
      <div>
        {/* Top line: Company & Save */}
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
            <Building2 className="w-3.5 h-3.5 text-slate-500" />
            <span className="truncate max-w-[200px] text-slate-300 font-semibold">{job.company}</span>
            {job.remote && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Remote
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {match && <MatchBadge score={match.overall_match} size="sm" />}
            <button
              onClick={toggleSave}
              disabled={isSaving}
              className={`p-2 rounded-xl border transition-colors ${
                isSaved
                  ? 'bg-brand-500/10 border-brand-500/30 text-brand-400'
                  : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
              }`}
              title={isSaved ? 'Remove from saved' : 'Save job'}
            >
              <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-brand-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Title */}
        <Link to={`/jobs/${job.id}`} className="block group-hover:text-brand-400 transition-colors">
          <h3 className="text-base font-bold text-white mb-2 leading-snug line-clamp-1">{job.title}</h3>
        </Link>

        {/* Meta badges */}
        <div className="flex flex-wrap items-center gap-y-1 gap-x-3 text-xs text-slate-400 mb-3.5">
          <span className="flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-slate-500" />
            {job.location}
          </span>
          <span className="flex items-center gap-1">
            <Briefcase className="w-3.5 h-3.5 text-slate-500" />
            {job.employment_type}
          </span>
          {job.salary_min && (
            <span className="text-slate-300 font-medium">
              ${(job.salary_min / 1000).toFixed(0)}k - ${(job.salary_max! / 1000).toFixed(0)}k
            </span>
          )}
        </div>

        {/* Description snippet */}
        <p className="text-xs text-slate-400 line-clamp-2 mb-4 leading-relaxed">
          {job.description}
        </p>

        {/* Skills pill tags */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {job.skills.slice(0, 5).map((skill, idx) => {
            const isMatched = match?.matching_skills.includes(skill);
            return (
              <span
                key={idx}
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium border ${
                  isMatched
                    ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                    : 'bg-slate-950/70 text-slate-300 border-slate-800'
                }`}
              >
                {isMatched && <Check className="w-2.5 h-2.5 text-emerald-400" />}
                {skill}
              </span>
            );
          })}
          {job.skills.length > 5 && (
            <span className="text-[11px] text-slate-500 self-center pl-1">
              +{job.skills.length - 5} more
            </span>
          )}
        </div>
      </div>

      {/* Bottom actions */}
      <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between gap-2">
        {match ? (
          <Link
            to={`/jobs/${job.id}/match`}
            className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Why this matches ({match.overall_match}%)</span>
          </Link>
        ) : (
          <span className="text-xs text-slate-500 font-medium">{job.category}</span>
        )}

        <Link
          to={`/jobs/${job.id}`}
          className="inline-flex items-center gap-1 text-xs font-semibold text-slate-300 hover:text-white px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 transition-colors"
        >
          <span>View Details</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
};
