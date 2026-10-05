import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Job, ExplainableMatch, SkillGapResponse } from '../types';
import { MatchBreakdownCard } from '../components/MatchBreakdownCard';
import { SkillGapCard } from '../components/SkillGapCard';
import {
  ArrowLeft,
  Sparkles,
  Building2,
  ExternalLink,
  Send,
  Bookmark,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';

export const JobMatchAnalysisPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [match, setMatch] = useState<ExplainableMatch | null>(null);
  const [skillGap, setSkillGap] = useState<SkillGapResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const jobId = parseInt(id || '0');

  useEffect(() => {
    if (!jobId) return;

    const loadData = async () => {
      setIsLoading(true);
      try {
        const [jobData, matchData, gapData] = await Promise.all([
          api.getJob(jobId),
          api.getJobMatch(jobId),
          api.getSkillGap(jobId),
        ]);
        setJob(jobData);
        setMatch(matchData);
        setSkillGap(gapData);
      } catch (err) {
        console.error('Failed to load match analysis:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [jobId]);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-xs text-slate-400">Computing multidimensional match vectors and skill taxonomy overlaps...</p>
      </div>
    );
  }

  if (!job || !match) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center">
        <h2 className="text-lg font-bold text-white mb-2">Match Analysis Unavailable</h2>
        <p className="text-xs text-slate-400 mb-4">Could not calculate match analysis for this role.</p>
        <Link to="/jobs" className="text-xs text-brand-400 font-semibold hover:underline">
          Return to jobs
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top navigation */}
      <div className="flex items-center justify-between">
        <Link
          to={`/jobs/${job.id}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Job Details</span>
        </Link>
        <div className="flex items-center gap-2">
          <Link
            to={`/jobs/${job.id}`}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-colors shadow-md shadow-brand-500/20"
          >
            Apply to Role
          </Link>
        </div>
      </div>

      {/* Title Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-brand-400 mb-1">
          <Sparkles className="w-4 h-4" />
          <span>Explainable Career Matching Engine</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white mb-2">
          Match Analysis: {job.title}
        </h1>
        <p className="text-xs text-slate-400 flex items-center gap-2">
          <Building2 className="w-3.5 h-3.5 text-slate-500" />
          <span>{job.company}</span>
          <span>&bull;</span>
          <span>{job.location}</span>
          <span>&bull;</span>
          <span>{job.employment_type}</span>
        </p>
      </div>

      {/* Central Compatibility Breakdown */}
      <MatchBreakdownCard match={match} />

      {/* Targeted Skill Gap for this role */}
      {skillGap && (
        <div className="space-y-3">
          <SkillGapCard data={skillGap} />
        </div>
      )}
    </div>
  );
};
