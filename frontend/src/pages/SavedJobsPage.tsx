import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Job } from '../types';
import { JobCard } from '../components/JobCard';
import { Bookmark, ArrowRight, Briefcase } from 'lucide-react';

export const SavedJobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadSavedJobs = async () => {
    setIsLoading(true);
    try {
      const res = await api.getSavedJobs();
      setJobs(res.items || []);
    } catch (err) {
      console.error('Failed to load saved jobs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSavedJobs();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center justify-between pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-brand-400 mb-1">
            <Bookmark className="w-3.5 h-3.5" />
            <span>Saved Bookmarks</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">Saved Opportunities</h1>
          <p className="text-xs text-slate-400 mt-1">
            {jobs.length} bookmarked opportunities saved for later application.
          </p>
        </div>

        <Link
          to="/jobs"
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 flex items-center gap-1.5 transition-colors"
        >
          <Briefcase className="w-3.5 h-3.5" />
          <span>Explore More Roles</span>
        </Link>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 h-48 animate-pulse" />
          ))}
        </div>
      ) : jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onSavedChange={() => loadSavedJobs()}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-slate-900/60 rounded-3xl border border-slate-800">
          <Bookmark className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">No saved jobs</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-4">
            Save opportunities here so you can return to them later.
          </p>
          <Link
            to="/jobs"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-colors shadow-md shadow-brand-500/20"
          >
            <span>Browse Opportunities</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}
    </div>
  );
};
