import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Brain,
  Check,
  Circle,
  TrendingUp,
  ArrowRight,
  ShieldCheck,
  ChevronRight,
  Award,
  GraduationCap,
  MapPin,
  HelpCircle,
  Cpu,
  BookOpen,
} from 'lucide-react';
import { MatchBadge } from '../components/MatchBadge';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Hero Section */}
      <section className="relative pt-20 pb-20 overflow-hidden border-b border-slate-900">
        {/* Subtle background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-brand-500/10 blur-[120px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-semibold text-brand-400 mb-6 shadow-sm">
              <Sparkles className="w-3.5 h-3.5" />
              <span>JobTrail-AI &bull; Explainable Recommendation Architecture</span>
            </div>

            <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-white mb-3 leading-tight">
              JobTrail<span className="text-brand-400">-AI</span>
            </h1>

            <h2 className="text-lg sm:text-2xl font-bold text-slate-200 mb-5">
              Explainable AI-Powered Job &amp; Internship Recommendation Platform
            </h2>

            <blockquote className="text-base sm:text-xl font-medium text-brand-300 italic mb-6 max-w-2xl mx-auto border-l-2 border-brand-500/50 pl-4 py-1 bg-brand-500/5 rounded-r-xl">
              &ldquo;Discover opportunities that match your profile &mdash; and understand exactly why.&rdquo;
            </blockquote>

            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed max-w-2xl mx-auto mb-8">
              No black-box algorithms or keyword guesswork. JobTrail-AI models candidate profile representations with Sentence Transformers (<code className="text-slate-300">all-MiniLM-L6-v2</code>), normalizes skills against a 107-canonical taxonomy, and delivers mathematical explainability across every opportunity.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                to="/register"
                className="w-full sm:w-auto px-6 py-3.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-all shadow-lg shadow-brand-500/25 flex items-center justify-center gap-2 text-xs sm:text-sm"
              >
                <span>Get Recommended</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/how-it-works"
                className="w-full sm:w-auto px-6 py-3.5 rounded-xl font-semibold bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 transition-colors flex items-center justify-center gap-2 text-xs sm:text-sm"
              >
                <BookOpen className="w-4 h-4 text-brand-400" />
                <span>How It Works</span>
              </Link>
              <Link
                to="/login"
                className="w-full sm:w-auto px-5 py-3.5 rounded-xl font-semibold text-slate-400 hover:text-white transition-colors flex items-center justify-center gap-1.5 text-xs sm:text-sm"
              >
                <span>Demo Sign In</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Interactive Match Engine Showcase Mockup */}
          <div className="max-w-4xl mx-auto bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl backdrop-blur-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-800/80 gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-brand-400">Live Demonstration Preview</span>
                <h3 className="text-xl font-bold text-white">Machine Learning Engineer Intern</h3>
                <p className="text-xs text-slate-400">TechNova Solutions &bull; Remote &bull; $55,000 - $80,000</p>
              </div>
              <div className="flex items-center gap-3 self-start sm:self-center">
                <MatchBadge score={94} size="lg" />
              </div>
            </div>

            {/* Prominent Overall Match Hero */}
            <div className="text-center py-5 px-4 bg-slate-950/80 border border-slate-800/90 rounded-2xl my-6 shadow-inner">
              <div className="text-5xl sm:text-6xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-brand-400 via-emerald-300 to-teal-200">
                94%
              </div>
              <div className="text-sm font-bold uppercase tracking-widest text-slate-200 mt-1">
                Overall Match
              </div>
              <div className="text-xs text-slate-400 mt-1">
                50% Semantic &bull; 25% Skills &bull; 15% Eligibility &bull; 10% Preferences
              </div>
            </div>

            {/* 4 Score Progress Bars */}
            <div className="space-y-3 mb-6">
              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <div className="flex justify-between items-center mb-1 text-xs">
                  <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                    <Brain className="w-3.5 h-3.5 text-blue-400" />
                    <span>Semantic Match</span>
                    <span className="text-[10px] text-slate-500 font-mono">(50% weight)</span>
                  </span>
                  <span className="font-mono font-bold text-white">92%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500" style={{ width: '92%' }} />
                </div>
              </div>

              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <div className="flex justify-between items-center mb-1 text-xs">
                  <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Skill Match</span>
                    <span className="text-[10px] text-slate-500 font-mono">(25% weight)</span>
                  </span>
                  <span className="font-mono font-bold text-white">96%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-500" style={{ width: '96%' }} />
                </div>
              </div>

              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <div className="flex justify-between items-center mb-1 text-xs">
                  <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                    <GraduationCap className="w-3.5 h-3.5 text-amber-400" />
                    <span>Eligibility</span>
                    <span className="text-[10px] text-slate-500 font-mono">(15% weight)</span>
                  </span>
                  <span className="font-mono font-bold text-white">100%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div className="h-full rounded-full bg-gradient-to-r from-amber-500 to-orange-500" style={{ width: '100%' }} />
                </div>
              </div>

              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <div className="flex justify-between items-center mb-1 text-xs">
                  <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-purple-400" />
                    <span>Preference</span>
                    <span className="text-[10px] text-slate-500 font-mono">(10% weight)</span>
                  </span>
                  <span className="font-mono font-bold text-white">80%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div className="h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-500" style={{ width: '80%' }} />
                </div>
              </div>
            </div>

            {/* MATCHING SKILLS & SKILL GAP */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-800/80">
              <div>
                <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <span className="text-emerald-400 font-bold">&#10003;</span>
                  <span>MATCHING SKILLS</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {['Python', 'Machine Learning', 'Pandas', 'SQL'].map((s, idx) => (
                    <span key={idx} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{s}</span>
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <span className="text-amber-400 font-bold">&#9675;</span>
                  <span>SKILL GAP</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {['Docker', 'AWS'].map((s, idx) => (
                    <span key={idx} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-950 text-amber-300 border border-amber-500/30">
                      <Circle className="w-3 h-3 text-amber-400" />
                      <span>{s}</span>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* WHY THIS JOB? */}
            <div className="mt-5 p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <HelpCircle className="w-4 h-4 text-brand-400" />
                <span>WHY THIS JOB?</span>
              </div>
              <ul className="space-y-1.5 text-xs text-slate-300">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                  Strong technical skill overlap.
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                  Education requirement is satisfied.
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                  Your profile has high semantic similarity.
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                  The job matches your remote preference.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 3 Pillars Section */}
      <section id="features" className="py-20 border-b border-slate-900 bg-slate-950/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white mb-3">
              How JobTrail-AI Solves Career Discovery
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Unlike black-box job boards that match keywords blindly, JobTrail-AI models candidate profile representation
              and computes deterministic, transparent recommendations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center mb-4">
                <Brain className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-2">Pretrained Sentence Transformers</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Uses <code className="text-brand-300">all-MiniLM-L6-v2</code> to convert your textual profile into dense semantic vectors, capturing conceptual alignment beyond shallow keywords.
              </p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <div className="w-10 h-10 rounded-xl bg-brand-500/10 text-brand-400 border border-brand-500/20 flex items-center justify-center mb-4">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-2">Explainable 4D Matching</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Clear formula combining Semantic Similarity (50%), Skill Overlap (25%), Eligibility (15%), and Preferences (10%) with verified reasons.
              </p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center mb-4">
                <TrendingUp className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-2">Targeted Skill-Gap Engine</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Identifies missing technical requirements for your dream jobs and calculates which competencies will give the highest match score boost.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="p-10 rounded-3xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white mb-4">
              Ready to find career paths that genuinely match you?
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mb-8 max-w-lg mx-auto">
              Upload your resume or build your candidate profile in 2 minutes. Experience genuine explainable career matching.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                to="/register"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-colors shadow-lg shadow-brand-500/20 text-xs sm:text-sm"
              >
                <span>Create Candidate Account</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/how-it-works"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors text-xs sm:text-sm"
              >
                <span>Read Technical Architecture</span>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
