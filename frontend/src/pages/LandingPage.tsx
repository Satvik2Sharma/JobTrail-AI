import React from 'react';
import { Link } from 'react-router-dom';
import {
  Compass,
  Sparkles,
  Brain,
  CheckCircle,
  TrendingUp,
  Search,
  ArrowRight,
  ShieldCheck,
  ChevronRight,
  Layers,
  Award,
  GraduationCap,
  MapPin,
  FileText,
} from 'lucide-react';
import { MatchBadge } from '../components/MatchBadge';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Hero Section */}
      <section className="relative pt-24 pb-20 overflow-hidden border-b border-slate-900">
        {/* Subtle background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-brand-500/10 blur-[120px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-semibold text-brand-400 mb-6 shadow-sm">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Next-Gen Career Recommendation Engine</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
              Find opportunities that <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-emerald-300">actually match you</span>.
            </h1>

            <p className="text-base sm:text-lg text-slate-400 leading-relaxed max-w-2xl mx-auto mb-8">
              JobTrail-AI uses your skills, education, experience and career preferences to find relevant jobs and internships —
              then explains <em>why</em> they match and <em>what skills you're missing</em>.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                to="/register"
                className="w-full sm:w-auto px-6 py-3.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-all shadow-lg shadow-brand-500/25 flex items-center justify-center gap-2"
              >
                <span>Get Recommended</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/login"
                className="w-full sm:w-auto px-6 py-3.5 rounded-xl font-semibold bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 transition-colors flex items-center justify-center gap-2"
              >
                <span>Demo Sign In</span>
                <ChevronRight className="w-4 h-4 text-slate-500" />
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
                <MatchBadge score={91} size="lg" />
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-6">
              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
                <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mb-1">
                  <Brain className="w-3.5 h-3.5 text-blue-400" />
                  Semantic Match
                </div>
                <div className="text-lg font-bold text-white">92%</div>
                <div className="text-[10px] text-slate-500">50% weight</div>
              </div>
              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
                <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mb-1">
                  <Award className="w-3.5 h-3.5 text-emerald-400" />
                  Skill Overlap
                </div>
                <div className="text-lg font-bold text-white">94%</div>
                <div className="text-[10px] text-slate-500">25% weight</div>
              </div>
              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
                <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mb-1">
                  <GraduationCap className="w-3.5 h-3.5 text-amber-400" />
                  Eligibility
                </div>
                <div className="text-lg font-bold text-white">100%</div>
                <div className="text-[10px] text-slate-500">15% weight</div>
              </div>
              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
                <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mb-1">
                  <MapPin className="w-3.5 h-3.5 text-purple-400" />
                  Preferences
                </div>
                <div className="text-lg font-bold text-white">80%</div>
                <div className="text-[10px] text-slate-500">10% weight</div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div>
                <div className="text-xs font-semibold text-slate-400 mb-2">Matching Skills</div>
                <div className="flex flex-wrap gap-1.5">
                  {['Python', 'Machine Learning', 'Pandas', 'SQL', 'FastAPI'].map((s, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                      &check; {s}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-xs font-semibold text-slate-400 mb-2">Missing Skills to Learn</div>
                <div className="flex flex-wrap gap-1.5">
                  {['Docker', 'AWS'].map((s, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30">
                      &cir; {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-5 p-4 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="text-xs font-bold text-slate-300 mb-2 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-brand-400" />
                <span>Evidence-Based Why:</span>
              </div>
              <ul className="space-y-1.5 text-xs text-slate-400">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                  Strong overlap with technical skills (4 matching core skills detected).
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                  Your B.Tech Computer Science degree satisfies the educational criteria.
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                  Your remote workplace preference directly aligns with this remote role.
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
            <p className="text-sm text-slate-400">
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
            <h2 className="text-3xl font-extrabold text-white mb-4">
              Ready to find career paths that genuinely match you?
            </h2>
            <p className="text-sm text-slate-400 mb-8 max-w-lg mx-auto">
              Upload your resume or build your candidate profile in 2 minutes. Experience genuine explainable career matching.
            </p>
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-colors shadow-lg shadow-brand-500/20"
            >
              <span>Create Candidate Account</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
