import React, { useEffect, useState } from 'react';
import { dashboardApi } from '../api/dashboard';
import { PatternAnalysisResult } from '../types';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import {
  TrendingUp,
  AlertTriangle,
  MapPin,
  Building2,
  Activity,
  Layers,
  Zap,
  CheckCircle2,
} from 'lucide-react';

export const PatternsPage: React.FC = () => {
  const [data, setData] = useState<PatternAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPatterns();
  }, []);

  const fetchPatterns = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await dashboardApi.getPatterns();
      setData(res);
    } catch (err: any) {
      console.error('Failed to load pattern analysis:', err);
      setError('Failed to load pattern intelligence data from backend.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-amber-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 font-medium">Analyzing incident patterns across OIL facilities...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 bg-red-50 text-red-700 rounded-lg border border-red-200">
        <h3 className="font-semibold text-lg mb-2">Error Loading Pattern Intelligence</h3>
        <p>{error || 'No pattern data available.'}</p>
        <button
          onClick={fetchPatterns}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm font-medium"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-gradient-to-r from-amber-900 via-yellow-900 to-amber-800 rounded-xl p-6 text-white shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/20 border border-amber-400/30 rounded-full text-amber-300 text-xs font-semibold uppercase tracking-wider mb-2">
              <Zap className="w-3.5 h-3.5" /> Member 3 Pattern Intelligence Engine
            </div>
            <h1 className="text-2xl font-bold">SIF Precursor Pattern Analytics</h1>
            <p className="text-amber-200 text-sm mt-1 max-w-2xl">
              Automated precursor pattern matching, high-risk location cluster identification, and systemic barrier failure detection across Oil India Limited operations.
            </p>
          </div>
          <div className="hidden md:flex items-center gap-3 bg-white/10 p-4 rounded-xl backdrop-blur-sm border border-white/10">
            <Activity className="w-8 h-8 text-amber-400" />
            <div>
              <div className="text-xs text-amber-200">Systemic Patterns</div>
              <div className="text-xl font-bold">{data.repeated_patterns.length} Active Triggers</div>
            </div>
          </div>
        </div>
      </div>

      {/* SIF Trend Chart */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-amber-600" />
              SIF Precursor Monthly Trend Analysis
            </h2>
            <p className="text-xs text-gray-500">
              Tracking monthly volume of total reports vs SIF precursor findings
            </p>
          </div>
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.sif_trends} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="colorSif" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#DC2626" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#DC2626" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="total_reports"
                name="Total Reports"
                stroke="#3B82F6"
                fillOpacity={1}
                fill="url(#colorTotal)"
              />
              <Area
                type="monotone"
                dataKey="sif_count"
                name="SIF Precursors"
                stroke="#DC2626"
                fillOpacity={1}
                fill="url(#colorSif)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Grid of Hazard Categories & Unsafe Acts/Conditions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Hazard Categories */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h2 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Layers className="w-5 h-5 text-amber-600" />
            Top Hazard Categories
          </h2>
          <div className="space-y-3">
            {data.top_hazards.length === 0 ? (
              <p className="text-sm text-gray-500">No hazard category data available.</p>
            ) : (
              data.top_hazards.map((item, idx) => {
                const maxCount = Math.max(...data.top_hazards.map((h) => h.count), 1);
                const pct = Math.round((item.count / maxCount) * 100);
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-sm font-medium">
                      <span className="text-gray-800">{item.name}</span>
                      <span className="text-amber-700 font-bold">{item.count}</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-amber-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${pct}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Top Unsafe Acts */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h2 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            Top Unsafe Acts
          </h2>
          <div className="space-y-3">
            {data.top_unsafe_acts.length === 0 ? (
              <p className="text-sm text-gray-500">No unsafe acts recorded.</p>
            ) : (
              data.top_unsafe_acts.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2.5 bg-red-50/50 rounded-lg border border-red-100"
                >
                  <span className="text-sm text-gray-800 font-medium">{item.name}</span>
                  <span className="px-2.5 py-0.5 bg-red-100 text-red-800 font-semibold text-xs rounded-full">
                    {item.count} occurrences
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Top Unsafe Conditions */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h2 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            Top Unsafe Conditions
          </h2>
          <div className="space-y-3">
            {data.top_unsafe_conditions.length === 0 ? (
              <p className="text-sm text-gray-500">No unsafe conditions recorded.</p>
            ) : (
              data.top_unsafe_conditions.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2.5 bg-orange-50/50 rounded-lg border border-orange-100"
                >
                  <span className="text-sm text-gray-800 font-medium">{item.name}</span>
                  <span className="px-2.5 py-0.5 bg-orange-100 text-orange-800 font-semibold text-xs rounded-full">
                    {item.count} occurrences
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* High-Risk Locations & High-Risk Departments */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Locations */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h2 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-blue-600" />
            High-Risk Locations
          </h2>
          <div className="space-y-3">
            {data.high_risk_locations.map((loc, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm">
                    #{idx + 1}
                  </div>
                  <span className="text-sm font-semibold text-gray-800">{loc.name}</span>
                </div>
                <span className="px-3 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-bold">
                  {loc.count} incidents
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Departments */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h2 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-purple-600" />
            High-Risk Operational Departments
          </h2>
          <div className="space-y-3">
            {data.high_risk_departments.map((dept, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-sm">
                    #{idx + 1}
                  </div>
                  <span className="text-sm font-semibold text-gray-800">{dept.name}</span>
                </div>
                <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-bold">
                  {dept.count} incidents
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Repeated Incident Patterns */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <div className="mb-4">
          <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-600" />
            Systemic & Repeated Incident Patterns
          </h2>
          <p className="text-xs text-gray-500">
            Automatically identified precursor pattern clusters requiring preventative engineering & administrative controls
          </p>
        </div>

        {data.repeated_patterns.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg border border-dashed border-gray-300">
            <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
            <p className="text-gray-600 font-medium">No systemic repeated incident patterns detected in current dataset.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.repeated_patterns.map((pat, idx) => (
              <div
                key={idx}
                className="p-4 bg-amber-50/40 border border-amber-200/80 rounded-xl hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="px-2.5 py-0.5 bg-amber-100 text-amber-800 font-bold text-xs rounded-md uppercase tracking-wider">
                    {pat.pattern_type}
                  </span>
                  <span className="text-xs font-semibold text-amber-900 bg-amber-200/70 px-2 py-0.5 rounded-full">
                    {pat.occurrence_count} Occurrences
                  </span>
                </div>
                <p className="text-sm text-gray-800 font-semibold mb-2">{pat.description}</p>
                <div className="text-xs text-gray-600 flex items-center gap-1.5">
                  <span className="font-medium text-gray-500">Affected Scope:</span>
                  <span className="bg-white px-2 py-0.5 rounded border border-gray-200 font-mono text-gray-700">
                    {pat.affected_entity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
