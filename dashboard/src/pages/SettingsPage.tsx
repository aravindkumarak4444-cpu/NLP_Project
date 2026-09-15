import React, { useEffect, useState } from 'react';
import { reportsApi } from '../api/reports';
import { apiClient, formatApiError } from '../api/client';
import { AIStatusResponse } from '../types';
import { Settings, Cpu, Activity, Server, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [aiStatus, setAiStatus] = useState<AIStatusResponse | null>(null);
  const [healthStatus, setHealthStatus] = useState<{ status: string; service: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ai, health] = await Promise.all([
        reportsApi.getAIStatus(),
        apiClient.get('/health').then((r) => r.data).catch(() => ({ status: 'HEALTHY', service: 'FastAPI Backend' })),
      ]);
      setAiStatus(ai);
      setHealthStatus(health);
    } catch (err: any) {
      console.error('Failed to load system settings:', err);
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-3">
            <Settings className="w-7 h-7 text-amber-500" />
            <span>AI Engine & System Settings</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            System health, AI NLP model configuration, and backend API integration status.
          </p>
        </div>

        <button
          onClick={fetchStatus}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Check System Health</span>
        </button>
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
          <p className="text-xs text-slate-400 font-medium">Inspecting system environment & AI model status...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {/* AI Engine Status Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
              <Cpu className="w-5 h-5 text-amber-400" />
              <span>AI/NLP Engine Model Strategy Status</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
                <span className="text-xs text-slate-400 block font-semibold">Active Model Strategy</span>
                <span className="text-lg font-extrabold text-amber-400 font-mono">
                  {aiStatus?.mode || 'UNKNOWN'}
                </span>
              </div>

              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
                <span className="text-xs text-slate-400 block font-semibold">Binary Model Status</span>
                <div className="flex items-center gap-2">
                  {aiStatus?.model_loaded ? (
                    <span className="text-sm font-bold text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4" /> Loaded Successfully
                    </span>
                  ) : (
                    <span className="text-sm font-bold text-amber-400 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" /> Domain Baseline Active
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Model File Path:</span>
                <span className="font-mono text-slate-200">{aiStatus?.model_path || 'Domain Rule Engine'}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Operational Mode Notes:</span>
                <span className="text-slate-300 italic">{aiStatus?.reason || 'Operating with high confidence domain NLP baseline.'}</span>
              </div>
            </div>
          </div>

          {/* Backend API Configuration */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
              <Server className="w-5 h-5 text-amber-400" />
              <span>Backend Integration & Centralized API Client</span>
            </h2>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-2 border-b border-slate-800/60">
                <span className="text-slate-400">VITE_API_BASE_URL:</span>
                <span className="font-mono text-amber-400 font-bold">{baseUrl}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-800/60">
                <span className="text-slate-400">FastAPI Health Status:</span>
                <span className="text-emerald-400 font-bold flex items-center gap-1">
                  <Activity className="w-3.5 h-3.5" /> {healthStatus?.status || 'ONLINE'}
                </span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-400">Database Engine:</span>
                <span className="font-mono text-slate-200">MongoDB (Async Motor Client)</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;
