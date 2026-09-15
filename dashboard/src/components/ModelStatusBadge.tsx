import React from 'react';
import { Cpu, CheckCircle2, AlertOctagon } from 'lucide-react';

interface ModelStatusBadgeProps {
  mode?: string;
  loaded?: boolean;
}

export const ModelStatusBadge: React.FC<ModelStatusBadgeProps> = ({ mode, loaded = true }) => {
  if (mode === 'REAL_MODEL' || mode === 'PREDICT_SCRIPT') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-300 border border-emerald-800">
        <Cpu className="w-3.5 h-3.5 text-emerald-400" />
        AI MODEL ONLINE ({mode})
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-300 border border-amber-800">
      <AlertOctagon className="w-3.5 h-3.5 text-amber-400" />
      FALLBACK NLP ENGINE
    </span>
  );
};
