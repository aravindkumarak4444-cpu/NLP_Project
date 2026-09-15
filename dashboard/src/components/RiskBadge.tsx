import React from 'react';
import { SIFRiskLevel } from '../types';
import { ShieldAlert, AlertTriangle, AlertCircle, CheckCircle2 } from 'lucide-react';

interface RiskBadgeProps {
  level?: SIFRiskLevel | string;
  score?: number;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score }) => {
  if (!level) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
        UNASSESSED
      </span>
    );
  }

  const normalized = level.toUpperCase();

  switch (normalized) {
    case 'CRITICAL':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-red-950/80 text-red-400 border border-red-800/80 shadow-sm shadow-red-950">
          <ShieldAlert className="w-3.5 h-3.5 text-red-500 animate-pulse" />
          CRITICAL {score ? `(${score})` : ''}
        </span>
      );
    case 'HIGH':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-orange-950/80 text-orange-400 border border-orange-800/80 shadow-sm shadow-orange-950">
          <AlertTriangle className="w-3.5 h-3.5 text-orange-400" />
          HIGH {score ? `(${score})` : ''}
        </span>
      );
    case 'MEDIUM':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-300 border border-amber-800/80">
          <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
          MEDIUM {score ? `(${score})` : ''}
        </span>
      );
    case 'LOW':
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-950/80 text-emerald-400 border border-emerald-800/80">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          LOW {score ? `(${score})` : ''}
        </span>
      );
  }
};
