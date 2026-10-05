import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  FileText,
  Upload,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Award,
  GraduationCap,
  Briefcase,
  FolderGit2,
  Cpu,
  Layers,
  Check,
} from 'lucide-react';

export const ResumeIntelligencePage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<
    'idle' | 'uploading' | 'extracting' | 'analyzing' | 'completed' | 'failed'
  >('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [intelligenceData, setIntelligenceData] = useState<any>(null);
  const [completeness, setCompleteness] = useState<number>(0);
  const [isLoadingExisting, setIsLoadingExisting] = useState<boolean>(true);

  const loadExistingResumeIntelligence = async () => {
    setIsLoadingExisting(true);
    try {
      const res = await api.getResumeIntelligence();
      if (res.has_resume && res.intelligence) {
        setIntelligenceData(res.intelligence);
        setCompleteness(res.completeness || res.intelligence.profile_completeness || 0);
      }
    } catch (err) {
      console.error('Failed to load existing resume data:', err);
    } finally {
      setIsLoadingExisting(false);
    }
  };

  useEffect(() => {
    loadExistingResumeIntelligence();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      if (f.name.toLowerCase().endsWith('.pdf')) {
        setSelectedFile(f);
        setErrorMessage(null);
      } else {
        setErrorMessage('Please upload a PDF document (.pdf).');
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setErrorMessage(null);
    setUploadStatus('uploading');

    try {
      // Simulate stepped progress indicators for UX clarity
      setTimeout(() => setUploadStatus('extracting'), 400);
      setTimeout(() => setUploadStatus('analyzing'), 900);

      const res = await api.uploadResume(selectedFile);
      setIntelligenceData(res.intelligence);
      setCompleteness(res.intelligence?.profile_completeness || 85);
      setUploadStatus('completed');
    } catch (err: any) {
      setUploadStatus('failed');
      const msg = err.message || '';
      if (
        msg.includes('selectable') ||
        msg.includes('extractable') ||
        msg.includes('Scanned') ||
        msg.includes('parse') ||
        msg.includes('Failed')
      ) {
        setErrorMessage("We couldn't process this resume. Please make sure the PDF contains selectable text and try again.");
      } else {
        setErrorMessage(msg || "We couldn't process this resume. Please make sure the PDF contains selectable text and try again.");
      }
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-brand-400 mb-1">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Resume Intelligence Engine</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
          Resume Intelligence & Skill Parsing
        </h1>
        <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
          Upload your PDF resume. JobTrail-AI runs PyMuPDF text extraction, extracts contact details, education, degree,
          and projects, and normalizes candidate skills against our comprehensive technical taxonomy.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8">
        <div className="border-2 border-dashed border-slate-800 hover:border-brand-500/40 rounded-2xl p-8 text-center transition-colors">
          <div className="w-12 h-12 rounded-2xl bg-brand-500/10 text-brand-400 border border-brand-500/20 flex items-center justify-center mx-auto mb-3">
            <Upload className="w-6 h-6" />
          </div>

          <h3 className="text-base font-bold text-white mb-1">
            {selectedFile ? selectedFile.name : 'Upload your PDF Resume'}
          </h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-4">
            Upload a resume to automatically discover your skills and experience. Supports selectable PDF up to 10MB.
          </p>

          <div className="flex items-center justify-center gap-3">
            <label className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white cursor-pointer transition-colors inline-flex items-center gap-2">
              <FileText className="w-3.5 h-3.5" />
              <span>{selectedFile ? 'Change PDF' : 'Select PDF File'}</span>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>

            {selectedFile && (
              <button
                onClick={handleUpload}
                disabled={['uploading', 'extracting', 'analyzing'].includes(uploadStatus)}
                className="px-6 py-2.5 rounded-xl font-bold bg-brand-500 hover:bg-brand-400 disabled:opacity-60 text-slate-950 text-xs transition-colors shadow-md shadow-brand-500/20 flex items-center gap-1.5"
              >
                <span>Process Resume</span>
              </button>
            )}
          </div>
        </div>

        {/* State progress alerts */}
        {uploadStatus !== 'idle' && (
          <div className="mt-4 p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs">
            {uploadStatus === 'uploading' && (
              <div className="flex items-center gap-2 text-blue-400">
                <div className="w-3.5 h-3.5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                <span>Uploading PDF document...</span>
              </div>
            )}
            {uploadStatus === 'extracting' && (
              <div className="flex items-center gap-2 text-indigo-400">
                <div className="w-3.5 h-3.5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                <span>Extracting raw text via PyMuPDF block parser...</span>
              </div>
            )}
            {uploadStatus === 'analyzing' && (
              <div className="flex items-center gap-2 text-purple-400">
                <div className="w-3.5 h-3.5 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
                <span>Analyzing candidate attributes and normalizing technical skills...</span>
              </div>
            )}
            {uploadStatus === 'completed' && (
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle className="w-4 h-4" />
                <span>Analysis complete! Extracted profile and detected skills have been updated.</span>
              </div>
            )}
            {uploadStatus === 'failed' && (
              <div className="flex items-center gap-2 text-rose-400">
                <AlertCircle className="w-4 h-4" />
                <span>{errorMessage || 'Failed to parse resume.'}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Extracted Intelligence Results */}
      {intelligenceData && (
        <div className="space-y-6">
          {/* Completeness Gauge */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-bold text-white">Profile Completeness</h3>
                <p className="text-xs text-slate-400">
                  Calculated deterministically from available contact, education, skill, and project information.
                </p>
              </div>
              <div className="text-2xl font-extrabold text-brand-400">{completeness}%</div>
            </div>
            <div className="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden border border-slate-800">
              <div
                className="h-full bg-gradient-to-r from-brand-500 to-emerald-400 rounded-full transition-all duration-700"
                style={{ width: `${completeness}%` }}
              />
            </div>
          </div>

          {/* Detected Skills Taxonomy Section */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Award className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-white">
                  Detected Normalized Skills ({intelligenceData.detected_skills?.length || 0})
                </h3>
              </div>
              <span className="text-[11px] text-slate-500">Matched against Skill Taxonomy</span>
            </div>

            <div className="flex flex-wrap gap-2 pt-2">
              {intelligenceData.detected_skills?.map((sk: string, idx: number) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30"
                >
                  <Check className="w-3 h-3 text-emerald-400" />
                  {sk}
                </span>
              ))}
            </div>
          </div>

          {/* Candidate Overview Card */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <GraduationCap className="w-4 h-4 text-blue-400" />
                Education & Degree
              </h4>
              <div className="space-y-1.5 text-xs text-slate-300">
                <div>
                  <span className="text-slate-500">Degree: </span>
                  <span className="font-semibold text-white">{intelligenceData.degree || 'Not detected'}</span>
                </div>
                <div>
                  <span className="text-slate-500">Field: </span>
                  <span className="font-semibold text-white">{intelligenceData.field_of_study || 'Not detected'}</span>
                </div>
                <div>
                  <span className="text-slate-500">Graduation Year: </span>
                  <span className="font-semibold text-white">{intelligenceData.graduation_year || 'Not detected'}</span>
                </div>
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Briefcase className="w-4 h-4 text-purple-400" />
                Contact & Experience
              </h4>
              <div className="space-y-1.5 text-xs text-slate-300">
                <div>
                  <span className="text-slate-500">Name: </span>
                  <span className="font-semibold text-white">{intelligenceData.name || 'From profile'}</span>
                </div>
                <div>
                  <span className="text-slate-500">Email: </span>
                  <span className="font-semibold text-white">{intelligenceData.email || 'From profile'}</span>
                </div>
                <div>
                  <span className="text-slate-500">Phone: </span>
                  <span className="font-semibold text-white">{intelligenceData.phone || 'Not detected'}</span>
                </div>
                <div>
                  <span className="text-slate-500">Estimated Tech Experience: </span>
                  <span className="font-semibold text-white">{intelligenceData.experience_years} years</span>
                </div>
              </div>
            </div>
          </div>

          {/* Extracted Projects & Sections */}
          {intelligenceData.sections?.projects && intelligenceData.sections.projects.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
                <FolderGit2 className="w-4 h-4 text-brand-400" />
                <span>Extracted Project Highlights</span>
              </h3>
              <ul className="space-y-2 text-xs text-slate-300">
                {intelligenceData.sections.projects.map((proj: string, idx: number) => (
                  <li key={idx} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 leading-relaxed">
                    {proj}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
