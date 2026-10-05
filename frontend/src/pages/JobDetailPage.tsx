import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Job, ExplainableMatch } from '../types';
import { MatchBreakdownCard } from '../components/MatchBreakdownCard';
import { MatchBadge } from '../components/MatchBadge';
import {
  Building2,
  MapPin,
  Briefcase,
  Bookmark,
  Send,
  ExternalLink,
  ArrowLeft,
  DollarSign,
  GraduationCap,
  Sparkles,
  CheckCircle,
  Share2,
} from 'lucide-react';

export const JobDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [match, setMatch] = useState<ExplainableMatch | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [hasApplied, setHasApplied] = useState(false);
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [applyNotes, setApplyNotes] = useState('');
  const [isApplying, setIsApplying] = useState(false);
  const [applySuccessMessage, setApplySuccessMessage] = useState<string | null>(null);

  const jobId = parseInt(id || '0');

  useEffect(() => {
    if (!jobId) return;

    const loadData = async () => {
      setIsLoading(true);
      try {
        const [jobData, matchData] = await Promise.allSettled([
          api.getJob(jobId),
          api.getJobMatch(jobId),
        ]);

        if (jobData.status === 'fulfilled') {
          setJob(jobData.value);
          setIsSaved(jobData.value.is_saved);
          setHasApplied(jobData.value.has_applied);
        }

        if (matchData.status === 'fulfilled') {
          setMatch(matchData.value);
        }
      } catch (err) {
        console.error('Failed to load job details:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [jobId]);

  const handleToggleSave = async () => {
    if (!job) return;
    try {
      if (isSaved) {
        await api.unsaveJob(job.id);
        setIsSaved(false);
      } else {
        await api.saveJob(job.id);
        setIsSaved(true);
      }
    } catch (err) {
      console.error('Failed to toggle save:', err);
    }
  };

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!job) return;
    setIsApplying(true);
    try {
      await api.applyToJob(job.id, applyNotes);
      setHasApplied(true);
      setIsApplyModalOpen(false);
      setApplySuccessMessage('Application submitted successfully! Tracked in your pipeline.');
    } catch (err: any) {
      alert(err.message || 'Failed to submit application.');
    } finally {
      setIsApplying(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center">
        <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-xs text-slate-400">Loading opportunity & calculating compatibility matrix...</p>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center">
        <h2 className="text-lg font-bold text-white mb-2">Job Not Found</h2>
        <p className="text-xs text-slate-400 mb-4">The opportunity you are looking for does not exist or has been closed.</p>
        <Link to="/jobs" className="text-xs text-brand-400 font-semibold hover:underline">
          Return to jobs listing
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back button */}
      <div>
        <Link
          to="/jobs"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Opportunities</span>
        </Link>
      </div>

      {applySuccessMessage && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>{applySuccessMessage}</span>
          </div>
          <Link to="/applications" className="font-bold underline hover:text-emerald-300">
            View Applications Pipeline
          </Link>
        </div>
      )}

      {/* Hero Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8">
        <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
              <Building2 className="w-4 h-4 text-brand-400" />
              <span className="text-slate-200 text-sm font-bold">{job.company}</span>
              {job.remote && (
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Remote Opportunity
                </span>
              )}
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {job.title}
            </h1>

            <div className="flex flex-wrap items-center gap-y-2 gap-x-4 text-xs text-slate-400">
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4 text-slate-500" />
                {job.location}
              </span>
              <span className="flex items-center gap-1">
                <Briefcase className="w-4 h-4 text-slate-500" />
                {job.employment_type} ({job.experience_level})
              </span>
              {job.salary_min && (
                <span className="flex items-center gap-1 text-slate-200 font-semibold">
                  <DollarSign className="w-4 h-4 text-emerald-400" />
                  ${job.salary_min.toLocaleString()} - ${job.salary_max?.toLocaleString()} / yr
                </span>
              )}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleToggleSave}
              className={`p-3 rounded-2xl border transition-colors ${
                isSaved
                  ? 'bg-brand-500/10 border-brand-500/30 text-brand-400'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
              }`}
              title={isSaved ? 'Unsave' : 'Save'}
            >
              <Bookmark className={`w-5 h-5 ${isSaved ? 'fill-brand-400' : ''}`} />
            </button>

            {hasApplied ? (
              <div className="px-5 py-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4" />
                <span>Applied</span>
              </div>
            ) : (
              <button
                onClick={() => setIsApplyModalOpen(true)}
                className="px-6 py-3 rounded-2xl font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 text-xs transition-colors shadow-lg shadow-brand-500/20 flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                <span>Apply Now</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Prominent Match Analysis Section */}
      {match && (
        <div className="space-y-3">
          <MatchBreakdownCard match={match} />
        </div>
      )}

      {/* Job Details Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Description, Responsibilities, Requirements */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-base font-bold text-white">About the Position</h2>
            <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
              {job.description}
            </p>
          </div>

          {job.responsibilities && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
              <h2 className="text-base font-bold text-white">Key Responsibilities</h2>
              <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
                {job.responsibilities}
              </div>
            </div>
          )}

          {job.requirements && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
              <h2 className="text-base font-bold text-white">Eligibility & Requirements</h2>
              <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
                {job.requirements}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Skills, Education requirement, and Meta */}
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-sm font-bold text-white">Required Technical Skills</h3>
            <div className="flex flex-wrap gap-1.5">
              {job.skills.map((s, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-950 text-slate-300 border border-slate-800"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>

          {job.education_requirement && (
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-2">
              <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
                <GraduationCap className="w-4 h-4 text-amber-400" />
                <span>Education Requirement</span>
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                {job.education_requirement}
              </p>
            </div>
          )}

          {/* Quick Apply CTA Box */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-brand-950/40 to-slate-900 border border-brand-500/20 text-center space-y-3">
            <Sparkles className="w-6 h-6 text-brand-400 mx-auto" />
            <h4 className="text-xs font-bold text-white">Interested in this role?</h4>
            <p className="text-[11px] text-slate-400">
              Submit your candidate profile directly into the application tracking system.
            </p>
            <button
              onClick={() => setIsApplyModalOpen(true)}
              disabled={hasApplied}
              className="w-full py-2.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 disabled:opacity-60 text-slate-950 text-xs transition-colors shadow-md shadow-brand-500/20"
            >
              {hasApplied ? 'Already Applied' : 'Submit Application'}
            </button>
          </div>
        </div>
      </div>

      {/* Apply Modal */}
      {isApplyModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-1">Apply to {job.title}</h3>
            <p className="text-xs text-slate-400 mb-4">{job.company} &bull; {job.location}</p>

            <form onSubmit={handleApply} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Cover Note / Pitch (Optional)
                </label>
                <textarea
                  rows={4}
                  value={applyNotes}
                  onChange={(e) => setApplyNotes(e.target.value)}
                  placeholder="Share a short note about your relevant technical projects or interests..."
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
                />
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] text-slate-400">
                Your extracted candidate profile, detected skills ({match?.matching_skills.length || 0} matched), and education will be automatically included.
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsApplyModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isApplying}
                  className="px-5 py-2.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 disabled:opacity-60 text-slate-950 text-xs transition-colors flex items-center gap-1.5"
                >
                  {isApplying ? 'Submitting...' : 'Confirm Application'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
