import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardApi } from '../api/dashboard';
import { reportsApi } from '../api/reports';
import {
  DashboardSummaryResponse,
  SafetyReport,
  TrendPoint,
  AIStatusResponse,
} from '../types';
import { StatCard } from '../components/StatCard';
import { RiskBadge } from '../components/RiskBadge';
import { StatusBadge } from '../components/StatusBadge';
import { ModelStatusBadge } from '../components/ModelStatusBadge';
import {
  ShieldAlert,
  AlertTriangle,
  FileText,
  CheckCircle2,
  TrendingUp,
  PlusCircle,
  ArrowRight,
  Activity,
  Zap,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts';

import { useAuth } from '../context/AuthContext';
import { workflowApi } from '../api/workflow';
import { AssignedAction } from '../types';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const isWorker = user?.role === 'WORKER';

  const [summary, setSummary] = useState<DashboardSummaryResponse | null>(null);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [recentReports, setRecentReports] = useState<SafetyReport[]>([]);
  const [myActions, setMyActions] = useState<AssignedAction[]>([]);
  const [aiStatus, setAIStatus] = useState<AIStatusResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        if (isWorker) {
          const [reportsData, actionsData, statusData] = await Promise.all([
            reportsApi.getMyReports({ page: 1, limit: 10 }),
            workflowApi.getMyActions(),
            reportsApi.getAIStatus(),
          ]);
          setRecentReports(reportsData.items);
          setMyActions(actionsData);
          setAIStatus(statusData);
        } else {
          const [sumData, trendData, reportsData, statusData] = await Promise.all([
            dashboardApi.getSummary(),
            dashboardApi.getTrends(),
            reportsApi.listReports({ page: 1, limit: 5 }),
            reportsApi.getAIStatus(),
          ]);
          setSummary(sumData);
          setTrends(trendData.sif_trends);
          setRecentReports(reportsData.items);
          setAIStatus(statusData);
        }
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [isWorker]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-400 gap-2">
        <Activity className="w-5 h-5 animate-spin text-amber-500" />
        <span>Loading HSE Analytics Dashboard...</span>
      </div>
    );
  }

  if (isWorker) {
    return (
      <div className="space-y-8">
        {/* Worker Top Banner */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-xl font-extrabold text-slate-100">
                Welcome back, {user?.full_name || user?.username}
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded font-bold">
                WORKER PORTAL
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Personal HSE Safety Portal for submitting observations and tracking assigned corrective actions ({user?.department}).
            </p>
          </div>

          <Link
            to="/reports/new"
            className="px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-xl transition-colors flex items-center gap-2 shadow-lg shadow-amber-500/10 self-start sm:self-auto"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Submit Safety Report</span>
          </Link>
        </div>

        {/* Worker Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="My Submitted Reports"
            value={recentReports.length}
            subtitle="Observations submitted by you"
            icon={<FileText className="w-5 h-5 text-blue-400" />}
            borderAccent="border-blue-900/50"
          />
          <StatCard
            title="Under Review"
            value={recentReports.filter((r) => r.status === 'REVIEW_REQUIRED' || r.status === 'SUBMITTED').length}
            subtitle="Safety Officer evaluation pending"
            icon={<Activity className="w-5 h-5 text-amber-400" />}
            borderAccent="border-amber-900/50"
          />
          <StatCard
            title="Analyzed Reports"
            value={recentReports.filter((r) => r.status !== 'SUBMITTED').length}
            subtitle="Evaluated by AI Engine"
            icon={<CheckCircle2 className="w-5 h-5 text-emerald-400" />}
            borderAccent="border-emerald-900/50"
          />
          <StatCard
            title="My Assigned Actions"
            value={myActions.length}
            subtitle={`${myActions.filter((a) => a.status === 'COMPLETED').length} Completed`}
            icon={<Zap className="w-5 h-5 text-purple-400" />}
            borderAccent="border-purple-900/50"
          />
        </div>

        {/* Worker My Reports Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              My Recent Safety Reports
            </h2>
            <Link to="/reports" className="text-xs font-semibold text-amber-400 hover:underline flex items-center gap-1">
              <span>View All My Reports</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Report ID</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentReports.length > 0 ? (
                  recentReports.map((report) => (
                    <tr key={report.report_id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-semibold text-slate-200">{report.report_id}</td>
                      <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400">{report.report_type}</td>
                      <td className="py-3.5 px-4 max-w-xs truncate text-slate-300">{report.description}</td>
                      <td className="py-3.5 px-4 text-slate-400">{report.location}</td>
                      <td className="py-3.5 px-4"><StatusBadge status={report.status} /></td>
                      <td className="py-3.5 px-4 text-right">
                        <Link to={`/reports/${report.report_id}`} className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded text-xs transition-colors">
                          View
                        </Link>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-500">
                      You have not submitted any safety reports yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }

  const criticalCount = summary?.risk_breakdown.critical || 0;
  const highCount = summary?.risk_breakdown.high || 0;

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-xl font-extrabold text-slate-100">
              HSE Incident & SIF Precursor Intelligence Dashboard
            </h1>
            {aiStatus && <ModelStatusBadge mode={aiStatus.mode} loaded={aiStatus.model_loaded} />}
          </div>
          <p className="text-xs text-slate-400">
            Real-time Serious Injury & Fatality (SIF) precursor detection engine & Oil India Limited safety analytics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/reports/new"
            className="px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-xl transition-colors flex items-center gap-2 shadow-lg shadow-amber-500/10"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Submit Safety Report</span>
          </Link>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Safety Reports"
          value={summary?.total_reports || 0}
          subtitle="Unsafe Acts, Conditions & Near Misses"
          icon={<FileText className="w-5 h-5 text-blue-400" />}
          borderAccent="border-blue-900/50"
        />

        <StatCard
          title="SIF Precursors Detected"
          value={summary?.sif_precursor_count || 0}
          subtitle={`${summary?.sif_precursor_percentage || 0}% precursor detection rate`}
          icon={<ShieldAlert className="w-5 h-5 text-red-500" />}
          borderAccent="border-red-900/50"
        />

        <StatCard
          title="Critical / High Risk"
          value={criticalCount + highCount}
          subtitle={`${criticalCount} Critical • ${highCount} High`}
          icon={<AlertTriangle className="w-5 h-5 text-orange-400" />}
          borderAccent="border-orange-900/50"
        />

        <StatCard
          title="Corrective Actions Open"
          value={summary?.actions.open_actions || 0}
          subtitle={`${summary?.actions.resolved_actions || 0} Resolved Actions`}
          icon={<CheckCircle2 className="w-5 h-5 text-emerald-400" />}
          borderAccent="border-emerald-900/50"
        />
      </div>

      {/* Analytics Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SIF Precursor Trend Chart */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-amber-500" />
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                SIF Precursor Incident Trends Over Time
              </h2>
            </div>
            <span className="text-[11px] text-slate-400 font-mono">Monthly Aggregation</span>
          </div>

          <div className="h-64">
            {trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="sifColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="period" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                    labelStyle={{ color: '#f8fafc', fontWeight: 'bold', fontSize: '12px' }}
                  />
                  <Area type="monotone" dataKey="sif_count" name="SIF Precursors" stroke="#f59e0b" fillOpacity={1} fill="url(#sifColor)" />
                  <Area type="monotone" dataKey="total_reports" name="Total Reports" stroke="#38bdf8" fillOpacity={0} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No trend data available yet.
              </div>
            )}
          </div>
        </div>

        {/* Hazard Categories Breakdown */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-4 h-4 text-amber-500" />
            <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Top Incident Locations
            </h2>
          </div>

          <div className="h-64">
            {summary?.reports_by_location && summary.reports_by_location.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={summary.reports_by_location.slice(0, 5)} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis type="number" stroke="#94a3b8" fontSize={11} />
                  <YAxis type="category" dataKey="name" stroke="#94a3b8" fontSize={10} width={80} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                  <Bar dataKey="count" name="Incidents" fill="#0284c7" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No location data registered.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Safety Reports Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Recent Safety Reports
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Latest field submissions evaluated by the SIF precursor engine.
            </p>
          </div>
          <Link
            to="/reports"
            className="text-xs font-semibold text-amber-400 hover:text-amber-300 flex items-center gap-1 transition-colors"
          >
            <span>View All Reports</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Report ID</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Description</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">SIF Precursor</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {recentReports.length > 0 ? (
                recentReports.map((report) => (
                  <tr key={report.report_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-200">
                      {report.report_id}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400">
                      {report.report_type}
                    </td>
                    <td className="py-3.5 px-4 max-w-xs truncate text-slate-300">
                      {report.description}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">{report.location}</td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={report.status} />
                    </td>
                    <td className="py-3.5 px-4">
                      {report.analysis?.sif_precursor ? (
                        <span className="inline-flex items-center gap-1 font-bold text-red-400">
                          <ShieldAlert className="w-3.5 h-3.5" /> YES
                        </span>
                      ) : (
                        <span className="text-slate-500 font-medium">No</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <RiskBadge level={report.risk?.level} score={report.risk?.score} />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        to={`/reports/${report.report_id}`}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded text-xs transition-colors"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">
                    No safety reports created yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
