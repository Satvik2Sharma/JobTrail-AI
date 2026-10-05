import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Job, CandidateRankingItem } from '../types';
import { MatchBadge } from '../components/MatchBadge';
import { MatchBreakdownCard } from '../components/MatchBreakdownCard';
import {
  Users,
  ArrowLeft,
  Sparkles,
  Building2,
  Mail,
  GraduationCap,
  Briefcase,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export const RecruiterCandidateRankPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [candidates, setCandidates] = useState<CandidateRankingItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedCandidateId, setExpandedCandidateId] = useState<number | null>(null);

  const jobId = parseInt(id || '0');

  useEffect(() => {
    if (!jobId) return;

    const loadData = async () => {
      setIsLoading(true);
      try {
        const [jobData, rankedData] = await Promise.all([
          api.getJob(jobId),
          api.rankCandidates(jobId),
        ]);
        setJob(jobData);
        setCandidates(rankedData);
        if (rankedData.length > 0) {
          setExpandedCandidateId(rankedData[0].candidate_id);
        }
      } catch (err) {
        console.error('Failed to load candidate rankings:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [jobId]);

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center">
        <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-xs text-slate-400">
          Running explainable ML matching engine to rank all applicants and candidates...
        </p>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center">
        <h2 className="text-lg font-bold text-white mb-2">Job Not Found</h2>
        <Link to="/recruiter" className="text-xs text-brand-400 font-semibold hover:underline">
          Return to recruiter portal
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <Link
          to="/recruiter"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Recruiter Hub</span>
        </Link>
      </div>

      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-purple-400 mb-1">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Explainable Candidate Ranking Engine</span>
        </div>
        <h1 className="text-2xl font-extrabold text-white mb-2">
          Ranked Candidates for: {job.title}
        </h1>
        <p className="text-xs text-slate-400 flex items-center gap-2">
          <Building2 className="w-3.5 h-3.5 text-slate-500" />
          <span>{job.company}</span>
          <span>&bull;</span>
          <span>{job.location}</span>
          <span>&bull;</span>
          <span>{candidates.length} candidate profiles evaluated</span>
        </p>
      </div>

      {/* Candidates Ranking List */}
      <div className="space-y-4">
        {candidates.map((cand, idx) => {
          const isExpanded = expandedCandidateId === cand.candidate_id;

          return (
            <div
              key={cand.candidate_id}
              className="bg-slate-900 border border-slate-800 rounded-3xl p-6 transition-all duration-200"
            >
              {/* Top candidate summary bar */}
              <div
                onClick={() => setExpandedCandidateId(isExpanded ? null : cand.candidate_id)}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer select-none"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-brand-600 to-emerald-400 flex items-center justify-center text-slate-950 font-black text-sm shrink-0">
                    #{idx + 1}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-base font-bold text-white">{cand.candidate_name}</h3>
                      <span className="text-[11px] text-slate-500 flex items-center gap-1">
                        <Mail className="w-3 h-3" />
                        {cand.candidate_email}
                      </span>
                    </div>

                    <div className="flex items-center gap-3 text-xs text-slate-400 mt-0.5">
                      <span className="flex items-center gap-1">
                        <GraduationCap className="w-3.5 h-3.5 text-slate-500" />
                        {cand.degree || 'Degree unspecified'}
                      </span>
                      <span>&bull;</span>
                      <span className="flex items-center gap-1">
                        <Briefcase className="w-3.5 h-3.5 text-slate-500" />
                        {cand.experience_years} yrs exp
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4 self-end sm:self-center">
                  <MatchBadge score={cand.match.overall_match} size="md" />
                  <button className="text-slate-400 hover:text-white p-1">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Expanded Match Breakdown */}
              {isExpanded && (
                <div className="mt-6 pt-6 border-t border-slate-800">
                  <MatchBreakdownCard match={cand.match} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
