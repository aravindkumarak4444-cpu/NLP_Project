import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { reportsApi } from '../api/reports';
import { formatApiError } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { SafetyReport, ReportStatus } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { StatusBadge } from '../components/StatusBadge';
import { ModelStatusBadge } from '../components/ModelStatusBadge';
import { ActionItemModal } from '../components/ActionItemModal';
import {
  ShieldAlert,
  Cpu,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  Play,
  PlusCircle,
  FileText,
  Activity,
  Calendar,
  MapPin,
  Building2,
  User as UserIcon,
  Zap,
  ExternalLink,
  Trash2,
} from 'lucide-react';

export const ReportDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [report, setReport] = useState<SafetyReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);

  const fetchReportDetails = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await reportsApi.getReportById(id);
      setReport(data);
    } catch (err: any) {
      console.error('Failed to load report details:', err);
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReportDetails();
  }, [id]);

  const handleTriggerAnalysis = async () => {
    if (!id) return;
    setAnalyzing(true);
    try {
      await reportsApi.analyzeReport(id);
      await fetchReportDetails();
    } catch (err: any) {
      console.error('Failed to execute AI analysis:', err);
      setError(formatApiError(err));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleStatusUpdate = async (newStatus: string) => {
    if (!id) return;
    setUpdatingStatus(true);
    try {
      await reportsApi.updateStatus(id, newStatus);
      await fetchReportDetails();
    } catch (err: any) {
      console.error('Failed to update status:', err);
      alert(formatApiError(err));
    } finally {
      setUpdatingStatus(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-400 flex items-center justify-center gap-2">
        <Activity className="w-5 h-5 animate-spin text-amber-500" />
        <span>Loading Safety Report Details & AI Evaluation...</span>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-xl mx-auto py-12 bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center">
        <AlertTriangle className="w-10 h-10 text-red-400 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-slate-100 mb-2">Error Loading Safety Report</h2>
        <p className="text-xs text-slate-400 mb-6">{error || 'Report with the given ID was not found.'}</p>
        <Link
          to="/reports"
          className="px-4 py-2 bg-amber-500 text-slate-950 font-bold text-xs rounded-xl hover:bg-amber-400 transition-colors"
        >
          Return to Safety Reports
        </Link>
      </div>
    );
  }

  const analysis = report.analysis;
  const risk = report.risk;
  const lsr = report.life_saving_rule;
  const recs = report.recommendations;
  const pattern = report.pattern_data;

  const isOfficerOrManager = user?.role === 'SAFETY_OFFICER' || user?.role === 'MANAGER' || user?.role === 'ADMIN';

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2 flex-wrap">
            <span className="text-xl font-extrabold text-slate-100 font-mono">
              {report.report_id}
            </span>
            <StatusBadge status={report.status} />
            {analysis && (
              <ModelStatusBadge mode={analysis.model_source} loaded={true} />
            )}
          </div>
          <p className="text-xs text-slate-400 flex items-center gap-4 flex-wrap">
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-amber-500" /> {report.location}
            </span>
            <span className="flex items-center gap-1">
              <Building2 className="w-3.5 h-3.5 text-amber-500" /> {report.department}
            </span>
            <span className="flex items-center gap-1">
              <UserIcon className="w-3.5 h-3.5 text-amber-500" /> Submitted by {report.submitted_by}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-amber-500" /> {new Date(report.created_at).toLocaleString()}
            </span>
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Link
            to={`/analysis/${report.report_id}`}
            className="px-3.5 py-2.5 bg-slate-800 hover:bg-slate-700 text-amber-400 font-semibold text-xs rounded-xl border border-slate-700 flex items-center gap-1.5 transition-colors"
          >
            <Cpu className="w-4 h-4" />
            <span>AI Diagnostics Page</span>
            <ExternalLink className="w-3 h-3" />
          </Link>

          <button
            onClick={handleTriggerAnalysis}
            disabled={analyzing}
            className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs rounded-xl transition-colors flex items-center gap-2 shadow-lg shadow-amber-500/10 disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <Activity className="w-4 h-4 animate-spin" />
                <span>Running AI Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>{analysis ? 'Re-run AI Pipeline' : 'Run AI Pipeline'}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Report Status Lifecycle Controls (For Safety Officers / Managers / Admins) */}
      {isOfficerOrManager && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md flex items-center justify-between gap-4 flex-wrap">
          <span className="text-xs font-semibold text-slate-300">Lifecycle Status Control:</span>
          <div className="flex items-center gap-2 flex-wrap">
            {report.status === 'SUBMITTED' && (
              <button
                onClick={() => handleStatusUpdate('REVIEW_REQUIRED')}
                disabled={updatingStatus}
                className="px-3 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg text-xs font-semibold"
              >
                Mark Review Required
              </button>
            )}
            {report.status === 'REVIEW_REQUIRED' && (
              <button
                onClick={() => handleStatusUpdate('ACTION_ASSIGNED')}
                disabled={updatingStatus}
                className="px-3 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg text-xs font-semibold"
              >
                Mark Action Assigned
              </button>
            )}
            {report.status === 'ACTION_ASSIGNED' && (
              <button
                onClick={() => handleStatusUpdate('IN_PROGRESS')}
                disabled={updatingStatus}
                className="px-3 py-1.5 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded-lg text-xs font-semibold"
              >
                Set In Progress
              </button>
            )}
            {report.status === 'IN_PROGRESS' && (
              <button
                onClick={() => handleStatusUpdate('RESOLVED')}
                disabled={updatingStatus}
                className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-lg text-xs font-semibold"
              >
                Mark Resolved
              </button>
            )}
            {report.status === 'RESOLVED' && (
              <button
                onClick={() => handleStatusUpdate('VERIFIED')}
                disabled={updatingStatus}
                className="px-3 py-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded-lg text-xs font-semibold"
              >
                Verify Resolution
              </button>
            )}
            {report.status === 'VERIFIED' && (
              <button
                onClick={() => handleStatusUpdate('CLOSED')}
                disabled={updatingStatus}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg text-xs font-semibold"
              >
                Close Report
              </button>
            )}
          </div>
        </div>
      )}


      {/* Description Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
          <FileText className="w-4 h-4 text-amber-500" />
          Field Observation Description
        </h2>
        <p className="text-sm text-slate-200 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800/80 font-normal">
          {report.description}
        </p>
      </div>

      {/* AI Analysis & SIF Precursor Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Member 1: SIF Precursor Detection */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Cpu className="w-4 h-4 text-amber-500" />
              Member 1: AI/NLP SIF Precursor
            </h2>
            {analysis && (
              <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-800 text-slate-300 rounded">
                {analysis.model_source}
              </span>
            )}
          </div>

          {analysis ? (
            <div className="space-y-4">
              <div className="p-4 rounded-xl border flex items-center justify-between bg-slate-950 border-slate-800">
                <div>
                  <span className="text-xs text-slate-400 block">SIF Precursor Flag</span>
                  <span className={`text-xl font-extrabold ${analysis.sif_precursor ? 'text-red-400' : 'text-emerald-400'}`}>
                    {analysis.sif_precursor ? 'DETECTED' : 'NOT DETECTED'}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-400 block">AI Probability</span>
                  <span className="text-xl font-bold font-mono text-amber-400">
                    {Math.round(analysis.confidence * 100)}%
                  </span>
                </div>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400">Hazard Category:</span>
                  <span className="font-semibold text-slate-200">{analysis.hazard_category}</span>
                </div>
                {analysis.unsafe_act && (
                  <div className="flex justify-between py-1 border-b border-slate-800/50">
                    <span className="text-slate-400">Unsafe Act:</span>
                    <span className="font-semibold text-slate-200">{analysis.unsafe_act}</span>
                  </div>
                )}
                {analysis.unsafe_condition && (
                  <div className="flex justify-between py-1 border-b border-slate-800/50">
                    <span className="text-slate-400">Unsafe Condition:</span>
                    <span className="font-semibold text-slate-200">{analysis.unsafe_condition}</span>
                  </div>
                )}
              </div>

              {analysis.evidence.length > 0 && (
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                    Extracted Evidence
                  </span>
                  <div className="space-y-1">
                    {analysis.evidence.map((ev, i) => (
                      <div key={i} className="text-xs bg-slate-950 p-2 rounded border border-slate-800 text-slate-300">
                        {ev}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="py-8 text-center text-xs text-slate-500">
              AI analysis not executed yet. Click &quot;Run AI Analysis Pipeline&quot; above.
            </div>
          )}
        </div>

        {/* Member 2: Life-Saving Rule & Risk Matrix */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-amber-500" />
              Member 2: Life-Saving Rules & Risk
            </h2>
            {risk && <RiskBadge level={risk.level} score={risk.score} />}
          </div>

          {lsr && risk ? (
            <div className="space-y-4">
              {/* Life Saving Rule Card */}
              <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-800/40">
                <span className="text-[10px] font-mono font-bold text-amber-500 uppercase tracking-wider block mb-1">
                  {lsr.rule_id}
                </span>
                <h3 className="text-sm font-bold text-amber-300">{lsr.rule_name}</h3>
                <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">{lsr.description}</p>
              </div>

              {/* 5x5 Risk Assessment Metrics */}
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase">Severity</span>
                  <span className="text-lg font-bold text-slate-100 font-mono">{risk.severity}/5</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase">Likelihood</span>
                  <span className="text-lg font-bold text-slate-100 font-mono">{risk.likelihood}/5</span>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase">Risk Score</span>
                  <span className="text-lg font-bold text-amber-400 font-mono">{risk.score}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="py-8 text-center text-xs text-slate-500">
              Rule mapping and risk assessment pending.
            </div>
          )}
        </div>

        {/* Member 3: Pattern Analysis */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-500" />
              Member 3: Incident Patterns
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-800 text-slate-300 rounded">
              SQLite Sync
            </span>
          </div>

          {pattern ? (
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-400">Activity Pattern:</span>
                  <span className="font-semibold text-slate-200">{pattern.activity || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Location Pattern:</span>
                  <span className="font-semibold text-slate-200">{pattern.location || 'N/A'}</span>
                </div>
                {pattern.barrier_failure && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">Barrier Failure:</span>
                    <span className="font-semibold text-red-400">{pattern.barrier_failure}</span>
                  </div>
                )}
              </div>

              {pattern.precursor_patterns.length > 0 && (
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                    Precursor Pattern Flags
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {pattern.precursor_patterns.map((pat, idx) => (
                      <span key={idx} className="px-2 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded text-[11px]">
                        {pat}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="py-8 text-center text-xs text-slate-500">
              Pattern analysis data not available.
            </div>
          )}
        </div>
      </div>

      {/* Recommendations Section */}
      {recs && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
          <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            HSE Recommendation Protocol
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="bg-slate-950 p-4 rounded-xl border border-red-900/40 space-y-2">
              <span className="font-bold text-red-400 uppercase block tracking-wider text-[11px]">
                Immediate Actions
              </span>
              <ul className="list-disc list-inside space-y-1.5 text-slate-300">
                {recs.immediate_actions.map((act, i) => (
                  <li key={i}>{act}</li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-950 p-4 rounded-xl border border-amber-900/40 space-y-2">
              <span className="font-bold text-amber-400 uppercase block tracking-wider text-[11px]">
                Preventive Actions
              </span>
              <ul className="list-disc list-inside space-y-1.5 text-slate-300">
                {recs.preventive_actions.map((act, i) => (
                  <li key={i}>{act}</li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-950 p-4 rounded-xl border border-emerald-900/40 space-y-2">
              <span className="font-bold text-emerald-400 uppercase block tracking-wider text-[11px]">
                Verification Actions
              </span>
              <ul className="list-disc list-inside space-y-1.5 text-slate-300">
                {recs.verification_actions.map((act, i) => (
                  <li key={i}>{act}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Action Tracking Management */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Assigned Corrective Actions
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Track resolution progress for required corrective and preventive measures.
            </p>
          </div>

          <button
            onClick={() => setIsActionModalOpen(true)}
            className="px-3.5 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-xl transition-colors flex items-center gap-1.5"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Add Action Item</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Action ID</th>
                <th className="py-3 px-4">Description</th>
                <th className="py-3 px-4">Assigned To</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Target Due Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {report.actions.length > 0 ? (
                report.actions.map((act) => (
                  <tr key={act.action_id} className="hover:bg-slate-800/40">
                    <td className="py-3 px-4 font-mono font-bold text-slate-200">{act.action_id}</td>
                    <td className="py-3 px-4 text-slate-200">{act.description}</td>
                    <td className="py-3 px-4 text-slate-400">{act.assigned_to || 'Unassigned'}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950/80 text-amber-400 border border-amber-800">
                        {act.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      {act.due_date ? new Date(act.due_date).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-6 text-center text-slate-500">
                    No corrective actions assigned yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Item Modal */}
      <ActionItemModal
        reportId={report.report_id}
        isOpen={isActionModalOpen}
        onClose={() => setIsActionModalOpen(false)}
        onSuccess={fetchReportDetails}
      />
    </div>
  );
};
