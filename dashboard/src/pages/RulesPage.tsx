import React, { useState, useEffect } from 'react';
import { rulesApi } from '../api/rules';
import { RuleResponse } from '../types';
import { BookOpen, ShieldCheck, Tag, Activity } from 'lucide-react';

export const RulesPage: React.FC = () => {
  const [rules, setRules] = useState<RuleResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRules = async () => {
      try {
        setLoading(true);
        const data = await rulesApi.getRules();
        setRules(data);
      } catch (err) {
        console.error('Failed to fetch rules:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRules();
  }, []);

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-400 flex items-center justify-center gap-2">
        <Activity className="w-5 h-5 animate-spin text-amber-500" />
        <span>Fetching Mandatory Life-Saving Rules...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-500">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold text-slate-100">
              Oil India Limited — Life-Saving Rules Catalog
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Official Life-Saving Rules mapped by Member 2 NLP Engine to prevent serious injuries and fatalities.
            </p>
          </div>
        </div>
      </div>

      {/* Rules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {rules.map((rule) => (
          <div
            key={rule.rule_id}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between hover:border-amber-500/40 transition-colors"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-amber-400 bg-amber-950/60 border border-amber-800 px-2.5 py-0.5 rounded">
                  {rule.rule_id}
                </span>
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>

              <h2 className="text-sm font-bold text-slate-100">{rule.rule_name}</h2>
              <p className="text-xs text-slate-300 leading-relaxed">{rule.description}</p>
            </div>

            {rule.hazard_categories && rule.hazard_categories.length > 0 && (
              <div className="pt-4 mt-4 border-t border-slate-800/80">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                  <Tag className="w-3 h-3 text-amber-500" /> Linked Hazard Categories
                </span>
                <div className="flex flex-wrap gap-1">
                  {rule.hazard_categories.map((cat, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-slate-950 text-slate-400 border border-slate-800 rounded text-[10px] font-mono"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
