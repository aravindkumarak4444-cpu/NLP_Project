import React from 'react';
import { ReportStatus } from '../types';

interface StatusBadgeProps {
  status: ReportStatus | string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getStyle = (st: string) => {
    switch (st) {
      case 'SUBMITTED':
        return 'bg-blue-950/70 text-blue-400 border-blue-800';
      case 'AI_ANALYZED':
        return 'bg-purple-950/70 text-purple-300 border-purple-800';
      case 'REVIEW_REQUIRED':
        return 'bg-amber-950/70 text-amber-300 border-amber-800';
      case 'ACTION_ASSIGNED':
      case 'IN_PROGRESS':
        return 'bg-cyan-950/70 text-cyan-300 border-cyan-800';
      case 'RESOLVED':
      case 'VERIFIED':
      case 'CLOSED':
        return 'bg-emerald-950/70 text-emerald-400 border-emerald-800';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${getStyle(
        status
      )}`}
    >
      {status.replace(/_/g, ' ')}
    </span>
  );
};
