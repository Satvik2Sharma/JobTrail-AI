import React from 'react';
import { Sparkles } from 'lucide-react';

interface MatchBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const MatchBadge: React.FC<MatchBadgeProps> = ({ score, size = 'md', showIcon = true }) => {
  let colorClasses = 'bg-slate-800 text-slate-300 border-slate-700';

  if (score >= 85) {
    colorClasses = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-[0_0_12px_rgba(16,185,129,0.15)]';
  } else if (score >= 70) {
    colorClasses = 'bg-teal-500/10 text-teal-300 border-teal-500/30';
  } else if (score >= 50) {
    colorClasses = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  } else {
    colorClasses = 'bg-slate-800/80 text-slate-400 border-slate-700/60';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-sm px-2.5 py-1 gap-1.5',
    lg: 'text-base font-semibold px-3.5 py-1.5 gap-2',
  }[size];

  return (
    <span className={`inline-flex items-center font-medium rounded-full border ${colorClasses} ${sizeClasses}`}>
      {showIcon && <Sparkles className={size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'} />}
      <span>{score}% Match</span>
    </span>
  );
};
