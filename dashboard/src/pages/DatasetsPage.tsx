import React, { useState, useEffect } from 'react';
import { getDatasets, getDatasetDetails, DatasetInfo } from '../api/ml';
import { Database, CheckCircle2, AlertTriangle, FileSpreadsheet, HardDrive, RefreshCw, BarChart2, Search } from 'lucide-react';

export const DatasetsPage: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<DatasetInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string | null>(null);

  const fetchDatasets = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDatasets();
      setDatasets(data);
      if (data.length > 0) {
        const details = await getDatasetDetails(data[0].dataset_id);
        setSelectedDataset(details);
      }
    } catch (err: any) {
      setError('Failed to load dataset metadata. Please check backend connection.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleSelectDataset = async (ds: DatasetInfo) => {
    try {
      const details = await getDatasetDetails(ds.dataset_id);
      setSelectedDataset(details);
    } catch (err) {
      setSelectedDataset(ds);
    }
  };

  const filteredDatasets = datasets.filter((ds) =>
    ds.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ds.dataset_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
        <div>
          <div className="flex items-center gap-2">
            <Database className="w-6 h-6 text-amber-500" />
            <h1 className="text-xl font-bold text-slate-100">Dataset Management & Quality Pipeline</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            OIL HSE Dataset ingestion, validation metrics, split statistics, and raw text preprocessing.
          </p>
        </div>
        <button
          onClick={fetchDatasets}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Datasets</span>
        </button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 rounded-lg text-amber-400">
            <HardDrive className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">Total Registered Datasets</p>
            <p className="text-2xl font-black text-slate-100">{datasets.length}</p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">Total Safety Records</p>
            <p className="text-2xl font-black text-slate-100">
              {datasets.reduce((acc, d) => acc + d.records_count, 0)}
            </p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-red-500/10 rounded-lg text-red-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">Avg SIF Precursor Ratio</p>
            <p className="text-2xl font-black text-amber-400">
              {datasets.length > 0
                ? `${(datasets.reduce((acc, d) => acc + d.sif_ratio, 0) / datasets.length * 100).toFixed(0)}%`
                : '0%'}
            </p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">Pipeline Status</p>
            <p className="text-sm font-bold text-emerald-400 uppercase tracking-wide">Ready for Training</p>
          </div>
        </div>
      </div>

      {/* Main Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Dataset List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-200">Registered Safety Datasets</h2>
            <span className="text-[10px] font-mono bg-slate-800 text-amber-400 px-2 py-0.5 rounded">
              {filteredDatasets.length} Available
            </span>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search datasets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
            />
          </div>

          {isLoading ? (
            <div className="py-12 text-center text-slate-500 text-xs">Loading datasets...</div>
          ) : error ? (
            <div className="p-4 bg-red-950/30 border border-red-800 text-red-300 text-xs rounded-lg">{error}</div>
          ) : (
            <div className="space-y-2">
              {filteredDatasets.map((ds) => {
                const isSelected = selectedDataset?.dataset_id === ds.dataset_id;
                return (
                  <button
                    key={ds.dataset_id}
                    onClick={() => handleSelectDataset(ds)}
                    className={`w-full text-left p-3.5 rounded-lg border transition-all ${
                      isSelected
                        ? 'bg-amber-500/10 border-amber-500/40 text-slate-100 shadow-sm'
                        : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:bg-slate-800/50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-200 truncate">{ds.name}</span>
                      <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">
                        v{ds.version}
                      </span>
                    </div>
                    <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
                      <span>{ds.records_count} Records</span>
                      <span className="text-amber-400 font-mono">{(ds.sif_ratio * 100).toFixed(0)}% SIF</span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column: Dataset Details & Record Inspector */}
        <div className="lg:col-span-2 space-y-6">
          {selectedDataset ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-amber-400 bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded">
                      {selectedDataset.dataset_id}
                    </span>
                    <h2 className="text-base font-bold text-slate-100">{selectedDataset.name}</h2>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">Source: {selectedDataset.source}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-semibold rounded-full flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> VALIDATED
                  </span>
                </div>
              </div>

              {/* Stats Breakdown */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-center">
                  <p className="text-[11px] text-slate-400 uppercase font-mono">Total Records</p>
                  <p className="text-xl font-extrabold text-slate-100 mt-1">{selectedDataset.records_count}</p>
                </div>
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-center">
                  <p className="text-[11px] text-red-400 uppercase font-mono">SIF Precursors</p>
                  <p className="text-xl font-extrabold text-red-400 mt-1">{selectedDataset.sif_precursor_count}</p>
                </div>
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-center">
                  <p className="text-[11px] text-emerald-400 uppercase font-mono">Non-SIF Controls</p>
                  <p className="text-xl font-extrabold text-emerald-400 mt-1">{selectedDataset.non_sif_count}</p>
                </div>
              </div>

              {/* Record Inspector Table */}
              <div>
                <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-amber-400" />
                  Dataset Sample Records Preview
                </h3>
                {selectedDataset.sample_records && selectedDataset.sample_records.length > 0 ? (
                  <div className="overflow-x-auto border border-slate-800 rounded-lg">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-mono text-[10px]">
                        <tr>
                          <th className="py-2.5 px-3">Report ID</th>
                          <th className="py-2.5 px-3">Description</th>
                          <th className="py-2.5 px-3">SIF Label</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 bg-slate-900/50">
                        {selectedDataset.sample_records.map((rec, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/40">
                            <td className="py-2.5 px-3 font-mono text-amber-400">{rec.report_id || `REC-${idx + 1}`}</td>
                            <td className="py-2.5 px-3 text-slate-300 max-w-md truncate">{rec.description}</td>
                            <td className="py-2.5 px-3">
                              <span
                                className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                                  rec.sif_potential === 1 || rec.sif_precursor
                                    ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                                    : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                                }`}
                              >
                                {rec.sif_potential === 1 || rec.sif_precursor ? 'SIF PRECURSOR' : 'NON-SIF'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-6 bg-slate-950 rounded-lg text-center text-xs text-slate-500">
                    Sample preview records validated for training split.
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-500 text-xs">
              Select a dataset from the left panel to inspect quality metrics.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DatasetsPage;
