import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import {
  Briefcase,
  Building2,
  MapPin,
  ArrowLeft,
  Plus,
  X,
  Sparkles,
  Check,
} from 'lucide-react';

const COMMON_SKILLS = [
  'Python', 'Machine Learning', 'SQL', 'FastAPI', 'React', 'TypeScript',
  'Docker', 'AWS', 'PostgreSQL', 'NumPy', 'Pandas', 'Git', 'Linux'
];

export const RecruiterJobCreatePage: React.FC = () => {
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [location, setLocation] = useState('San Francisco, CA');
  const [remote, setRemote] = useState(false);
  const [employmentType, setEmploymentType] = useState('Full-time');
  const [experienceLevel, setExperienceLevel] = useState('0-1 years');
  const [educationRequirement, setEducationRequirement] = useState('B.Tech/B.E. in Computer Science or related STEM field');
  const [category, setCategory] = useState('AI/ML');
  const [description, setDescription] = useState('');
  const [requirements, setRequirements] = useState('');
  const [responsibilities, setResponsibilities] = useState('');
  const [salaryMin, setSalaryMin] = useState<number | ''>(60000);
  const [salaryMax, setSalaryMax] = useState<number | ''>(85000);
  const [skills, setSkills] = useState<string[]>(['Python', 'Machine Learning', 'SQL']);
  const [skillInput, setSkillInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const navigate = useNavigate();

  const toggleSkill = (sk: string) => {
    if (skills.includes(sk)) {
      setSkills(skills.filter((s) => s !== sk));
    } else {
      setSkills([...skills, sk]);
    }
  };

  const addSkill = () => {
    if (skillInput.trim() && !skills.includes(skillInput.trim())) {
      setSkills([...skills, skillInput.trim()]);
      setSkillInput('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !company || !description) {
      alert('Please fill out all required fields.');
      return;
    }

    setIsSubmitting(true);
    try {
      await api.createRecruiterJob({
        title,
        company,
        location,
        remote,
        employment_type: employmentType,
        experience_level: experienceLevel,
        education_requirement: educationRequirement,
        category,
        description,
        requirements,
        responsibilities,
        salary_min: salaryMin ? Number(salaryMin) : undefined,
        salary_max: salaryMax ? Number(salaryMax) : undefined,
        skills,
      });

      navigate('/recruiter');
    } catch (err: any) {
      alert(err.message || 'Failed to create job posting.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <Link
        to="/recruiter"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Recruiter Hub</span>
      </Link>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-purple-400 mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Embeddings Auto-Generated</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">Create Job Posting</h1>
          <p className="text-xs text-slate-400 mt-1">
            Publish an opportunity. Our Sentence-Transformer will immediately generate vector representations
            to enable candidate ranking.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Job Title *</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Junior Machine Learning Engineer"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Company Name *</label>
              <input
                type="text"
                required
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="e.g. TechNova Labs"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Location *</label>
              <input
                type="text"
                required
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. San Francisco, CA"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Employment Type</label>
              <select
                value={employmentType}
                onChange={(e) => setEmploymentType(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500"
              >
                <option value="Internship">Internship</option>
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Experience Level</label>
              <select
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500"
              >
                <option value="0-1 years">0-1 years (Entry/Intern)</option>
                <option value="1-2 years">1-2 years (Junior)</option>
                <option value="2-4 years">2-4 years (Mid)</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="remoteCheck"
              checked={remote}
              onChange={(e) => setRemote(e.target.checked)}
              className="rounded bg-slate-950 border-slate-800 text-brand-500 focus:ring-0"
            />
            <label htmlFor="remoteCheck" className="text-xs text-slate-300 cursor-pointer">
              Remote Opportunity (Candidates anywhere can apply)
            </label>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Education Requirement</label>
              <input
                type="text"
                value={educationRequirement}
                onChange={(e) => setEducationRequirement(e.target.value)}
                placeholder="e.g. B.Tech/B.E. in Computer Science"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500"
              >
                <option value="AI/ML">AI/ML</option>
                <option value="Data Science & Analytics">Data Science & Analytics</option>
                <option value="Backend Development">Backend Development</option>
                <option value="Frontend Development">Frontend Development</option>
                <option value="Full Stack">Full Stack</option>
                <option value="Cloud & DevOps">Cloud & DevOps</option>
                <option value="Cybersecurity">Cybersecurity</option>
                <option value="Mobile Development">Mobile Development</option>
              </select>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Role Description *</label>
            <textarea
              rows={4}
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the opportunity, core responsibilities, and team culture..."
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>

          {/* Skills Tag Management */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Required Skills</label>
            <div className="flex flex-wrap gap-1.5 p-3 rounded-xl bg-slate-950 border border-slate-800 mb-3">
              {skills.map((s) => (
                <span
                  key={s}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-brand-500/20 text-brand-300 border border-brand-500/30"
                >
                  {s}
                  <button type="button" onClick={() => toggleSkill(s)} className="hover:text-rose-400">
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>

            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                placeholder="Type and add a skill..."
                className="flex-1 px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500"
              />
              <button
                type="button"
                onClick={addSkill}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" />
                Add
              </button>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {COMMON_SKILLS.filter((s) => !skills.includes(s)).map((sk) => (
                <button
                  key={sk}
                  type="button"
                  onClick={() => toggleSkill(sk)}
                  className="px-2.5 py-1 rounded-lg text-[11px] font-medium bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-white"
                >
                  + {sk}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <Link
              to="/recruiter"
              className="px-5 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 disabled:opacity-60 text-slate-950 text-xs transition-colors shadow-lg shadow-brand-500/20 flex items-center gap-1.5"
            >
              {isSubmitting ? 'Generating Embeddings & Publishing...' : 'Publish Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
