import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Job } from '../types';
import {
  Briefcase,
  PlusCircle,
  Users,
  Building2,
  Calendar,
  Sparkles,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';

export const RecruiterPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadRecruiterJobs = async () => {
    setIsLoading(true);
    try {
      const data = await api.getRecruiterJobs();
      setJobs(data);
    } catch (err) {
      console.error('Failed to load recruiter jobs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRecruiterJobs();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-purple-400 mb-1">
            <Briefcase className="w-3.5 h-3.5" />
            <span>Recruiter Portal</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">Talent Management Hub</h1>
          <p className="text-xs text-slate-400 mt-1">
            Create job postings, define skill requirements, and evaluate candidates using the ML matching engine.
          </p>
        </div>

        <Link
          to="/recruiter/jobs/new"
          className="px-5 py-2.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 text-xs flex items-center gap-1.5 transition-colors shadow-lg shadow-brand-500/20"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Post New Opportunity</span>
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2].map((n) => (
            <div key={n} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 h-28 animate-pulse" />
          ))}
        </div>
      ) : jobs.length > 0 ? (
        <div className="space-y-3">
          {jobs.map((j) => (
            <div
              key={j.id}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-1.5">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="font-semibold text-slate-200">{j.company}</span>
                  <span>&bull;</span>
                  <span>{j.location}</span>
                  <span>&bull;</span>
                  <span className="text-brand-400 font-medium">{j.category}</span>
                </div>

                <h3 className="text-base font-bold text-white">{j.title}</h3>

                <div className="flex flex-wrap gap-1.5">
                  {j.skills.slice(0, 5).map((s, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-slate-950 text-slate-300 border border-slate-800"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Link
                  to={`/recruiter/jobs/${j.id}/candidates`}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-1.5 transition-colors"
                >
                  <Users className="w-4 h-4" />
                  <span>Rank Candidates</span>
                </Link>

                <Link
                  to={`/jobs/${j.id}`}
                  className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-white"
                  title="View Public Listing"
                >
                  <ExternalLink className="w-4 h-4" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-slate-900/60 rounded-3xl border border-slate-800">
          <Briefcase className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">No postings yet</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-4">
            Publish your first job opening to automatically rank applicant candidates with our ML pipeline.
          </p>
          <Link
            to="/recruiter/jobs/new"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-colors shadow-md shadow-brand-500/20"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Post First Opportunity</span>
          </Link>
        </div>
      )}
    </div>
  );
};
