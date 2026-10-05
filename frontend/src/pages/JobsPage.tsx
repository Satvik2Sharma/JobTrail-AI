import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Job, ExplainableMatch } from '../types';
import { JobCard } from '../components/JobCard';
import {
  Search,
  Filter,
  Sparkles,
  MapPin,
  Briefcase,
  ChevronLeft,
  ChevronRight,
  SlidersHorizontal,
  X,
} from 'lucide-react';

const CATEGORIES = [
  'All',
  'AI/ML',
  'Data Science & Analytics',
  'Backend Development',
  'Frontend Development',
  'Full Stack',
  'Cloud & DevOps',
  'Cybersecurity',
  'Mobile Development',
  'Software Engineering & Systems',
];

const EXPERIENCE_LEVELS = [
  'All',
  '0-1 years',
  '1-2 years',
  '0-2 years',
];

export const JobsPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSemanticMode, setIsSemanticMode] = useState(true);
  const [category, setCategory] = useState('All');
  const [remoteOnly, setRemoteOnly] = useState<boolean | undefined>(undefined);
  const [experienceLevel, setExperienceLevel] = useState('All');
  const [locationFilter, setLocationFilter] = useState('');

  const [jobs, setJobs] = useState<Job[]>([]);
  const [semanticMatches, setSemanticMatches] = useState<Record<number, ExplainableMatch>>({});
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalJobs, setTotalJobs] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const fetchJobs = async () => {
    setIsLoading(true);
    try {
      if (isSemanticMode && searchQuery.trim().length >= 3) {
        // Natural language semantic search
        const res = await api.semanticSearch(
          searchQuery,
          category !== 'All' ? category : undefined,
          remoteOnly,
          20
        );
        const mappedJobs = res.items.map((it) => it.job);
        setJobs(mappedJobs);
        setTotalJobs(res.total_matches);
        setTotalPages(1);

        // Fetch match explanations for top results
        const matchesMap: Record<number, ExplainableMatch> = {};
        for (const it of res.items.slice(0, 5)) {
          try {
            const m = await api.getJobMatch(it.job.id);
            matchesMap[it.job.id] = m;
          } catch (_) {}
        }
        setSemanticMatches(matchesMap);
      } else {
        // Standard listing with keyword & filters
        const res = await api.listJobs({
          page,
          page_size: 15,
          category: category !== 'All' ? category : undefined,
          remote: remoteOnly,
          experience_level: experienceLevel !== 'All' ? experienceLevel : undefined,
          location: locationFilter || undefined,
          keyword: searchQuery.trim() || undefined,
        });

        setJobs(res.items);
        setTotalJobs(res.total);
        setTotalPages(res.total_pages);

        // Fetch recommendation matches for user if available
        try {
          const recRes = await api.getRecommendations({ limit: 30 });
          const matchesMap: Record<number, ExplainableMatch> = {};
          recRes.items.forEach((item) => {
            matchesMap[item.job.id] = item.match;
          });
          setSemanticMatches(matchesMap);
        } catch (_) {}
      }
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [page, category, remoteOnly, experienceLevel]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchJobs();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header & Search Bar */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white mb-1">
          Explore Opportunities
        </h1>
        <p className="text-xs text-slate-400 mb-6">
          Search over 300+ realistic prototype tech jobs using natural language semantic queries or keywords.
        </p>

        {/* Search Input Box */}
        <form onSubmit={handleSearchSubmit} className="relative mb-4">
          <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl focus-within:border-brand-500/80 transition-colors">
            <div className="pl-3 text-slate-500">
              {isSemanticMode ? (
                <Sparkles className="w-5 h-5 text-brand-400" />
              ) : (
                <Search className="w-5 h-5" />
              )}
            </div>

            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={
                isSemanticMode
                  ? 'Try natural language: "machine learning internship for python student with no experience"...'
                  : 'Search by title, company, or keyword...'
              }
              className="flex-1 bg-transparent px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none"
            />

            {searchQuery && (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery('');
                  setPage(1);
                }}
                className="p-1.5 text-slate-500 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}

            <button
              type="button"
              onClick={() => setIsSemanticMode(!isSemanticMode)}
              className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-colors ${
                isSemanticMode
                  ? 'bg-brand-500/10 text-brand-300 border-brand-500/30'
                  : 'bg-slate-800 text-slate-400 border-slate-700'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Semantic AI Search</span>
            </button>

            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 text-xs transition-colors shadow-md shadow-brand-500/20"
            >
              Search
            </button>
          </div>
        </form>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1 pb-2 overflow-x-auto">
          <span className="text-xs font-semibold text-slate-400 flex items-center gap-1 pr-1">
            <SlidersHorizontal className="w-3.5 h-3.5" />
            Category:
          </span>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => {
                setCategory(cat);
                setPage(1);
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-colors whitespace-nowrap ${
                category === cat
                  ? 'bg-brand-500/20 text-brand-300 border-brand-500/40'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Secondary Filters Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-800/80 text-xs text-slate-400">
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => {
                setRemoteOnly(remoteOnly ? undefined : true);
                setPage(1);
              }}
              className={`px-3 py-1 rounded-lg border font-medium transition-colors ${
                remoteOnly
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              Remote Only
            </button>

            <div className="flex items-center gap-1.5">
              <span>Experience:</span>
              <select
                value={experienceLevel}
                onChange={(e) => {
                  setExperienceLevel(e.target.value);
                  setPage(1);
                }}
                className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-300 focus:outline-none"
              >
                {EXPERIENCE_LEVELS.map((lvl) => (
                  <option key={lvl} value={lvl}>
                    {lvl}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            Showing <span className="font-semibold text-white">{jobs.length}</span> of {totalJobs} opportunities
          </div>
        </div>
      </div>

      {/* Jobs Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 h-56 animate-pulse" />
          ))}
        </div>
      ) : jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              match={semanticMatches[job.id]}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-slate-900/60 rounded-3xl border border-slate-800">
          <Briefcase className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">No matching opportunities found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-4">
            Try adjusting your search criteria, switching between Semantic AI and keyword mode, or clearing active filters.
          </p>
          <button
            onClick={() => {
              setSearchQuery('');
              setCategory('All');
              setRemoteOnly(undefined);
              setExperienceLevel('All');
              setPage(1);
            }}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-white transition-colors"
          >
            Reset Filters
          </button>
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-6 border-t border-slate-800 text-xs">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-40 flex items-center gap-1 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>

          <span className="text-slate-400">
            Page <span className="text-white font-semibold">{page}</span> of {totalPages}
          </span>

          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-40 flex items-center gap-1 transition-colors"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};
