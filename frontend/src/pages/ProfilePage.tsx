import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { UserProfile, SkillItem } from '../types';
import { useAuth } from '../context/AuthContext';
import {
  User,
  GraduationCap,
  Wrench,
  Sliders,
  Check,
  Plus,
  Trash2,
  Save,
  AlertCircle,
  Sparkles,
} from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form states
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [preferredLocation, setPreferredLocation] = useState('');
  const [remotePreference, setRemotePreference] = useState('any');
  const [education, setEducation] = useState('');
  const [degree, setDegree] = useState('');
  const [fieldOfStudy, setFieldOfStudy] = useState('');
  const [graduationYear, setGraduationYear] = useState<number | ''>('');
  const [experienceYears, setExperienceYears] = useState<number>(0);
  const [interests, setInterests] = useState('');

  // Skill management
  const [skills, setSkills] = useState<SkillItem[]>([]);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillProficiency, setNewSkillProficiency] = useState('intermediate');

  const loadProfile = async () => {
    setIsLoading(true);
    try {
      const data = await api.getProfile();
      setProfile(data);
      setPhone(data.phone || '');
      setLocation(data.location || '');
      setPreferredLocation(data.preferred_location || '');
      setRemotePreference(data.remote_preference || 'any');
      setEducation(data.education || '');
      setDegree(data.degree || '');
      setFieldOfStudy(data.field_of_study || '');
      setGraduationYear(data.graduation_year || '');
      setExperienceYears(data.experience_years || 0);
      setInterests(data.interests || '');
      setSkills(data.skills || []);
    } catch (err) {
      console.error('Failed to load profile:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSuccessMessage(null);
    try {
      const updated = await api.updateProfile({
        phone,
        location,
        preferred_location: preferredLocation,
        remote_preference: remotePreference,
        education,
        degree,
        field_of_study: fieldOfStudy,
        graduation_year: graduationYear ? Number(graduationYear) : undefined,
        experience_years: Number(experienceYears),
        interests,
      });
      setProfile(updated);
      setSuccessMessage('Profile details updated successfully.');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      alert(err.message || 'Failed to update profile.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddSkill = async () => {
    if (!newSkillName.trim()) return;
    try {
      const added = await api.addSkill(newSkillName.trim(), newSkillProficiency, 'manual');
      setSkills((prev) => [...prev.filter((s) => s.name.toLowerCase() !== added.name.toLowerCase()), added]);
      setNewSkillName('');
    } catch (err) {
      console.error('Failed to add skill:', err);
    }
  };

  const handleRemoveSkill = async (skillName: string) => {
    try {
      await api.removeSkill(skillName);
      setSkills((prev) => prev.filter((s) => s.name.toLowerCase() !== skillName.toLowerCase()));
    } catch (err) {
      console.error('Failed to remove skill:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-xs text-slate-400">Loading your candidate profile...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-brand-400 mb-1">
            <User className="w-3.5 h-3.5" />
            <span>Candidate Profile Settings</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white">{user?.full_name}</h1>
          <p className="text-xs text-slate-400 mt-0.5">{user?.email} &bull; Role: {user?.role}</p>
        </div>

        <div className="text-right">
          <div className="text-xl font-bold text-brand-400">{profile?.profile_completeness || 0}%</div>
          <div className="text-[11px] text-slate-500 font-medium">Profile Completeness</div>
        </div>
      </div>

      {successMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
          <Check className="w-4 h-4" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Main Profile Form */}
      <form onSubmit={handleSaveProfile} className="space-y-6">
        {/* Education & Experience */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-5">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <GraduationCap className="w-4 h-4 text-blue-400" />
            <span>Education & Experience</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Degree</label>
              <input
                type="text"
                value={degree}
                onChange={(e) => setDegree(e.target.value)}
                placeholder="e.g. B.Tech Computer Science"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Field of Study</label>
              <input
                type="text"
                value={fieldOfStudy}
                onChange={(e) => setFieldOfStudy(e.target.value)}
                placeholder="e.g. Computer Science"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Graduation Year</label>
              <input
                type="number"
                value={graduationYear}
                onChange={(e) => setGraduationYear(e.target.value ? parseInt(e.target.value) : '')}
                placeholder="2025"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Tech Experience (Years)</label>
              <input
                type="number"
                step="0.5"
                min="0"
                value={experienceYears}
                onChange={(e) => setExperienceYears(parseFloat(e.target.value) || 0)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>
          </div>
        </div>

        {/* Preferences & Contact */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-5">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4 text-purple-400" />
            <span>Preferences & Contact</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Current Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. San Francisco, CA"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Preferred Target Location</label>
              <input
                type="text"
                value={preferredLocation}
                onChange={(e) => setPreferredLocation(e.target.value)}
                placeholder="e.g. Remote or Austin, TX"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Phone Number</label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 000-0000"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Remote Work Setting</label>
              <select
                value={remotePreference}
                onChange={(e) => setRemotePreference(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500"
              >
                <option value="any">Open to Any (Remote or On-site)</option>
                <option value="remote">Remote Only</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">In-Office Only</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Career Interests & Focus</label>
            <input
              type="text"
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
              placeholder="e.g. Machine Learning, Cloud Systems, Data Science, Backend"
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>
        </div>

        {/* Submit Changes */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSaving}
            className="px-6 py-3 rounded-2xl font-bold bg-brand-500 hover:bg-brand-400 disabled:opacity-60 text-slate-950 text-xs transition-colors shadow-lg shadow-brand-500/20 flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            <span>{isSaving ? 'Saving...' : 'Save Profile Changes'}</span>
          </button>
        </div>
      </form>

      {/* Interactive Skill Taxonomy Manager */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-5">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Wrench className="w-4 h-4 text-emerald-400" />
            <span>Skill Inventory ({skills.length})</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Skills are automatically normalized against JobTrail-AI's canonical taxonomy for exact scoring.
          </p>
        </div>

        {/* Add Skill Row */}
        <div className="flex flex-col sm:flex-row gap-2.5">
          <input
            type="text"
            value={newSkillName}
            onChange={(e) => setNewSkillName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSkill())}
            placeholder="Type skill name (e.g. PyTorch, Kubernetes, TypeScript)..."
            className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
          />

          <select
            value={newSkillProficiency}
            onChange={(e) => setNewSkillProficiency(e.target.value)}
            className="px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>

          <button
            type="button"
            onClick={handleAddSkill}
            className="px-5 py-2.5 rounded-xl font-bold bg-slate-800 hover:bg-slate-700 text-white text-xs flex items-center justify-center gap-1.5 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Skill</span>
          </button>
        </div>

        {/* Active Skills List */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 pt-2">
          {skills.map((s) => (
            <div
              key={s.id || s.name}
              className="flex items-center justify-between p-3 rounded-xl bg-slate-950/80 border border-slate-800"
            >
              <div>
                <div className="text-xs font-semibold text-slate-200">{s.name}</div>
                <div className="text-[10px] text-slate-500 capitalize">{s.proficiency} &bull; {s.source}</div>
              </div>

              <button
                type="button"
                onClick={() => handleRemoveSkill(s.name)}
                className="p-1 text-slate-500 hover:text-rose-400 transition-colors"
                title="Remove skill"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
