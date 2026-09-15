import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { reportsApi } from '../api/reports';
import { ReportType } from '../types';
import { PlusCircle, ArrowRight, AlertCircle, FileText } from 'lucide-react';

export const ReportCreate: React.FC = () => {
  const [reportType, setReportType] = useState<ReportType>('UNSAFE_ACT');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [department, setDepartment] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (description.trim().length < 10) {
      setError('Description must be at least 10 characters long.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const created = await reportsApi.createReport({
        report_type: reportType,
        description,
        location,
        department,
      });

      // Automatically trigger AI analysis pipeline for the newly created report
      try {
        await reportsApi.analyzeReport(created.report_id);
      } catch (analErr) {
        console.warn('Auto-analysis warning (can be re-run manually):', analErr);
      }

      navigate(`/reports/${created.report_id}`);
    } catch (err: any) {
      console.error('Failed to submit report:', err);
      setError(
        err.response?.data?.error?.message ||
          'Failed to submit report. Please check input parameters.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800">
          <div className="p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-500">
            <PlusCircle className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-100">Submit Field Safety Incident Report</h1>
            <p className="text-xs text-slate-400">
              Log Unsafe Acts, Unsafe Conditions, or Near Misses for automated SIF precursor AI detection.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-3.5 bg-red-950/80 border border-red-800 rounded-xl text-red-300 text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Report Type Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">
              Report Category <span className="text-red-400">*</span>
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'UNSAFE_ACT', label: 'Unsafe Act', desc: 'Unsafe behavior or protocol bypass' },
                { id: 'UNSAFE_CONDITION', label: 'Unsafe Condition', desc: 'Physical workplace/equipment hazard' },
                { id: 'NEAR_MISS', label: 'Near Miss', desc: 'Incident that could have caused injury' },
              ].map((item) => (
                <button
                  type="button"
                  key={item.id}
                  onClick={() => setReportType(item.id as ReportType)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    reportType === item.id
                      ? 'bg-amber-500/10 border-amber-500 text-amber-400 font-bold shadow-md shadow-amber-500/5'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <span className="block text-xs font-bold">{item.label}</span>
                  <span className="block text-[10px] text-slate-500 mt-1">{item.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Location & Department Inputs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Plant / Rig / Location <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                required
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Processing Plant Area A"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Department / Operation <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                required
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="e.g. Maintenance / Drilling"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>
          </div>

          {/* Description Textarea */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Incident Description & Field Observations <span className="text-red-400">*</span>
            </label>
            <textarea
              required
              rows={5}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the unsafe act, condition, or near miss in detail (e.g. Worker was working at height on scaffold structure without fall protection harness)."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 leading-relaxed"
            />
            <span className="text-[10px] text-slate-500 mt-1 block">
              Min 10 characters. Include equipment, activities, and safety control breaches if applicable.
            </span>
          </div>

          {/* Submit Button */}
          <div className="pt-3">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 disabled:opacity-50"
            >
              {loading ? (
                <span>Submitting & Running AI Analysis...</span>
              ) : (
                <>
                  <span>Submit Safety Report & Trigger SIF Precursor AI</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
