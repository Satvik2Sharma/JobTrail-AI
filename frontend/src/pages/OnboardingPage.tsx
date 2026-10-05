import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import {
  Compass,
  ArrowRight,
  ArrowLeft,
  Check,
  Upload,
  FileText,
  Sparkles,
  Plus,
  X,
  Building,
  GraduationCap,
  Wrench,
  Sliders,
  CheckCircle,
} from 'lucide-react';

const SUGGESTED_SKILLS = [
  'Python', 'Machine Learning', 'Pandas', 'NumPy', 'SQL',
  'FastAPI', 'React', 'JavaScript', 'TypeScript', 'Docker',
  'Git', 'AWS', 'Data Structures', 'Algorithms', 'Tailwind CSS',
  'PostgreSQL', 'Scikit-learn', 'PyTorch', 'REST API', 'Linux'
];

export const OnboardingPage: React.FC = () => {
  const [step, setStep] = useState<number>(1);
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  
  // Education
  const [degree, setDegree] = useState('B.Tech in Computer Science');
  const [education, setEducation] = useState('B.Tech');
  const [fieldOfStudy, setFieldOfStudy] = useState('Computer Science');
  const [graduationYear, setGraduationYear] = useState<number>(2025);
  const [experienceYears, setExperienceYears] = useState<number>(0.5);

  // Skills
  const [selectedSkills, setSelectedSkills] = useState<string[]>([
    'Python', 'Machine Learning', 'SQL', 'Git'
  ]);
  const [customSkillInput, setCustomSkillInput] = useState('');

  // Preferences
  const [remotePreference, setRemotePreference] = useState('hybrid');
  const [preferredLocation, setPreferredLocation] = useState('San Francisco, CA');
  const [interests, setInterests] = useState('Machine Learning, Distributed Systems, Web Development');

  // Resume
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'completed' | 'failed'>('idle');
  const [uploadMessage, setUploadMessage] = useState<string>('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const toggleSkill = (skill: string) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter((s) => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const addCustomSkill = () => {
    if (customSkillInput.trim() && !selectedSkills.includes(customSkillInput.trim())) {
      setSelectedSkills([...selectedSkills, customSkillInput.trim()]);
      setCustomSkillInput('');
    }
  };

  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        setResumeFile(file);
      } else {
        alert('Please select a valid PDF file.');
      }
    }
  };

  const handleUploadResume = async () => {
    if (!resumeFile) return;
    setUploadState('uploading');
    setUploadMessage('Extracting text and analyzing candidate attributes with PyMuPDF...');
    try {
      const res = await api.uploadResume(resumeFile);
      setUploadState('completed');
      setUploadMessage(`Successfully parsed! Detected ${res.skills_detected_count} skills.`);
      if (res.intelligence?.detected_skills) {
        // Merge skills
        const combined = Array.from(new Set([...selectedSkills, ...res.intelligence.detected_skills]));
        setSelectedSkills(combined);
      }
    } catch (err: any) {
      setUploadState('failed');
      setUploadMessage(err.message || 'Failed to process PDF.');
    }
  };

  const handleFinish = async () => {
    setIsSubmitting(true);
    try {
      await api.updateProfile({
        phone,
        location,
        education,
        degree,
        field_of_study: fieldOfStudy,
        graduation_year: graduationYear,
        experience_years: experienceYears,
        remote_preference: remotePreference,
        preferred_location: preferredLocation,
        interests,
        skills: selectedSkills,
      });

      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to update profile during onboarding:', err);
      navigate('/dashboard');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen py-12 px-4 max-w-2xl mx-auto">
      {/* Stepper Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-2">
          <span>Step {step} of 5</span>
          <span>{Math.round((step / 5) * 100)}% Completed</span>
        </div>
        <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
          <div
            className="h-full bg-gradient-to-r from-brand-500 to-emerald-400 transition-all duration-300"
            style={{ width: `${(step / 5) * 100}%` }}
          />
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl">
        {/* Step 1: Basic Information */}
        {step === 1 && (
          <div className="space-y-5">
            <div>
              <div className="inline-flex p-2.5 rounded-xl bg-brand-500/10 text-brand-400 mb-3 border border-brand-500/20">
                <Building className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-white">Basic Information</h2>
              <p className="text-xs text-slate-400">Let's start with your location and contact details.</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Current Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. San Francisco, CA or Bengaluru, India"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Phone Number (Optional)</label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 000-0000"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>
          </div>
        )}

        {/* Step 2: Education */}
        {step === 2 && (
          <div className="space-y-5">
            <div>
              <div className="inline-flex p-2.5 rounded-xl bg-blue-500/10 text-blue-400 mb-3 border border-blue-500/20">
                <GraduationCap className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-white">Education & Background</h2>
              <p className="text-xs text-slate-400">This helps evaluate eligibility criteria for student and entry roles.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Degree / Qualification</label>
                <input
                  type="text"
                  value={degree}
                  onChange={(e) => setDegree(e.target.value)}
                  placeholder="e.g. B.Tech Computer Science"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Field of Study</label>
                <input
                  type="text"
                  value={fieldOfStudy}
                  onChange={(e) => setFieldOfStudy(e.target.value)}
                  placeholder="e.g. Computer Science / AI / IT"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Graduation Year</label>
                <input
                  type="number"
                  value={graduationYear}
                  onChange={(e) => setGraduationYear(parseInt(e.target.value) || 2025)}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Experience (Years)</label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  value={experienceYears}
                  onChange={(e) => setExperienceYears(parseFloat(e.target.value) || 0)}
                  placeholder="e.g. 0.5 for internship/projects"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Skills */}
        {step === 3 && (
          <div className="space-y-5">
            <div>
              <div className="inline-flex p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 mb-3 border border-emerald-500/20">
                <Wrench className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-white">Technical Skills</h2>
              <p className="text-xs text-slate-400">Select skills you know or add your own.</p>
            </div>

            {/* Selected Skills Chips */}
            <div>
              <div className="text-xs font-semibold text-slate-300 mb-2">
                Selected Skills ({selectedSkills.length})
              </div>
              <div className="flex flex-wrap gap-1.5 min-h-[44px] p-3 rounded-xl bg-slate-950 border border-slate-800">
                {selectedSkills.map((sk) => (
                  <span
                    key={sk}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-brand-500/20 text-brand-300 border border-brand-500/30"
                  >
                    {sk}
                    <button
                      type="button"
                      onClick={() => toggleSkill(sk)}
                      className="hover:text-rose-400 transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Custom Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={customSkillInput}
                onChange={(e) => setCustomSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCustomSkill())}
                placeholder="Type a skill (e.g. PyTorch, Next.js, Docker)..."
                className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
              <button
                type="button"
                onClick={addCustomSkill}
                className="px-4 py-2.5 rounded-xl font-semibold bg-slate-800 hover:bg-slate-700 text-white text-xs flex items-center gap-1 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add
              </button>
            </div>

            {/* Suggested Skills */}
            <div>
              <div className="text-xs font-semibold text-slate-400 mb-2">Popular Suggestions</div>
              <div className="flex flex-wrap gap-1.5">
                {SUGGESTED_SKILLS.filter((s) => !selectedSkills.includes(s)).map((sk) => (
                  <button
                    key={sk}
                    type="button"
                    onClick={() => toggleSkill(sk)}
                    className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-colors"
                  >
                    + {sk}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Preferences */}
        {step === 4 && (
          <div className="space-y-5">
            <div>
              <div className="inline-flex p-2.5 rounded-xl bg-purple-500/10 text-purple-400 mb-3 border border-purple-500/20">
                <Sliders className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-white">Workplace Preferences</h2>
              <p className="text-xs text-slate-400">Configure remote settings and role interest areas.</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2">Remote Work Preference</label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {[
                  { id: 'remote', label: 'Remote Only' },
                  { id: 'hybrid', label: 'Hybrid' },
                  { id: 'onsite', label: 'In-Office' },
                  { id: 'any', label: 'Open to Any' },
                ].map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setRemotePreference(opt.id)}
                    className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-colors ${
                      remotePreference === opt.id
                        ? 'bg-brand-500/20 text-brand-300 border-brand-500/40'
                        : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Preferred Target Location</label>
              <input
                type="text"
                value={preferredLocation}
                onChange={(e) => setPreferredLocation(e.target.value)}
                placeholder="e.g. San Francisco, CA or Remote"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Career Interests & Domains</label>
              <input
                type="text"
                value={interests}
                onChange={(e) => setInterests(e.target.value)}
                placeholder="e.g. Machine Learning, Cloud Systems, Full Stack, Cybersecurity"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>
          </div>
        )}

        {/* Step 5: Resume Upload */}
        {step === 5 && (
          <div className="space-y-5">
            <div>
              <div className="inline-flex p-2.5 rounded-xl bg-brand-500/10 text-brand-400 mb-3 border border-brand-500/20">
                <FileText className="w-5 h-5" />
              </div>
              <h2 className="text-xl font-bold text-white">Upload Your Resume (PDF)</h2>
              <p className="text-xs text-slate-400">
                PyMuPDF extracts your technical background automatically. You can also skip this step!
              </p>
            </div>

            <div className="border-2 border-dashed border-slate-800 hover:border-brand-500/40 rounded-2xl p-6 text-center transition-colors">
              <Upload className="w-8 h-8 text-slate-500 mx-auto mb-2" />
              <p className="text-xs text-slate-300 font-medium mb-1">
                {resumeFile ? resumeFile.name : 'Select or drag your PDF resume here'}
              </p>
              <p className="text-[11px] text-slate-500 mb-3">PDF up to 10MB</p>
              <label className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white cursor-pointer transition-colors">
                <Upload className="w-3.5 h-3.5" />
                Browse File
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleResumeChange}
                  className="hidden"
                />
              </label>
            </div>

            {resumeFile && (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs text-slate-300">
                  <FileText className="w-4 h-4 text-brand-400" />
                  <span className="font-semibold">{resumeFile.name}</span>
                  <span className="text-slate-500">({(resumeFile.size / 1024).toFixed(1)} KB)</span>
                </div>
                <button
                  type="button"
                  onClick={handleUploadResume}
                  disabled={uploadState === 'uploading'}
                  className="px-3 py-1.5 rounded-lg font-semibold bg-brand-500 text-slate-950 hover:bg-brand-400 text-xs transition-colors flex items-center gap-1"
                >
                  {uploadState === 'uploading' ? 'Analyzing...' : 'Parse Resume'}
                </button>
              </div>
            )}

            {uploadMessage && (
              <div
                className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
                  uploadState === 'completed'
                    ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                    : uploadState === 'failed'
                    ? 'bg-rose-500/10 border border-rose-500/20 text-rose-400'
                    : 'bg-blue-500/10 border border-blue-500/20 text-blue-400'
                }`}
              >
                {uploadState === 'completed' && <CheckCircle className="w-4 h-4 shrink-0" />}
                <span>{uploadMessage}</span>
              </div>
            )}
          </div>
        )}

        {/* Stepper Navigation Buttons */}
        <div className="mt-8 pt-6 border-t border-slate-800 flex items-center justify-between">
          {step > 1 ? (
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>
          ) : (
            <div />
          )}

          <div className="flex items-center gap-2">
            {step === 5 && (
              <button
                type="button"
                onClick={handleFinish}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 transition-colors"
              >
                Skip Resume
              </button>
            )}

            {step < 5 ? (
              <button
                type="button"
                onClick={() => setStep(step + 1)}
                className="px-5 py-2.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 text-slate-950 text-xs transition-colors flex items-center gap-1 shadow-md shadow-brand-500/20"
              >
                <span>Continue</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleFinish}
                disabled={isSubmitting}
                className="px-5 py-2.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 disabled:opacity-60 text-slate-950 text-xs transition-colors flex items-center gap-1 shadow-md shadow-brand-500/20"
              >
                <span>Complete Profile & View Matches</span>
                <Check className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
