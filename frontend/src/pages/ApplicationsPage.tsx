import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Application } from '../types';
import {
  Send,
  Building2,
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';

const STATUS_CONFIG: Record<
  string,
  { label: string; color: string; bgColor: string; icon: React.FC<any> }
> = {
  applied: {
    label: 'Applied',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10 border-blue-500/30',
    icon: Clock,
  },
  interview: {
    label: 'Interview',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10 border-purple-500/30',
    icon: CheckCircle2,
  },
  selected: {
    label: 'Selected',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10 border-emerald-500/30',
    icon: CheckCircle2,
  },
  rejected: {
    label: 'Rejected',
    color: 'text-rose-400',
    bgColor: 'bg-rose-500/10 border-rose-500/30',
    icon: XCircle,
  },
};

export const ApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  const loadApplications = async () => {
    setIsLoading(true);
    try {
      const data = await api.getApplications();
      setApplications(data);
    } catch (err) {
      console.error('Failed to load applications:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadApplications();
  }, []);

  const handleUpdateStatus = async (id: number, newStatus: string) => {
    try {
      await api.updateApplicationStatus(id, newStatus);
      setApplications((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: newStatus as any } : a))
      );
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const filteredApps =
    statusFilter === 'all'
      ? applications
      : applications.filter((a) => a.status === statusFilter);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-brand-400 mb-1">
            <Send className="w-3.5 h-3.5" />
            <span>Recruitment Pipeline</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">Application Tracker</h1>
          <p className="text-xs text-slate-400 mt-1">
            Track and manage your submitted applications and interview progression.
          </p>
        </div>

        {/* Status filter tabs */}
        <div className="flex flex-wrap items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-2xl">
          {['all', 'applied', 'interview', 'selected', 'rejected'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize transition-colors ${
                statusFilter === st
                  ? 'bg-slate-800 text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((n) => (
            <div key={n} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 h-24 animate-pulse" />
          ))}
        </div>
      ) : filteredApps.length > 0 ? (
        <div className="space-y-3">
          {filteredApps.map((app) => {
            const config = STATUS_CONFIG[app.status] || STATUS_CONFIG.applied;
            const Icon = config.icon;
            const appliedDate = new Date(app.applied_at).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            });

            return (
              <div
                key={app.id}
                className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 transition-colors hover:border-slate-700/80"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-400 flex items-center gap-1">
                      <Building2 className="w-3.5 h-3.5 text-slate-500" />
                      {app.job.company}
                    </span>
                    <span className="text-xs text-slate-600">&bull;</span>
                    <span className="text-xs text-slate-400">{app.job.location}</span>
                  </div>

                  <Link to={`/jobs/${app.job.id}`} className="hover:text-brand-400 transition-colors block">
                    <h3 className="text-base font-bold text-white">{app.job.title}</h3>
                  </Link>

                  <div className="flex items-center gap-2 text-[11px] text-slate-500">
                    <Calendar className="w-3 h-3" />
                    <span>Applied on {appliedDate}</span>
                    {app.notes && (
                      <>
                        <span>&bull;</span>
                        <span className="truncate max-w-xs text-slate-400">Note: "{app.notes}"</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  {/* Status Dropdown */}
                  <select
                    value={app.status}
                    onChange={(e) => handleUpdateStatus(app.id, e.target.value)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold border capitalize focus:outline-none ${config.bgColor} ${config.color}`}
                  >
                    <option value="applied" className="bg-slate-900 text-slate-200">Applied</option>
                    <option value="interview" className="bg-slate-900 text-slate-200">Interview</option>
                    <option value="selected" className="bg-slate-900 text-slate-200">Selected</option>
                    <option value="rejected" className="bg-slate-900 text-slate-200">Rejected</option>
                  </select>

                  <Link
                    to={`/jobs/${app.job.id}`}
                    className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-white"
                    title="View role details"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16 bg-slate-900/60 rounded-3xl border border-slate-800">
          <Send className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">No applications</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-4">
            Your application activity will appear here.
          </p>
          <Link
            to="/jobs"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-colors shadow-md shadow-brand-500/20"
          >
            <span>Explore Opportunities</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}
    </div>
  );
};
