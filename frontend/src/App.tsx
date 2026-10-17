import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { CaseProvider } from './context/CaseContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';

// Pages
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { CheckIns } from './pages/CheckIns';
import { Assessments } from './pages/Assessments';
import { LongitudinalMonitoring } from './pages/LongitudinalMonitoring';
import { Alerts } from './pages/Alerts';
import { Referrals } from './pages/Referrals';
import { ConsentPage } from './pages/Consent';
import { SafeContacts } from './pages/SafeContacts';
import { Cases } from './pages/Cases';
import { Communication } from './pages/Communication';
import { AuditLogs } from './pages/AuditLogs';
import { NotFound } from './pages/NotFound';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CaseProvider>
          <Routes>
            {/* Public route */}
            <Route path="/login" element={<Login />} />

            {/* Protected authenticated routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="checkins" element={<CheckIns />} />
              <Route path="assessments" element={<Assessments />} />
              <Route path="referrals" element={<Referrals />} />
              <Route path="consent" element={<ConsentPage />} />
              <Route path="safe-contacts" element={<SafeContacts />} />
              <Route path="audit" element={<AuditLogs />} />

              {/* Staff / Clinical Triage only routes */}
              <Route
                path="monitoring"
                element={
                  <ProtectedRoute allowedRoles={['admin', 'caseworker', 'counsellor']}>
                    <LongitudinalMonitoring />
                  </ProtectedRoute>
                }
              />
              <Route
                path="alerts"
                element={
                  <ProtectedRoute allowedRoles={['admin', 'caseworker', 'counsellor']}>
                    <Alerts />
                  </ProtectedRoute>
                }
              />
              <Route
                path="cases"
                element={
                  <ProtectedRoute allowedRoles={['admin', 'caseworker', 'counsellor']}>
                    <Cases />
                  </ProtectedRoute>
                }
              />
              <Route
                path="communication"
                element={
                  <ProtectedRoute allowedRoles={['admin', 'caseworker', 'counsellor']}>
                    <Communication />
                  </ProtectedRoute>
                }
              />

              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </CaseProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
