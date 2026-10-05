import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Compass,
  Briefcase,
  Sparkles,
  FileText,
  Bookmark,
  CheckCircle,
  TrendingUp,
  LogOut,
  User,
  PlusCircle,
  Users,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout, isAuthenticated, isRecruiter } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to={isAuthenticated ? (isRecruiter ? '/recruiter' : '/dashboard') : '/'} className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-400 flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Compass className="w-5 h-5 text-slate-950" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-lg tracking-tight text-white">JobTrail<span className="text-brand-400">-AI</span></span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/30">
                  ML
                </span>
              </div>
            </div>
          </Link>

          {/* Navigation Links */}
          {isAuthenticated ? (
            <div className="hidden md:flex items-center gap-1">
              {!isRecruiter ? (
                <>
                  <Link
                    to="/dashboard"
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive('/dashboard')
                        ? 'bg-slate-800 text-white'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/jobs"
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                      isActive('/jobs')
                        ? 'bg-slate-800 text-white'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    <Briefcase className="w-4 h-4 text-slate-400" />
                    Jobs
                  </Link>
                  <Link
                    to="/resume-intelligence"
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                      isActive('/resume-intelligence')
                        ? 'bg-slate-800 text-white'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    <FileText className="w-4 h-4 text-slate-400" />
                    Resume AI
                  </Link>
                  <Link
                    to="/saved"
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                      isActive('/saved')
                        ? 'bg-slate-800 text-white'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    <Bookmark className="w-4 h-4 text-slate-400" />
                    Saved
                  </Link>
                  <Link
                    to="/applications"
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                      isActive('/applications')
                        ? 'bg-slate-800 text-white'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    <CheckCircle className="w-4 h-4 text-slate-400" />
                    Applications
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    to="/recruiter"
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive('/recruiter') && location.pathname === '/recruiter'
                        ? 'bg-slate-800 text-white'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    Recruiter Hub
                  </Link>
                  <Link
                    to="/recruiter/jobs/new"
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                      isActive('/recruiter/jobs/new')
                        ? 'bg-slate-800 text-white'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    <PlusCircle className="w-4 h-4 text-brand-400" />
                    Post Opportunity
                  </Link>
                </>
              )}
            </div>
          ) : (
            <div className="hidden md:flex items-center gap-6">
              <Link to="/#features" className="text-sm text-slate-300 hover:text-white transition-colors">
                How It Works
              </Link>
              <Link to="/#matching" className="text-sm text-slate-300 hover:text-white transition-colors">
                Explainable Matching
              </Link>
              <Link to="/#demo" className="text-sm text-slate-300 hover:text-white transition-colors">
                ML Pipeline
              </Link>
            </div>
          )}

          {/* Right Action Buttons */}
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <Link
                  to="/profile"
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors"
                >
                  <div className="w-6 h-6 rounded-full bg-brand-500/20 border border-brand-500/40 text-brand-300 flex items-center justify-center text-xs font-bold">
                    {user?.full_name?.charAt(0) || 'U'}
                  </div>
                  <span className="text-xs font-medium text-slate-200 hidden sm:inline">{user?.full_name}</span>
                  <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {user?.role}
                  </span>
                </Link>

                <button
                  onClick={handleLogout}
                  title="Logout"
                  className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-slate-900 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2.5">
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-xl text-sm font-medium text-slate-200 hover:text-white hover:bg-slate-900 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-xl text-sm font-semibold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-colors shadow-lg shadow-brand-500/20"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
