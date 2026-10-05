import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { JobRecommendationItem, UserProfile, SkillGapResponse } from '../types';
import { JobCard } from '../components/JobCard';
import { MatchBreakdownCard } from '../components/MatchBreakdownCard';
import { SkillGapCard } from '../components/SkillGapCard';
import {
  Sparkles,
  Bookmark,
  Send,
  UserCheck,
  TrendingUp,
  Search,
  ArrowRight,
  FileText,
  Clock,
  Briefcase,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [recommendations, setRecommendations] = useState<JobRecommendationItem[]>([]);
  const [skillGap, setSkillGap] = useState<SkillGapResponse | null>(null);
  const [savedCount, setSavedCount] = useState<number>(0);
  const [appliedCount, setAppliedCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedMatch, setSelectedMatch] = useState<JobRecommendationItem | null>(null);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [profData, recData, gapData, savedData, appsData] = await Promise.all([
        api.getProfile(),
        api.getRecommendations({ limit: 8 }),
        api.getSkillGap(),
        api.getSavedJobs(),
        api.getApplications(),
      ]);

      setProfile(profData);
      setRecommendations(recData.items);
      if (recData.items.length > 0) {
        setSelectedMatch(recData.items[0]);
      }
      setSkillGap(gapData);
      setSavedCount(savedData.total || savedData.items.length);
      setAppliedCount(appsData.length);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Greeting Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-brand-400 mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Career Intelligence Hub</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            {getGreeting()}, {user?.full_name?.split(' ')[0] || 'Candidate'}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            <span className="font-semibold text-brand-300">{recommendations.length} curated opportunities</span> match your profile based on semantic vector proximity and skill overlap.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            to="/jobs"
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 flex items-center gap-1.5 transition-colors"
          >
            <Search className="w-3.5 h-3.5" />
            <span>Browse All 300+ Jobs</span>
          </Link>
          <Link
            to="/resume-intelligence"
            className="px-4 py-2 rounded-xl text-xs font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 flex items-center gap-1.5 transition-colors shadow-lg shadow-brand-500/20"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Resume Intelligence</span>
          </Link>
        </div>
      </div>

      {/* 4 Metric Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">Recommended</span>
            <div className="p-1.5 rounded-lg bg-brand-500/10 text-brand-400">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">{recommendations.length}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Top-ranked opportunities</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">Saved Opportunities</span>
            <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
              <Bookmark className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">{savedCount}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Bookmarked roles</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">Applications</span>
            <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400">
              <Send className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">{appliedCount}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">In recruitment pipeline</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">Profile Readiness</span>
            <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <UserCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">{profile?.profile_completeness || 0}%</div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
            <div
              className="h-full bg-brand-500 rounded-full"
              style={{ width: `${profile?.profile_completeness || 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Featured Match Highlight & Breakdown */}
      {selectedMatch && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-brand-400" />
              <span>Highest Compatibility Recommendation</span>
            </h2>
            <Link
              to={`/jobs/${selectedMatch.job.id}`}
              className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1"
            >
              <span>View Full Role</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <MatchBreakdownCard match={selectedMatch.match} />
        </div>
      )}

      {/* Top Matches Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Top Recommended Matches</h2>
            <p className="text-xs text-slate-400">Ranked by JobTrail-AI's hybrid ML recommendation algorithm</p>
          </div>
          <Link
            to="/jobs"
            className="text-xs font-semibold text-slate-400 hover:text-white flex items-center gap-1"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((n) => (
              <div key={n} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 h-48 animate-pulse" />
            ))}
          </div>
        ) : recommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.slice(0, 6).map((rec) => (
              <JobCard
                key={rec.job.id}
                job={rec.job}
                match={rec.match}
                onSavedChange={(saved) => setSavedCount((prev) => (saved ? prev + 1 : Math.max(0, prev - 1)))}
              />
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-slate-900 rounded-2xl border border-slate-800">
            <p className="text-xs text-slate-400">Complete your profile or upload a resume to generate recommendations.</p>
          </div>
        )}
      </div>

      {/* Skill Gap Analysis Preview */}
      {skillGap && (
        <div className="space-y-3">
          <SkillGapCard data={skillGap} />
        </div>
      )}
    </div>
  );
};
