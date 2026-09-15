import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { reportsApi } from '../api/reports';
import { formatApiError } from '../api/client';
import { SafetyReport, AnalysisResponse, AIStatusResponse } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { ModelStatusBadge } from '../components/ModelStatusBadge';
import {
  BrainCircuit,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  ArrowLeft,
  RefreshCw,
  FileText,
  ShieldAlert,
  ListOrdered,
  BookOpen,
} from 'lucide-react';

export const AnalysisDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<SafetyReport | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [aiStatus, setAiStatus] = useState<AIStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalysisData = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [repData, statusData] = await Promise.all([
        reportsApi.getReportById(id),
        reportsApi.getAIStatus(),
      ]);
      setReport(repData);
      setAiStatus(statusData);

      if (!repData.analysis) {
        // Trigger auto-analysis if not yet run
        const res = await reportsApi.analyzeReport(id);
        setAnalysis(res);
        setReport((prev) => (prev ? { ...prev, analysis: res.analysis, risk: res.risk, life_saving_rule: res.life_saving_rule, recommendations: res.recommendations } : prev));
      }
    } catch (err: any) {
      console.error('Failed to fetch analysis:', err);
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysisData();
  }, [id]);

  const handleReRunAnalysis = async () => {
    if (!id) return;
    setAnalyzing(true);
    setError(null);
    try {
      const res = await reportsApi.analyzeReport(id);
      setAnalysis(res);
      const updated = await reportsApi.getReportById(id);
      setReport(updated);
    } catch (err: any) {
      console.error('Re-analysis error:', err);
      setError(formatApiError(err));
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <div className="w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 font-medium text-sm">Running AI/NLP Pipeline Analysis for {id}...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-4xl mx-auto p-6 bg-red-950/40 border border-red-800 rounded-2xl text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto" />
        <h2 className="text-lg font-bold text-slate-100">AI Analysis Error</h2>
        <p className="text-sm text-red-300">{error || 'Report not found'}</p>
        <Link
          to="/reports"
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Reports</span>
        </Link>
      </div>
    );
  }

  const currentAnalysis = report.analysis;
  const currentRisk = report.risk;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Link to={`/reports/${report.report_id}`} className="text-xs text-amber-400 hover:underline flex items-center gap-1 font-mono">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Report {report.report_id}</span>
            </Link>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-3">
            <BrainCircuit className="w-7 h-7 text-amber-500" />
            <span>AI/NLP SIF Precursor Intelligence</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Model inference analysis & precursor evidence phrase extraction for Report ID: <span className="font-mono text-slate-200">{report.report_id}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          {aiStatus && <ModelStatusBadge mode={aiStatus.mode} loaded={aiStatus.model_loaded} />}

          <button
            onClick={handleReRunAnalysis}
            disabled={analyzing}
            className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs rounded-xl transition-all shadow-md disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${analyzing ? 'animate-spin' : ''}`} />
            <span>{analyzing ? 'Re-analyzing...' : 'Re-Run AI Engine'}</span>
          </button>
        </div>
      </div>

      {/* SIF Precursor & Confidence Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* SIF Precursor Banner */}
        <div className={`p-6 rounded-2xl border ${currentAnalysis?.sif_precursor ? 'bg-red-950/30 border-red-800' : 'bg-emerald-950/30 border-emerald-800'} space-y-2`}>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block">SIF Precursor Status</span>
          <div className="flex items-center gap-3">
            {currentAnalysis?.sif_precursor ? (
              <>
                <AlertTriangle className="w-8 h-8 text-red-500 animate-pulse" />
                <div>
                  <span className="text-xl font-extrabold text-red-400 block">SIF PRECURSOR DETECTED</span>
                  <span className="text-xs text-red-300">High severity precursor indicators found</span>
                </div>
              </>
            ) : (
              <>
                <CheckCircle2 className="w-8 h-8 text-emerald-500" />
                <div>
                  <span className="text-xl font-extrabold text-emerald-400 block">NO SIF PRECURSOR</span>
                  <span className="text-xs text-emerald-300">Standard operational observation</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* AI Model Confidence */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block">AI Confidence Score</span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-amber-400 font-mono">
              {currentAnalysis ? `${Math.round(currentAnalysis.confidence * 100)}%` : '0%'}
            </span>
            <span className="text-xs text-slate-400">Probability score</span>
          </div>
          <p className="text-[11px] text-slate-500 italic">
            Statistical model certainty for extracted precursor features.
          </p>
        </div>

        {/* Risk Assessment (Distinguished from AI Confidence) */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block">Matrix Risk Level</span>
          <div className="flex items-center justify-between">
            {currentRisk ? <RiskBadge level={currentRisk.level} /> : <span className="text-xs text-slate-500">Uncalculated</span>}
            <span className="text-xs text-slate-400 font-mono">Score: {currentRisk?.score || 0} / 25</span>
          </div>
          <div className="text-[11px] text-slate-400 pt-1">
            Likelihood ({currentRisk?.likelihood || 0}) × Severity ({currentRisk?.severity || 0})
          </div>
        </div>
      </div>

      {/* Deep AI Analysis Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Model Execution Details */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
            <Cpu className="w-5 h-5 text-amber-400" />
            <span>Extracted Hazard Parameters</span>
          </h2>

          <div className="space-y-3 text-sm">
            <div className="flex justify-between py-2 border-b border-slate-800/60">
              <span className="text-slate-400">Hazard Category:</span>
              <span className="font-bold text-amber-400">{currentAnalysis?.hazard_category || 'UNCLASSIFIED'}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800/60">
              <span className="text-slate-400">Unsafe Act:</span>
              <span className="font-medium text-slate-200">{currentAnalysis?.unsafe_act || 'None Detected'}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800/60">
              <span className="text-slate-400">Unsafe Condition:</span>
              <span className="font-medium text-slate-200">{currentAnalysis?.unsafe_condition || 'None Detected'}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800/60">
              <span className="text-slate-400">Safety Context Type:</span>
              <span className="font-mono text-xs px-2 py-0.5 bg-slate-800 text-emerald-400 rounded uppercase">
                {currentAnalysis?.context_type || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800/60">
              <span className="text-slate-400">Raw ML Model Prediction:</span>
              <span className="font-mono text-xs px-2 py-0.5 bg-slate-800 text-slate-300 rounded">
                {currentAnalysis?.raw_prediction !== undefined
                  ? (currentAnalysis.raw_prediction ? 'SIF PRECURSOR' : 'NON-SIF')
                  : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800/60">
              <span className="text-slate-400">Model Engine Source:</span>
              <span className="font-mono text-xs px-2 py-0.5 bg-slate-800 text-amber-400 rounded">
                {currentAnalysis?.model_source || 'FALLBACK'}
              </span>
            </div>
          </div>

          {currentAnalysis?.context_adjustment_reason && (
            <div className="p-3.5 bg-amber-950/40 border border-amber-800/60 rounded-xl text-xs text-amber-300 space-y-1">
              <span className="font-bold text-amber-400 block flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5" />
                <span>Explainable Safety Context:</span>
              </span>
              <p className="leading-relaxed text-amber-200/90">{currentAnalysis.context_adjustment_reason}</p>
            </div>
          )}
        </div>

        {/* Evidence Phrases */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
            <ListOrdered className="w-5 h-5 text-amber-400" />
            <span>Extracted Evidence Phrases</span>
          </h2>

          {currentAnalysis?.evidence && currentAnalysis.evidence.length > 0 ? (
            <ul className="space-y-2">
              {currentAnalysis.evidence.map((phrase, idx) => (
                <li key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                  <span>{phrase}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-500 italic">No specific evidence phrases extracted.</p>
          )}
        </div>
      </div>

      {/* Original Safety Report Text */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
        <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
          <FileText className="w-5 h-5 text-amber-400" />
          <span>Analyzed Report Description</span>
        </h2>
        <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-300 whitespace-pre-wrap leading-relaxed font-sans">
          {report.description}
        </div>
      </div>
    </div>
  );
};

export default AnalysisDetail;
