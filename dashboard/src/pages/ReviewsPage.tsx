import React, { useState, useEffect } from 'react';
import { reportsApi } from '../api/reports';
import { workflowApi, SubmitReviewPayload } from '../api/workflow';
import { SafetyReport, User, SIFRiskLevel } from '../types';
import { UserCheck, AlertOctagon, CheckCircle2, FileText, Send, RefreshCw, ShieldAlert, UserPlus } from 'lucide-react';

export const ReviewsPage: React.FC = () => {
  const [reports, setReports] = useState<SafetyReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<SafetyReport | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Review Decision State
  const [decision, setDecision] = useState<'ACCEPT' | 'REJECT' | 'CORRECT'>('ACCEPT');
  const [overrideSif, setOverrideSif] = useState<boolean>(true);
  const [correctedRisk, setCorrectedRisk] = useState<SIFRiskLevel>('HIGH');
  const [hazardCategory, setHazardCategory] = useState<string>('WORKING_AT_HEIGHT');
  const [reason, setReason] = useState<string>('Confirmed after safety inspection.');
  const [assignedTo, setAssignedTo] = useState<string>('');
  const [actionDescription, setActionDescription] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const fetchQueue = async () => {
    setIsLoading(true);
    setMessage(null);
    try {
      const [reportsData, usersData] = await Promise.all([
        reportsApi.listReports({ page: 1, limit: 50, status: 'REVIEW_REQUIRED' }),
        workflowApi.getUsers().catch(() => []),
      ]);
      setReports(reportsData.items);
      setUsers(usersData);
      if (reportsData.items.length > 0) {
        const item = reportsData.items[0];
        setSelectedReport(item);
        setOverrideSif(item.analysis?.sif_precursor ?? true);
        setCorrectedRisk(item.risk?.level || 'HIGH');
        setHazardCategory(item.analysis?.hazard_category || 'WORKING_AT_HEIGHT');
      }
    } catch (err) {
      setMessage({ text: 'Failed to load human review queue.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleSelectReport = (item: SafetyReport) => {
    setSelectedReport(item);
    setOverrideSif(item.analysis?.sif_precursor ?? true);
    setCorrectedRisk(item.risk?.level || 'HIGH');
    setHazardCategory(item.analysis?.hazard_category || 'WORKING_AT_HEIGHT');
  };

  const handleSubmitReview = async () => {
    if (!selectedReport) return;
    setSubmitting(true);
    try {
      const payload: SubmitReviewPayload = {
        report_id: selectedReport.report_id,
        decision,
        corrected_sif: decision === 'CORRECT' ? overrideSif : undefined,
        corrected_risk: decision === 'CORRECT' ? correctedRisk : undefined,
        corrected_hazard: decision === 'CORRECT' ? hazardCategory : undefined,
        correction_reason: reason,
        assigned_to: assignedTo || undefined,
        action_description: actionDescription || undefined,
      };

      await workflowApi.submitReview(payload);
      setMessage({ text: `Review decision '${decision}' submitted for report ${selectedReport.report_id}.`, type: 'success' });
      fetchQueue();
    } catch (err: any) {
      setMessage({ text: 'Failed to submit human review.', type: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
        <div>
          <div className="flex items-center gap-2">
            <UserCheck className="w-6 h-6 text-amber-500" />
            <h1 className="text-xl font-bold text-slate-100">Human-in-the-Loop Review Queue</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Expert safety officer validation for low-confidence AI classifications and precursor overrides.
          </p>
        </div>
        <button
          onClick={fetchQueue}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {message && (
        <div
          className={`p-4 rounded-xl border text-xs font-semibold flex items-center gap-2 ${
            message.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-800 text-emerald-300'
              : 'bg-red-950/40 border-red-800 text-red-300'
          }`}
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>{message.text}</span>
        </div>
      )}

      {/* Main Review Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Queue List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200">Pending Safety Reviews</h2>
            <span className="text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded">
              {reports.length} Pending
            </span>
          </div>

          {isLoading ? (
            <div className="py-12 text-center text-slate-500 text-xs">Loading queue...</div>
          ) : reports.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-xs">No pending items requiring review.</div>
          ) : (
            <div className="space-y-2.5">
              {reports.map((item) => {
                const isSelected = selectedReport?.report_id === item.report_id;
                const isNovel = item.analysis?.is_novel;
                return (
                  <button
                    key={item.report_id}
                    onClick={() => handleSelectReport(item)}
                    className={`w-full text-left p-3.5 rounded-lg border transition-all ${
                      isSelected
                        ? 'bg-amber-500/10 border-amber-500/40 text-slate-100 shadow-sm'
                        : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:bg-slate-800/50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-amber-400">{item.report_id}</span>
                      {isNovel && (
                        <span className="text-[9px] font-mono px-1.5 py-0.5 bg-purple-950 text-purple-300 border border-purple-800 rounded">
                          NOVEL
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-300 line-clamp-2 mt-1.5">{item.description}</p>
                    <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                      <span>Conf: {((item.analysis?.confidence || 0) * 100).toFixed(0)}%</span>
                      <span className="font-semibold text-amber-400">{item.analysis?.hazard_category}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column: Interactive Review Form */}
        <div className="lg:col-span-2 space-y-6">
          {selectedReport ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
                      {selectedReport.report_id}
                    </span>
                    <h2 className="text-base font-bold text-slate-100">Safety Observation Review</h2>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">Location: {selectedReport.location} • Submitted by: {selectedReport.submitted_by}</p>
                </div>
              </div>

              {/* Novel Report Warning Banner */}
              {selectedReport.analysis?.is_novel && (
                <div className="p-4 bg-purple-950/40 border border-purple-800/80 rounded-xl text-xs text-purple-200 space-y-1">
                  <span className="font-bold text-purple-300 flex items-center gap-1.5">
                    <ShieldAlert className="w-4 h-4 text-purple-400" />
                    <span>NOVEL / UNFAMILIAR REPORT DETECTED</span>
                  </span>
                  <p className="text-purple-300/90 leading-relaxed">
                    This report contains vocabulary or hazard patterns that are insufficiently represented in the current training data (Familiarity Score: {selectedReport.analysis.training_familiarity}). Safety Officer review is required.
                  </p>
                </div>
              )}

              {/* Description Box */}
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Original Field Report Description</span>
                <p className="text-xs text-slate-200 leading-relaxed">{selectedReport.description}</p>
              </div>

              {/* Current AI Prediction Summary */}
              {selectedReport.analysis && (
                <div className="p-4 bg-slate-950/60 rounded-lg border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 uppercase">Raw AI Prediction Result</span>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`text-xs font-extrabold px-2 py-0.5 rounded ${
                          selectedReport.analysis.raw_prediction
                            ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        }`}
                      >
                        {selectedReport.analysis.raw_prediction ? 'SIF PRECURSOR' : 'NON-SIF'}
                      </span>
                      <span className="text-xs text-slate-300 font-mono">
                        ({((selectedReport.analysis.raw_confidence || selectedReport.analysis.confidence) * 100).toFixed(0)}% Confidence)
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] font-mono text-slate-400 uppercase">Safety Context Type</span>
                    <p className="text-xs font-bold text-amber-400 mt-1">{selectedReport.analysis.context_type || 'UNKNOWN'}</p>
                  </div>
                </div>
              )}

              {/* Officer Decision Controls */}
              <div className="space-y-4 pt-2 border-t border-slate-800">
                <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Safety Officer Review Decision</h3>

                <div className="grid grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => setDecision('ACCEPT')}
                    className={`py-3 px-2 rounded-lg border text-center font-bold text-xs transition-all ${
                      decision === 'ACCEPT'
                        ? 'bg-emerald-950/60 border-emerald-500 text-emerald-300 shadow-md'
                        : 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-800'
                    }`}
                  >
                    ACCEPT AI RESULT
                  </button>

                  <button
                    type="button"
                    onClick={() => setDecision('CORRECT')}
                    className={`py-3 px-2 rounded-lg border text-center font-bold text-xs transition-all ${
                      decision === 'CORRECT'
                        ? 'bg-amber-950/60 border-amber-500 text-amber-300 shadow-md'
                        : 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-800'
                    }`}
                  >
                    CORRECT RESULT
                  </button>

                  <button
                    type="button"
                    onClick={() => setDecision('REJECT')}
                    className={`py-3 px-2 rounded-lg border text-center font-bold text-xs transition-all ${
                      decision === 'REJECT'
                        ? 'bg-red-950/60 border-red-500 text-red-300 shadow-md'
                        : 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-800'
                    }`}
                  >
                    REJECT REPORT
                  </button>
                </div>

                {decision === 'CORRECT' && (
                  <div className="p-4 bg-slate-950 border border-amber-800/40 rounded-xl space-y-3">
                    <span className="text-xs font-bold text-amber-400 block">Officer Correction Inputs</span>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-[11px] text-slate-400 font-medium block mb-1">Correct SIF Precursor</label>
                        <select
                          value={overrideSif ? 'TRUE' : 'FALSE'}
                          onChange={(e) => setOverrideSif(e.target.value === 'TRUE')}
                          className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                        >
                          <option value="TRUE">TRUE (SIF Precursor)</option>
                          <option value="FALSE">FALSE (Non-SIF)</option>
                        </select>
                      </div>

                      <div>
                        <label className="text-[11px] text-slate-400 font-medium block mb-1">Correct SIF Risk Level</label>
                        <select
                          value={correctedRisk}
                          onChange={(e) => setCorrectedRisk(e.target.value as SIFRiskLevel)}
                          className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                        >
                          <option value="CRITICAL">CRITICAL</option>
                          <option value="HIGH">HIGH</option>
                          <option value="MEDIUM">MEDIUM</option>
                          <option value="LOW">LOW</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 font-medium block mb-1">Correct Hazard Category</label>
                      <select
                        value={hazardCategory}
                        onChange={(e) => setHazardCategory(e.target.value)}
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                      >
                        <option value="WORKING_AT_HEIGHT">WORKING_AT_HEIGHT</option>
                        <option value="CONFINED_SPACE">CONFINED_SPACE</option>
                        <option value="ELECTRICAL_SAFETY">ELECTRICAL_SAFETY</option>
                        <option value="SUSPENDED_LOAD">SUSPENDED_LOAD</option>
                        <option value="PRESSURE_SYSTEMS">PRESSURE_SYSTEMS</option>
                        <option value="HOT_WORK">HOT_WORK</option>
                        <option value="GENERAL_SAFETY">GENERAL_SAFETY</option>
                      </select>
                    </div>
                  </div>
                )}

                <div className="space-y-1">
                  <label className="text-xs text-slate-400 font-medium">Correction Justification / Review Reason</label>
                  <input
                    type="text"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Provide audit justification..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  />
                </div>

                {/* Responsible Person & Corrective Action Section */}
                <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-3">
                  <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                    <UserPlus className="w-4 h-4 text-amber-500" />
                    <span>Assign Responsible Person & Action (Optional)</span>
                  </span>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Select Registered Responsible Person</label>
                      <select
                        value={assignedTo}
                        onChange={(e) => setAssignedTo(e.target.value)}
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200"
                      >
                        <option value="">None (Unassigned)</option>
                        {users.map((u) => (
                          <option key={u.user_id} value={u.username}>
                            {u.full_name} ({u.role} - {u.department})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Action Instruction</label>
                      <input
                        type="text"
                        value={actionDescription}
                        onChange={(e) => setActionDescription(e.target.value)}
                        placeholder="Corrective action description..."
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200"
                      />
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleSubmitReview}
                  disabled={submitting}
                  className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-extrabold text-xs rounded-lg shadow-md transition-transform active:scale-95 disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                  <span>{submitting ? 'Submitting Decision...' : 'Submit Safety Officer Decision'}</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-500 text-xs">
              Select a pending report from the left queue to perform safety review.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReviewsPage;
