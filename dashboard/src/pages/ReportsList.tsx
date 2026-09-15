import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { reportsApi, ReportQueryParams } from '../api/reports';
import { SafetyReport } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { StatusBadge } from '../components/StatusBadge';
import {
  FileText,
  Search,
  Filter,
  PlusCircle,
  ShieldAlert,
  ChevronLeft,
  ChevronRight,
  Activity,
} from 'lucide-react';

export const ReportsList: React.FC = () => {
  const [reports, setReports] = useState<SafetyReport[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [reportType, setReportType] = useState('');
  const [status, setStatus] = useState('');
  const [riskLevel, setRiskLevel] = useState('');
  const [sifOnly, setSifOnly] = useState(false);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const params: ReportQueryParams = {
        page,
        limit: 10,
        search: search || undefined,
        report_type: reportType || undefined,
        status: status || undefined,
        risk_level: riskLevel || undefined,
        sif_precursor: sifOnly ? true : undefined,
      };

      const res = await reportsApi.listReports(params);
      setReports(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error('Failed to fetch reports:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [page, reportType, status, riskLevel, sifOnly]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchReports();
  };

  return (
    <div className="space-y-6">
      {/* Top Title & CTA */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-amber-500" />
            Safety Incident & Hazard Reports
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Browse, search, and manage submitted Unsafe Acts, Unsafe Conditions, and Near Miss reports.
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

      {/* Filter Controls Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
          {/* Search Box */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search description, report ID, location..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2.5 pl-9 pr-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
            />
          </div>

          <button
            type="submit"
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
          >
            Search
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-slate-800/80">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-semibold mr-2">
            <Filter className="w-3.5 h-3.5 text-amber-500" />
            <span>Filters:</span>
          </div>

          {/* Type Filter */}
          <select
            value={reportType}
            onChange={(e) => {
              setReportType(e.target.value);
              setPage(1);
            }}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-amber-500"
          >
            <option value="">All Report Types</option>
            <option value="UNSAFE_ACT">Unsafe Act</option>
            <option value="UNSAFE_CONDITION">Unsafe Condition</option>
            <option value="NEAR_MISS">Near Miss</option>
          </select>

          {/* Status Filter */}
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-amber-500"
          >
            <option value="">All Statuses</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="AI_ANALYZED">AI Analyzed</option>
            <option value="REVIEW_REQUIRED">Review Required</option>
            <option value="ACTION_ASSIGNED">Action Assigned</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
          </select>

          {/* Risk Level Filter */}
          <select
            value={riskLevel}
            onChange={(e) => {
              setRiskLevel(e.target.value);
              setPage(1);
            }}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-amber-500"
          >
            <option value="">All SIF Risk Levels</option>
            <option value="CRITICAL">Critical Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="LOW">Low Risk</option>
          </select>

          {/* SIF Only Checkbox */}
          <label className="flex items-center gap-2 text-xs font-semibold text-amber-400 bg-amber-950/40 border border-amber-800/40 px-3 py-1.5 rounded-lg cursor-pointer">
            <input
              type="checkbox"
              checked={sifOnly}
              onChange={(e) => {
                setSifOnly(e.target.checked);
                setPage(1);
              }}
              className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-0"
            />
            <span>SIF Precursors Only</span>
          </label>
        </div>
      </div>

      {/* Reports Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="py-16 text-center text-slate-400 flex items-center justify-center gap-2">
            <Activity className="w-5 h-5 animate-spin text-amber-500" />
            <span>Fetching Safety Reports...</span>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800">
                  <tr>
                    <th className="py-3.5 px-4">Report ID</th>
                    <th className="py-3.5 px-4">Type</th>
                    <th className="py-3.5 px-4">Description</th>
                    <th className="py-3.5 px-4">Location</th>
                    <th className="py-3.5 px-4">Department</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4">SIF Precursor</th>
                    <th className="py-3.5 px-4">Risk Level</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {reports.length > 0 ? (
                    reports.map((report) => (
                      <tr key={report.report_id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3.5 px-4 font-mono font-bold text-slate-100">
                          {report.report_id}
                        </td>
                        <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400">
                          {report.report_type}
                        </td>
                        <td className="py-3.5 px-4 max-w-xs truncate text-slate-200">
                          {report.description}
                        </td>
                        <td className="py-3.5 px-4 text-slate-400">{report.location}</td>
                        <td className="py-3.5 px-4 text-slate-400">{report.department}</td>
                        <td className="py-3.5 px-4">
                          <StatusBadge status={report.status} />
                        </td>
                        <td className="py-3.5 px-4">
                          {report.analysis?.sif_precursor ? (
                            <span className="inline-flex items-center gap-1 font-bold text-red-400">
                              <ShieldAlert className="w-3.5 h-3.5 text-red-500" /> SIF
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
                            className="px-3 py-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded font-semibold text-xs transition-colors"
                          >
                            View & Analyze
                          </Link>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={9} className="py-12 text-center text-slate-500">
                        No safety reports match your search filter parameters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="bg-slate-950 px-4 py-3 border-t border-slate-800 flex items-center justify-between">
              <span className="text-xs text-slate-400">
                Showing {reports.length} of {total} safety reports (Page {page} of {totalPages})
              </span>

              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded disabled:opacity-40 transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded disabled:opacity-40 transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
