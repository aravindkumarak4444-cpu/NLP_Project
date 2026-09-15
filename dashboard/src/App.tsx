import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { ReportsList } from './pages/ReportsList';
import { ReportCreate } from './pages/ReportCreate';
import { ReportDetail } from './pages/ReportDetail';
import { AnalysisDetail } from './pages/AnalysisDetail';
import { RulesPage } from './pages/RulesPage';
import { PatternsPage } from './pages/PatternsPage';
import { DatasetsPage } from './pages/DatasetsPage';
import { ModelsPage } from './pages/ModelsPage';
import { ReviewsPage } from './pages/ReviewsPage';
import { ActionsPage } from './pages/ActionsPage';
import { UsersPage } from './pages/UsersPage';
import { ProfilePage } from './pages/ProfilePage';
import { SettingsPage } from './pages/SettingsPage';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-400 font-medium text-xs">Authenticating HSE session...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Portal Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <Layout>
                  <ReportsList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/reports/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <ReportCreate />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/reports/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <ReportDetail />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/analysis/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <AnalysisDetail />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/rules"
            element={
              <ProtectedRoute>
                <Layout>
                  <RulesPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/patterns"
            element={
              <ProtectedRoute>
                <Layout>
                  <PatternsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/datasets"
            element={
              <ProtectedRoute>
                <Layout>
                  <DatasetsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/models"
            element={
              <ProtectedRoute>
                <Layout>
                  <ModelsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/reviews"
            element={
              <ProtectedRoute>
                <Layout>
                  <ReviewsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/actions"
            element={
              <ProtectedRoute>
                <Layout>
                  <ActionsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/users"
            element={
              <ProtectedRoute>
                <Layout>
                  <UsersPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProfilePage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Layout>
                  <SettingsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Catch-all fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
