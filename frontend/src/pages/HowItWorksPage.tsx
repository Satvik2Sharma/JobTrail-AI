import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Brain,
  Award,
  GraduationCap,
  MapPin,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Layers,
  CheckCircle2,
  FileText,
  Sliders,
  Compass,
} from 'lucide-react';

export const HowItWorksPage: React.FC = () => {
  // Interactive Simulator State for Evaluators
  const [semanticScore, setSemanticScore] = useState(92);
  const [skillScore, setSkillScore] = useState(96);
  const [eligibilityScore, setEligibilityScore] = useState(100);
  const [preferenceScore, setPreferenceScore] = useState(80);

  const calculatedHybrid = Math.round(
    0.50 * semanticScore +
    0.25 * skillScore +
    0.15 * eligibilityScore +
    0.10 * preferenceScore
  );

  const pipelineSteps = [
    { name: 'Resume / Candidate Profile', desc: 'Raw PDF or structured profile inputs' },
    { name: 'Information Extraction', desc: 'PyMuPDF text stream and entity pattern parsing' },
    { name: 'Skill Normalization', desc: '107+ canonical taxonomy boundary matching' },
    { name: 'Candidate Representation', desc: 'Synthesized textual career profile narrative' },
    { name: 'Sentence Transformer', desc: 'all-MiniLM-L6-v2 deep contextual encoding' },
    { name: 'Semantic Embedding', desc: '384-dimensional dense vector generation' },
    { name: 'Cosine Similarity', desc: 'High-dimensional angular distance computation' },
    { name: 'Skill Compatibility', desc: 'Weighted Jaccard overlap of required core skills' },
    { name: 'Eligibility', desc: 'Degree level hierarchy and experience threshold check' },
    { name: 'Preferences', desc: 'Workplace model, location, and domain category match' },
    { name: 'Hybrid Match Score', desc: 'Deterministic 50/25/15/10 weighted formula' },
    { name: 'Ranking', desc: 'Descendant ordering across 305 job opportunities' },
    { name: 'Explainable Recommendation', desc: 'Evidence-based justification generation' },
    { name: 'Skill Gap Analysis', desc: 'Targeted missing competency impact prioritization' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-16">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-semibold text-brand-400">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Academic Architecture & Methodology</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-white">
            How <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-emerald-300">JobTrail-AI</span> Works
          </h1>
          <p className="text-base text-slate-400 leading-relaxed">
            Explainable AI-Powered Job & Internship Recommendation Platform.
            <br />
            <em className="text-slate-300">"Discover opportunities that match your profile — and understand exactly why."</em>
          </p>
        </div>

        {/* 1. Core Mathematical Formula */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-brand-400">
            <Cpu className="w-4 h-4" />
            <span>Hybrid Recommendation Formula</span>
          </div>

          <div className="p-6 bg-slate-950 rounded-2xl border border-slate-800 text-center space-y-2">
            <div className="text-lg sm:text-2xl font-mono font-bold text-white tracking-wide">
              Score = (0.50 &times; Semantic) + (0.25 &times; Skill) + (0.15 &times; Eligibility) + (0.10 &times; Preference)
            </div>
            <p className="text-xs text-slate-400">
              Deterministic, transparent, and explainable multi-factor scoring. Zero random weights or black-box guesswork.
            </p>
          </div>

          {/* Interactive Formula Playground */}
          <div className="pt-4 border-t border-slate-800/80">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <Sliders className="w-4 h-4 text-brand-400" />
                <span>Interactive Hybrid Scoring Simulator</span>
              </h3>
              <div className="text-xs font-bold px-3 py-1 rounded-full bg-brand-500/10 text-brand-300 border border-brand-500/30">
                Calculated Hybrid: <span className="text-white text-sm font-mono">{calculatedHybrid}%</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Semantic */}
              <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-blue-400">Semantic Match (50% weight)</span>
                  <span className="font-mono text-white font-bold">{semanticScore}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={semanticScore}
                  onChange={(e) => setSemanticScore(Number(e.target.value))}
                  className="w-full accent-blue-500"
                />
              </div>

              {/* Skill */}
              <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-emerald-400">Skill Match (25% weight)</span>
                  <span className="font-mono text-white font-bold">{skillScore}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={skillScore}
                  onChange={(e) => setSkillScore(Number(e.target.value))}
                  className="w-full accent-emerald-500"
                />
              </div>

              {/* Eligibility */}
              <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-amber-400">Eligibility Match (15% weight)</span>
                  <span className="font-mono text-white font-bold">{eligibilityScore}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={eligibilityScore}
                  onChange={(e) => setEligibilityScore(Number(e.target.value))}
                  className="w-full accent-amber-500"
                />
              </div>

              {/* Preference */}
              <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-purple-400">Preference Match (10% weight)</span>
                  <span className="font-mono text-white font-bold">{preferenceScore}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={preferenceScore}
                  onChange={(e) => setPreferenceScore(Number(e.target.value))}
                  className="w-full accent-purple-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* 2. Technical Contribution: The 14-Stage ML Pipeline */}
        <div className="space-y-6">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
              The JobTrail-AI End-to-End Pipeline
            </h2>
            <p className="text-xs text-slate-400">
              From raw unstructured resume text to explainable recommendations and skill gap roadmaps.
            </p>
          </div>

          <div className="relative border-l-2 border-brand-500/30 ml-4 sm:ml-8 pl-6 sm:pl-8 space-y-6 my-8">
            {pipelineSteps.map((step, idx) => (
              <div key={idx} className="relative group">
                <div className="absolute -left-[31px] sm:-left-[39px] top-1 w-6 h-6 rounded-full bg-slate-900 border-2 border-brand-400 flex items-center justify-center text-[10px] font-bold text-brand-300">
                  {idx + 1}
                </div>
                <div className="p-4 bg-slate-900/80 hover:bg-slate-900 border border-slate-800 rounded-2xl transition-colors">
                  <h4 className="text-sm font-bold text-white">{step.name}</h4>
                  <p className="text-xs text-slate-400 mt-0.5">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 3. Deep Dive into the 4 Pillars */}
        <div className="space-y-6">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white text-center">
            The Four Pillars of Recommendation
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Semantic Matching */}
            <div className="p-6 bg-slate-900 border border-slate-800 rounded-3xl space-y-3">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center">
                <Brain className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">1. Semantic Matching (50%)</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Represents candidate profile text and job descriptions as 384-dimensional dense vectors using{' '}
                <code className="text-brand-300 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">
                  all-MiniLM-L6-v2
                </code>
                . Cosine similarity calculates conceptual alignment beyond superficial keyword matching.
              </p>
              <div className="text-[11px] font-mono text-slate-400 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                cos(&theta;) = (u &bull; v) / (||u|| ||v||)
              </div>
            </div>

            {/* Skill Matching */}
            <div className="p-6 bg-slate-900 border border-slate-800 rounded-3xl space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center">
                <Award className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">2. Skill Compatibility (25%)</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Candidate skills are extracted using phrase and token boundary matching and normalized against a 107+ canonical skill taxonomy with synonym dictionaries. Evaluates exact required competencies with weighting.
              </p>
              <div className="text-[11px] font-mono text-slate-400 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                SkillScore = &sum;(w_matched) / &sum;(w_required)
              </div>
            </div>

            {/* Eligibility */}
            <div className="p-6 bg-slate-900 border border-slate-800 rounded-3xl space-y-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center">
                <GraduationCap className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">3. Eligibility & Education (15%)</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Evaluates candidate education level (High School &rarr; Associate &rarr; Bachelor's &rarr; Master's &rarr; Ph.D.) and years of experience against posted role prerequisites, giving neutral baseline if unspecified.
              </p>
              <div className="text-[11px] font-mono text-slate-400 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                Level(Candidate) &ge; Level(Requirement)
              </div>
            </div>

            {/* Preferences */}
            <div className="p-6 bg-slate-900 border border-slate-800 rounded-3xl space-y-3">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center justify-center">
                <MapPin className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">4. Preferences & Culture (10%)</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Compares remote workplace preference (Remote, Hybrid, Onsite), geographic location alignment, and category interests (AI/ML, Backend, Cloud, Systems) to ensure sustainable job satisfaction.
              </p>
              <div className="text-[11px] font-mono text-slate-400 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                Alignment(Remote, Location, Domain)
              </div>
            </div>
          </div>
        </div>

        {/* 4. Academic Honesty & Disclosures */}
        <div className="p-6 sm:p-8 bg-slate-900/60 border border-slate-800 rounded-3xl space-y-4">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
            <span>Academic Disclosure & Model Transparency</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs text-slate-400">
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <div className="font-bold text-white mb-1">Embedding Model</div>
              <div>Pretrained Sentence Transformer (<code className="text-brand-300">all-MiniLM-L6-v2</code>). No proprietary weights trained.</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <div className="font-bold text-white mb-1">Recommendation Core</div>
              <div>Custom deterministic hybrid ranking pipeline with 4-factor explainability.</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <div className="font-bold text-white mb-1">Job Dataset</div>
              <div>Synthetic prototype dataset (305 structured tech roles). No live scrapers or real employer data.</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <div className="font-bold text-white mb-1">Resume Parser</div>
              <div>PyMuPDF (<code className="text-brand-300">fitz</code>) textual extraction with regex entity boundary rules.</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <div className="font-bold text-white mb-1">Distance Metric</div>
              <div>Cosine similarity across normalized L2 unit vectors.</div>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <div className="font-bold text-white mb-1">Verification</div>
              <div>31 automated passing tests verifying ML ranking consistency and safety bounds.</div>
            </div>
          </div>
        </div>

        {/* Action Link */}
        <div className="text-center pt-4">
          <Link
            to="/register"
            className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 transition-colors shadow-lg shadow-brand-500/20 text-xs sm:text-sm"
          >
            <span>Experience JobTrail-AI Now</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
};
