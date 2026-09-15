import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { reportsApi } from '../api/reports';
import { formatApiError } from '../api/client';
import { SafetyReport, ActionItem, ActionStatus } from '../types';
import { useAuth } from '../context/AuthContext';
import {
  CheckSquare,
  Search,
  Filter,
  Clock,
  UserCheck,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';

interface ExtractedActionItem extends ActionItem {
  report_id: string;
  report_description: string;
  location: string;
  department: string;
}

export const ActionsPage: React.FC = () => {
  const { user } = useAuth();
  const [actionsList, setActionsList] = useState<ExtractedActionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [search, setSearch] = useState<string>('');
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const fetchActions = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await reportsApi.listReports({ limit: 100 });
      const extracted: ExtractedActionItem[] = [];

      res.items.forEach((r) => {
        if (r.actions && r.actions.length > 0) {
          r.actions.forEach((a) => {
            extracted.push({
              ...a,
              report_id: r.report_id,
              report_description: r.description,
              location: r.location,
              department: r.department,
            });
          });
        }
      });

      setActionsList(extracted);
    } catch (err: any) {
      console.error('Failed to load actions:', err);
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
  }, []);

  const handleStatusChange = async (reportId: string, actionId: string, newStatus: ActionStatus) => {
    setUpdatingId(actionId);
    try {
      await reportsApi.updateActionStatus(reportId, actionId, newStatus);
      await fetchActions();
    } catch (err: any) {
      console.error('Failed to update action status:', err);
      alert(formatApiError(err));
    } finally {
      setUpdatingId(null);
    }
  };

  const filteredActions = actionsList.filter((item) => {
    if (statusFilter !== 'ALL' && item.status !== statusFilter) return false;
    if (search.trim()) {
      const term = search.toLowerCase();
      const matchDesc = item.description.toLowerCase().includes(term);
      const matchReport = item.report_id.toLowerCase().includes(term);
      const matchAssignee = (item.assigned_to || '').toLowerCase().includes(term);
      const matchLoc = item.location.toLowerCase().includes(term);
      return matchDesc || matchReport || matchAssignee || matchLoc;
    }
    return true;
  });

  const isOfficerOrManager = user?.role === 'SAFETY_OFFICER' || user?.role === 'MANAGER' || user?.role === 'ADMIN';

  return (
    <div className="space-y-6">
      {/* Page Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-3">
            <CheckSquare className="w-7 h-7 text-amber-500" />
            <span>HSE Corrective Action Tracker</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Track, assign, and verify corrective action items created for SIF precursors across Oil India Limited sites.
          </p>
        </div>

        <button
          onClick={fetchActions}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh Actions</span>
        </button>
      </div>

      {/* Filters Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-4 shadow-lg">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search actions, assignees, reports..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl py-2 pl-9 pr-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
          />
        </div>

        {/* Status Filter Buttons */}
        <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto">
          {['ALL', 'PENDING', 'IN_PROGRESS', 'COMPLETED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                statusFilter === st
                  ? 'bg-amber-500 text-slate-950 shadow-md'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700'
              }`}
            >
              {st === 'ALL' ? 'All Statuses' : st.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-950/60 border border-red-800 rounded-xl text-xs text-red-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400 font-medium">Loading corrective action items...</p>
        </div>
      ) : filteredActions.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
          <CheckSquare className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-slate-200">No Action Items Found</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            {search || statusFilter !== 'ALL'
              ? 'No action items match your selected filters. Try clearing your search.'
              : 'No corrective actions have been assigned yet. Actions are created within Safety Reports.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filteredActions.map((action) => {
            const isCompleted = action.status === 'COMPLETED';
            const isInProgress = action.status === 'IN_PROGRESS';

            return (
              <div
                key={`${action.report_id}-${action.action_id}`}
                className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-700 transition-colors"
              >
                {/* Action Details */}
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full uppercase tracking-wider font-mono ${
                        isCompleted
                          ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'
                          : isInProgress
                          ? 'bg-amber-950/80 text-amber-400 border border-amber-800'
                          : 'bg-slate-800 text-slate-300 border border-slate-700'
                      }`}
                    >
                      {action.status.replace('_', ' ')}
                    </span>

                    <Link
                      to={`/reports/${action.report_id}`}
                      className="text-xs font-mono font-bold text-amber-400 hover:underline flex items-center gap-1"
                    >
                      <span>{action.report_id}</span>
                      <ExternalLink className="w-3 h-3" />
                    </Link>

                    <span className="text-xs text-slate-500">• {action.location}</span>
                    <span className="text-xs text-slate-500">• {action.department}</span>
                  </div>

                  <p className="text-sm font-semibold text-slate-100">{action.description}</p>

                  <div className="flex items-center gap-4 text-xs text-slate-400 pt-1">
                    <span className="flex items-center gap-1">
                      <UserCheck className="w-3.5 h-3.5 text-amber-500" />
                      <span>Assigned to: <strong className="text-slate-200">{action.assigned_to || 'Unassigned'}</strong></span>
                    </span>

                    {action.due_date && (
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-amber-500" />
                        <span>Due: {new Date(action.due_date).toLocaleDateString()}</span>
                      </span>
                    )}
                  </div>
                </div>

                {/* Status Toggle Buttons */}
                {isOfficerOrManager && (
                  <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
                    {action.status !== 'IN_PROGRESS' && !isCompleted && (
                      <button
                        onClick={() => handleStatusChange(action.report_id, action.action_id, 'IN_PROGRESS')}
                        disabled={updatingId === action.action_id}
                        className="px-3 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 text-xs font-semibold rounded-xl border border-amber-500/30 transition-colors disabled:opacity-50"
                      >
                        Start Action
                      </button>
                    )}

                    {!isCompleted ? (
                      <button
                        onClick={() => handleStatusChange(action.report_id, action.action_id, 'COMPLETED')}
                        disabled={updatingId === action.action_id}
                        className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-semibold rounded-xl border border-emerald-500/30 transition-colors disabled:opacity-50 flex items-center gap-1.5"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Mark Completed</span>
                      </button>
                    ) : (
                      <button
                        onClick={() => handleStatusChange(action.report_id, action.action_id, 'PENDING')}
                        disabled={updatingId === action.action_id}
                        className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-xl border border-slate-700 transition-colors disabled:opacity-50"
                      >
                        Reopen Action
                      </button>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ActionsPage;
