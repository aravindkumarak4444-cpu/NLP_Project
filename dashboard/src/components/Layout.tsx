import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { reportsApi } from '../api/reports';
import { AIStatusResponse } from '../types';
import { ModelStatusBadge } from './ModelStatusBadge';
import {
  Flame,
  LayoutDashboard,
  FileText,
  PlusCircle,
  BookOpen,
  PieChart,
  CheckSquare,
  Users,
  User as UserIcon,
  Settings,
  LogOut,
  Menu,
  X,
  Database,
  Cpu,
  UserCheck,
  ShieldCheck,
  ChevronRight,
  Bell,
  Search,
} from 'lucide-react';

interface LayoutProps {
  children?: React.ReactNode;
}

interface NavSection {
  title: string;
  items: {
    to: string;
    label: string;
    icon: React.ElementType;
    badge?: string;
  }[];
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [aiStatus, setAiStatus] = useState<AIStatusResponse | null>(null);

  useEffect(() => {
    reportsApi.getAIStatus().then(setAiStatus).catch(() => {});
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const role = user?.role || 'WORKER';

  const navSections: NavSection[] = [
    {
      title: 'OVERVIEW',
      items: [
        { to: '/dashboard', label: role === 'WORKER' ? 'My Safety Dashboard' : 'Dashboard Overview', icon: LayoutDashboard },
      ],
    },
    {
      title: 'SAFETY INTELLIGENCE',
      items: [
        { to: '/reports', label: role === 'WORKER' ? 'My Submitted Reports' : 'Safety Reports', icon: FileText },
        { to: '/reports/new', label: 'Submit Report', icon: PlusCircle },
        ...(role !== 'WORKER' ? [
          { to: '/rules', label: 'Life-Saving Rules', icon: BookOpen },
          { to: '/patterns', label: 'SIF Incident Patterns', icon: PieChart },
        ] : []),
      ],
    },
    {
      title: 'OPERATIONS',
      items: [
        ...(role !== 'WORKER' ? [
          { to: '/reviews', label: 'Human Review Queue', icon: UserCheck },
        ] : []),
        { to: '/actions', label: role === 'WORKER' ? 'My Assigned Actions' : 'Corrective Actions', icon: CheckSquare },
      ],
    },
    ...(role !== 'WORKER' ? [
      {
        title: 'ADMINISTRATION',
        items: [
          { to: '/datasets', label: 'Datasets & Candidate Feedback', icon: Database },
          { to: '/models', label: 'Model Registry', icon: Cpu },
          { to: '/users', label: 'Personnel Directory', icon: Users },
          { to: '/settings', label: 'System Settings', icon: Settings },
        ],
      },
    ] : [
      {
        title: 'ACCOUNT',
        items: [
          { to: '/profile', label: 'My Profile & Role', icon: UserIcon },
        ],
      },
    ]),
  ];

  // Helper to determine active page label for top header
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'HSE Intelligence Command Center';
    if (path === '/reports') return 'Field Safety Reports Directory';
    if (path === '/reports/new') return 'Submit New Field Observation Report';
    if (path.startsWith('/reports/')) return 'Safety Report Specification';
    if (path.startsWith('/analysis/')) return 'AI/NLP Precursor Diagnostic Analysis';
    if (path === '/rules') return 'OIL Life-Saving Rules Registry';
    if (path === '/patterns') return 'SIF Incident Pattern & Trend Analytics';
    if (path === '/datasets') return 'HSE Safety Datasets & Data Governance';
    if (path === '/models') return 'AI Model Registry & Evaluation Pipeline';
    if (path === '/reviews') return 'Human-in-the-Loop Review Queue';
    if (path === '/actions') return 'Corrective Actions Tracker';
    if (path === '/users') return 'HSE Personnel & Access Control Directory';
    if (path === '/profile') return 'User Profile & Authorization Privileges';
    if (path === '/settings') return 'System Diagnostics & Configurations';
    return 'HSE Safety Intelligence Platform';
  };

  return (
    <div className="min-h-screen bg-[#090D16] text-slate-100 flex font-sans antialiased">
      {/* Desktop Left Sidebar */}
      <aside className="hidden lg:flex flex-col w-64 bg-[#0F172A] border-r border-slate-800/80 fixed inset-y-0 z-30 shadow-2xl">
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
          <Link to="/dashboard" className="flex items-center gap-3 group">
            <div className="p-2.5 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl text-slate-950 shadow-md shadow-amber-500/10 group-hover:scale-105 transition-transform">
              <Flame className="w-5 h-5 font-bold" />
            </div>
            <div>
              <span className="font-extrabold text-slate-100 text-sm tracking-wide block leading-none">
                OIL INDIA LIMITED
              </span>
              <span className="text-[10px] text-amber-500 font-mono tracking-wider font-bold uppercase block mt-1">
                SIF Precursor AI Platform
              </span>
            </div>
          </Link>
        </div>

        {/* Navigation Sections */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {navSections.map((section, idx) => (
            <div key={idx} className="space-y-1">
              <span className="px-3 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500 block mb-1">
                {section.title}
              </span>
              {section.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === '/dashboard'}
                    className={({ isActive }) =>
                      `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold transition-all group ${
                        isActive
                          ? 'bg-amber-500/10 text-amber-400 border-l-2 border-amber-500 font-bold shadow-sm'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                      }`
                    }
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className="w-4 h-4 text-slate-400 group-hover:text-amber-400 transition-colors" />
                      <span>{item.label}</span>
                    </div>
                  </NavLink>
                );
              })}
            </div>
          ))}
        </div>

        {/* Sidebar Footer User Info */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-900/60 flex items-center justify-between">
          <Link to="/profile" className="flex items-center gap-2.5 min-w-0 group">
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 font-bold text-xs flex-shrink-0">
              {user?.full_name ? user.full_name.charAt(0) : 'U'}
            </div>
            <div className="truncate">
              <span className="block text-xs font-bold text-slate-200 truncate group-hover:text-amber-400 transition-colors">
                {user?.full_name || 'HSE User'}
              </span>
              <span className="block text-[10px] text-slate-400 font-mono">
                {user?.role || 'SAFETY_OFFICER'}
              </span>
            </div>
          </Link>

          <button
            onClick={handleLogout}
            className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-950/40 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Layout Area */}
      <div className="flex-1 flex flex-col lg:pl-64 min-w-0">
        {/* Top Header Bar */}
        <header className="bg-[#0F172A] border-b border-slate-800/80 sticky top-0 z-20 shadow-md h-16 flex items-center px-4 sm:px-6 justify-between">
          {/* Mobile Menu Button & Breadcrumb */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-slate-400 hover:text-slate-100 bg-slate-800 rounded-lg border border-slate-700"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

            <div>
              <h1 className="text-sm font-extrabold text-slate-100 flex items-center gap-2">
                <span>{getPageTitle()}</span>
              </h1>
              <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                <span>OIL HSE Portal</span>
                <ChevronRight className="w-3 h-3 text-slate-600" />
                <span className="font-mono text-slate-400">{location.pathname}</span>
              </div>
            </div>
          </div>

          {/* AI Model Status Badge & Quick Controls */}
          <div className="flex items-center gap-3">
            {aiStatus && <ModelStatusBadge mode={aiStatus.mode} loaded={aiStatus.model_loaded} />}

            {user && (
              <div className="hidden sm:flex items-center gap-2 border-l border-slate-800 pl-3">
                <span className="text-[11px] font-mono font-bold px-2 py-0.5 bg-slate-800 border border-slate-700 text-amber-400 rounded">
                  {user.department || 'Operations'}
                </span>
              </div>
            )}
          </div>
        </header>

        {/* Mobile Nav Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-[#0F172A] border-b border-slate-800 px-4 py-4 space-y-4">
            {navSections.map((section, idx) => (
              <div key={idx} className="space-y-1">
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  {section.title}
                </span>
                {section.items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={item.to === '/dashboard'}
                      onClick={() => setMobileMenuOpen(false)}
                      className={({ isActive }) =>
                        `flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                          isActive
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                            : 'text-slate-300 hover:bg-slate-800'
                        }`
                      }
                    >
                      <Icon className="w-4 h-4 text-slate-400" />
                      <span>{item.label}</span>
                    </NavLink>
                  );
                })}
              </div>
            ))}
            <div className="pt-2 border-t border-slate-800 flex justify-between items-center">
              <span className="text-xs text-slate-400">{user?.full_name} ({user?.role})</span>
              <button
                onClick={handleLogout}
                className="px-3 py-1.5 bg-red-950/60 border border-red-800 text-red-300 rounded-lg text-xs font-semibold"
              >
                Logout
              </button>
            </div>
          </div>
        )}

        {/* Page Content Container */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children || <Outlet />}
        </main>

        {/* Footer Bar */}
        <footer className="bg-[#0F172A] border-t border-slate-800/80 py-3.5 px-6 text-center text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Oil India Limited (OIL) • SIF Precursor AI Engine & Safety Portal</span>
          <span className="font-mono text-[11px] text-slate-600">Model Version: MOD-200SAMPLES-1789490114</span>
        </footer>
      </div>
    </div>
  );
};

export default Layout;
