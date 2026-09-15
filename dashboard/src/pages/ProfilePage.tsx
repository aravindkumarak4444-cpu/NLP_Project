import React from 'react';
import { useAuth } from '../context/AuthContext';
import { User, ShieldCheck, Mail, Building, Calendar, Key, CheckCircle2 } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="py-20 text-center text-slate-400">
        <p>No user session available. Please log in.</p>
      </div>
    );
  }

  const rolePrivileges: Record<string, string[]> = {
    WORKER: [
      'Submit new Unsafe Act / Unsafe Condition / Near-Miss reports',
      'View personal submitted reports',
      'View Life-Saving Rules directory',
    ],
    SAFETY_OFFICER: [
      'Submit and edit safety reports',
      'Trigger AI/NLP SIF precursor analysis pipeline',
      'Assign and track corrective action items',
      'Update report lifecycle statuses (Review, Action Assigned, Resolved)',
      'Inspect dataset pattern analytics',
    ],
    MANAGER: [
      'Full oversight of site safety reports and SIF precursors',
      'Approve and verify completed corrective actions',
      'Review high-risk department & location trends',
      'Export HSE intelligence analytics',
    ],
    ADMIN: [
      'Full system administrator access',
      'Manage user accounts & permissions',
      'Delete safety reports & override status lifecycles',
      'Configure AI engine model parameters',
    ],
  };

  const privileges = rolePrivileges[user.role] || rolePrivileges['WORKER'];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Profile Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl flex flex-col sm:flex-row items-center sm:items-start gap-6">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center text-slate-950 font-black text-3xl shadow-lg shadow-amber-500/20">
          {user.full_name.charAt(0).toUpperCase()}
        </div>

        <div className="space-y-2 text-center sm:text-left flex-1">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h1 className="text-2xl font-extrabold text-slate-100">{user.full_name}</h1>
              <p className="text-xs text-slate-400 font-mono mt-0.5">User ID: {user.user_id}</p>
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
              <ShieldCheck className="w-4 h-4" />
              <span>{user.role}</span>
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-300 pt-2 border-t border-slate-800">
            <span className="flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5 text-amber-400" />
              <span>{user.email}</span>
            </span>
            <span className="flex items-center gap-1.5">
              <Building className="w-3.5 h-3.5 text-amber-400" />
              <span>{user.department}</span>
            </span>
            <span className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-amber-400" />
              <span>Registered: {new Date(user.created_at).toLocaleDateString()}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Role Privileges Grid */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
          <Key className="w-5 h-5 text-amber-400" />
          <span>Role Authorization Privileges ({user.role})</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {privileges.map((priv, idx) => (
            <div key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <span>{priv}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
