import React, { useState, useEffect } from 'react';
import { getModels, getActiveModel, activateModel, trainModel, RegisteredModel } from '../api/ml';
import { Cpu, CheckCircle2, Play, Award, Zap, RefreshCw, BarChart2, ShieldCheck } from 'lucide-react';

export const ModelsPage: React.FC = () => {
  const [models, setModels] = useState<RegisteredModel[]>([]);
  const [activeModel, setActiveModel] = useState<RegisteredModel | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isTraining, setIsTraining] = useState(false);
  const [selectedClassifier, setSelectedClassifier] = useState('logistic');
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const fetchModelsData = async () => {
    setIsLoading(true);
    setMessage(null);
    try {
      const allModels = await getModels();
      setModels(allModels);
      const active = await getActiveModel();
      setActiveModel(active);
    } catch (err: any) {
      setMessage({ text: 'Failed to fetch model registry. Verify backend service.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModelsData();
  }, []);

  const handleActivateModel = async (modelId: string) => {
    try {
      await activateModel(modelId);
      setMessage({ text: `Model '${modelId}' set as Active production model.`, type: 'success' });
      fetchModelsData();
    } catch (err: any) {
      setMessage({ text: 'Failed to activate model version.', type: 'error' });
    }
  };

  const handleTriggerTrain = async () => {
    setIsTraining(true);
    setMessage(null);
    try {
      const res = await trainModel({ model_type: selectedClassifier });
      setMessage({
        text: `Training Complete! New Model Version ${res.results?.model_id || ''} Registered & Activated.`,
        type: 'success',
      });
      fetchModelsData();
    } catch (err: any) {
      setMessage({ text: 'Model training pipeline execution failed.', type: 'error' });
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-6 h-6 text-amber-500" />
            <h1 className="text-xl font-bold text-slate-100">Model Registry & Version Management</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Track trained SIF Precursor AI models, evaluation metrics (Accuracy, F1), active model status, and Hugging Face adapters.
          </p>
        </div>
        <button
          onClick={fetchModelsData}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Registry</span>
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

      {/* Active Model Spotlight Card */}
      {activeModel && (
        <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-amber-950/30 border border-amber-500/30 p-6 rounded-xl shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 bg-amber-500 text-slate-950 font-black text-[10px] rounded uppercase font-mono tracking-wider">
                  ACTIVE PRODUCTION MODEL
                </span>
                <span className="text-xs font-mono text-amber-400">{activeModel.model_id}</span>
              </div>
              <h2 className="text-lg font-extrabold text-slate-100 mt-2">{activeModel.model_name}</h2>
              <p className="text-xs text-slate-400 mt-1">{activeModel.description}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold rounded-lg flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4" /> INFERENCE READY
              </span>
            </div>
          </div>

          {/* Active Model Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
            <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800 text-center">
              <p className="text-[10px] text-slate-400 uppercase font-mono">Accuracy</p>
              <p className="text-xl font-black text-amber-400 mt-0.5">
                {((activeModel.metrics?.accuracy || 0) * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800 text-center">
              <p className="text-[10px] text-slate-400 uppercase font-mono">Precision</p>
              <p className="text-xl font-black text-blue-400 mt-0.5">
                {((activeModel.metrics?.precision || 0) * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800 text-center">
              <p className="text-[10px] text-slate-400 uppercase font-mono">Recall</p>
              <p className="text-xl font-black text-emerald-400 mt-0.5">
                {((activeModel.metrics?.recall || 0) * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800 text-center">
              <p className="text-[10px] text-slate-400 uppercase font-mono">F1 Score</p>
              <p className="text-xl font-black text-purple-400 mt-0.5">
                {((activeModel.metrics?.f1 || 0) * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Train & Evaluation Trigger Controls */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-500" />
            Trigger Model Retraining & Evaluation Pipeline
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Trains baseline TF-IDF model on prepared safety dataset splits and registers metric versions.
          </p>
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto">
          <select
            value={selectedClassifier}
            onChange={(e) => setSelectedClassifier(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-amber-500"
          >
            <option value="logistic">Logistic Regression (Default)</option>
            <option value="svm">Linear Support Vector Machine (SVM)</option>
          </select>
          <button
            onClick={handleTriggerTrain}
            disabled={isTraining}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold text-xs rounded-lg shadow-md transition-transform active:scale-95 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${isTraining ? 'animate-spin' : ''}`} />
            <span>{isTraining ? 'Training...' : 'Start Training'}</span>
          </button>
        </div>
      </div>

      {/* Registered Models Registry Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Award className="w-4 h-4 text-amber-400" />
            Model Version Registry Comparison
          </h3>
          <span className="text-xs text-slate-400 font-mono">{models.length} Versions Registered</span>
        </div>

        <div className="overflow-x-auto border border-slate-800 rounded-lg">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono text-[10px]">
              <tr>
                <th className="py-3 px-4">Model ID</th>
                <th className="py-3 px-4">Name & Type</th>
                <th className="py-3 px-4">Accuracy</th>
                <th className="py-3 px-4">Recall</th>
                <th className="py-3 px-4">F1 Score</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900/50">
              {models.map((m) => {
                const isActive = m.status === 'ACTIVE';
                return (
                  <tr key={m.model_id} className="hover:bg-slate-800/40">
                    <td className="py-3.5 px-4 font-mono text-amber-400 font-bold">{m.model_id}</td>
                    <td className="py-3.5 px-4 text-slate-200">
                      <div className="font-semibold">{m.model_name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{m.model_type}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-mono">
                      {((m.metrics?.accuracy || 0) * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-mono">
                      {((m.metrics?.recall || 0) * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-mono font-bold text-amber-400">
                      {((m.metrics?.f1 || 0) * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                          isActive
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                            : 'bg-slate-800 text-slate-400 border border-slate-700'
                        }`}
                      >
                        {m.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {!isActive && (
                        <button
                          onClick={() => handleActivateModel(m.model_id)}
                          className="px-3 py-1 bg-slate-800 hover:bg-amber-500 hover:text-slate-950 text-slate-200 text-[11px] font-bold rounded border border-slate-700 transition-colors"
                        >
                          Activate
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ModelsPage;
