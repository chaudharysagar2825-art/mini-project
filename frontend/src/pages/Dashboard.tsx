import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCase } from '../context/CaseContext';
import { dashboardApi } from '../api/dashboard';
import { checkinsApi } from '../api/checkins';
import { consentApi } from '../api/consent';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { HelplineBanner } from '../components/common/HelplineBanner';
import {
  CheckIn,
  Consent,
  DashboardSummary,
} from '../types';
import {
  Activity,
  AlertTriangle,
  HandHeart,
  FolderKanban,
  ClipboardPenLine,
  TrendingUp,
  ShieldCheck,
  ArrowRight,
  Radio,
  FileText,
  PlusCircle,
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { cases, activeCase, createAutoCase, isLoading: casesLoading } = useCase();
  const navigate = useNavigate();

  const isStaff = user && ['admin', 'caseworker', 'counsellor'].includes(user.role.toLowerCase());

  // Staff summary state
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  // Victim state
  const [latestCheckin, setLatestCheckin] = useState<CheckIn | null>(null);
  const [consent, setConsent] = useState<Consent | null>(null);
  const [loadingVictimData, setLoadingVictimData] = useState(false);
  const [generatingCase, setGeneratingCase] = useState(false);

  useEffect(() => {
    if (isStaff) {
      setLoadingSummary(true);
      dashboardApi
        .getDashboardSummary()
        .then((res) => setSummary(res))
        .catch(() => setSummary({ total_cases: 0, open_alerts: 0, active_referrals: 0 }))
        .finally(() => setLoadingSummary(false));
    } else if (activeCase) {
      setLoadingVictimData(true);
      Promise.all([
        checkinsApi.getCaseCheckIns(activeCase.id).catch(() => []),
        consentApi.getConsent(activeCase.id).catch(() => null),
      ])
        .then(([chks, cns]) => {
          if (chks && chks.length > 0) {
            setLatestCheckin(chks[0]);
          } else {
            setLatestCheckin(null);
          }
          setConsent(cns);
        })
        .finally(() => setLoadingVictimData(false));
    }
  }, [isStaff, activeCase]);

  const handleGenerateCase = async () => {
    setGeneratingCase(true);
    try {
      await createAutoCase();
    } catch (err) {
      console.error(err);
    } finally {
      setGeneratingCase(false);
    }
  };

  if (casesLoading) {
    return <LoadingSpinner size="lg" label="Loading dashboard data..." />;
  }

  // ─────────────────────────────────────────────────────────────
  // 1. STAFF PORTAL DASHBOARD
  // ─────────────────────────────────────────────────────────────
  if (isStaff) {
    return (
      <div className="space-y-6">
        {/* Hero Header */}
        <div className="rounded-2xl p-6 sm:p-8 bg-gradient-to-r from-teal-900 via-teal-950 to-slate-900 text-white shadow-sm border border-teal-800/40">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-teal-800 text-teal-200">
                  {user?.role.toUpperCase()} PORTAL
                </span>
                <span className="text-xs text-teal-300">Human-in-the-Loop Clinical Triage</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                Welcome back, {user?.username}
              </h1>
              <p className="mt-1 text-sm text-teal-100/80 max-w-2xl">
                Real-time operational metrics, longitudinal distress monitoring, and coordinated care referrals.
              </p>
            </div>
            <button
              onClick={() => navigate('/alerts')}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-semibold text-sm transition shadow-sm shrink-0"
            >
              <AlertTriangle className="w-4 h-4 text-teal-200" />
              <span>Review Alert Queue</span>
            </button>
          </div>
        </div>

        {/* Real Summary Metrics from API */}
        {loadingSummary ? (
          <LoadingSpinner label="Fetching summary statistics..." />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Active Support Cases
                </p>
                <h3 className="text-3xl font-black text-slate-900 mt-1">
                  {summary?.total_cases ?? 0}
                </h3>
                <p className="text-xs text-slate-400 mt-1">Cases registered under care</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center">
                <FolderKanban className="w-6 h-6" />
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Open Distress Alerts
                </p>
                <h3 className="text-3xl font-black text-rose-600 mt-1">
                  {summary?.open_alerts ?? 0}
                </h3>
                <p className="text-xs text-slate-400 mt-1">Requiring caseworker review</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
                <AlertTriangle className="w-6 h-6" />
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Active Referrals
                </p>
                <h3 className="text-3xl font-black text-slate-900 mt-1">
                  {summary?.active_referrals ?? 0}
                </h3>
                <p className="text-xs text-slate-400 mt-1">Inter-agency assistance</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center">
                <HandHeart className="w-6 h-6" />
              </div>
            </div>
          </div>
        )}

        {/* Operational Quick Nav Cards */}
        <h2 className="text-base font-bold text-slate-900 tracking-tight pt-2">
          Clinical Decision Support Modules
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div
            onClick={() => navigate('/monitoring')}
            className="group bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs hover:border-teal-500 hover:shadow-md transition cursor-pointer flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center mb-4 group-hover:scale-105 transition">
                <Activity className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 group-hover:text-teal-800 transition">
                Longitudinal Monitoring
              </h3>
              <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                Inspect 0-10 distress trajectories, trend lines, and AI decision support factors across cases.
              </p>
            </div>
            <div className="mt-5 flex items-center gap-1.5 text-xs font-bold text-teal-700 group-hover:gap-2.5 transition-all">
              <span>Inspect Trajectories</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>

          <div
            onClick={() => navigate('/alerts')}
            className="group bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs hover:border-teal-500 hover:shadow-md transition cursor-pointer flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center mb-4 group-hover:scale-105 transition">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 group-hover:text-teal-800 transition">
                Alert Triage Queue
              </h3>
              <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                Review deterministic rule evaluations, crisis signals, and record triage decisions.
              </p>
            </div>
            <div className="mt-5 flex items-center gap-1.5 text-xs font-bold text-teal-700 group-hover:gap-2.5 transition-all">
              <span>Manage Alerts</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>

          <div
            onClick={() => navigate('/communication')}
            className="group bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs hover:border-teal-500 hover:shadow-md transition cursor-pointer flex flex-col justify-between"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center mb-4 group-hover:scale-105 transition">
                <Radio className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 group-hover:text-teal-800 transition">
                Multi-Channel Communications
              </h3>
              <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                Inspect SMS and Voice/IVR telemetry, dispatch safe check-in reminders, and test NLP ingestion.
              </p>
            </div>
            <div className="mt-5 flex items-center gap-1.5 text-xs font-bold text-teal-700 group-hover:gap-2.5 transition-all">
              <span>View Telemetry</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────
  // 2. VICTIM PORTAL DASHBOARD
  // ─────────────────────────────────────────────────────────────

  // If no case exists for the victim, prompt case setup
  if (!activeCase && cases.length === 0) {
    return (
      <div className="max-w-2xl mx-auto py-12 text-center">
        <div className="bg-white p-8 sm:p-12 rounded-3xl shadow-sm border border-slate-200">
          <div className="w-16 h-16 rounded-2xl bg-teal-50 text-teal-700 flex items-center justify-center mx-auto mb-5">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">
            Welcome to Your Confidential Support Space
          </h2>
          <p className="text-sm text-slate-600 mb-8 max-w-lg mx-auto">
            To begin private well-being check-ins and access trauma-informed care coordination,
            let's create your anonymized support case.
          </p>

          <button
            onClick={handleGenerateCase}
            disabled={generatingCase}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-teal-800 text-white font-bold text-sm hover:bg-teal-900 shadow-md transition disabled:opacity-50"
          >
            <PlusCircle className="w-4 h-4" />
            <span>{generatingCase ? 'Setting up confidential case...' : 'Generate My Confidential Support Case'}</span>
          </button>
        </div>
      </div>
    );
  }

  const consentStatus = consent?.status || 'not_granted';
  const hasActiveConsent = consentStatus === 'granted';

  return (
    <div className="space-y-6">
      {/* Victim Hero Banner */}
      <div className="rounded-2xl p-6 sm:p-8 bg-gradient-to-r from-teal-900 to-slate-900 text-white shadow-sm border border-teal-800/40">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-teal-800 text-teal-200">
              Confidential Support Space
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight mt-2">
              Welcome back, {user?.username}
            </h1>
            <p className="mt-1 text-sm text-teal-100/80 max-w-xl">
              Your confidential hub for trauma-informed mental health monitoring, care coordination, and recovery support.
            </p>
          </div>

          <button
            onClick={() => navigate('/checkins')}
            disabled={!hasActiveConsent}
            className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition shadow-sm shrink-0 ${
              hasActiveConsent
                ? 'bg-teal-500 hover:bg-teal-400 text-slate-950'
                : 'bg-slate-700 text-slate-300 cursor-not-allowed'
            }`}
          >
            <ClipboardPenLine className="w-4 h-4" />
            <span>{hasActiveConsent ? 'Start Today’s Check-In' : 'Consent Required'}</span>
          </button>
        </div>
      </div>

      {/* 3 Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        {/* Case Info */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Active Support Case
            </span>
            <FolderKanban className="w-4 h-4 text-teal-700" />
          </div>
          <div className="text-lg font-bold text-slate-900">
            Case #{activeCase?.id}
          </div>
          <div className="text-xs font-mono text-slate-500 mt-1">
            Code: {activeCase?.case_code}
          </div>
          <div className="mt-3">
            <Badge variant={activeCase?.status || 'active'} text={activeCase?.status.toUpperCase()} />
          </div>
        </div>

        {/* Consent Status */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Privacy & DPDP Consent
              </span>
              <ShieldCheck className="w-4 h-4 text-teal-700" />
            </div>
            <div>
              <Badge variant={consentStatus} />
            </div>
            <p className="text-xs text-slate-500 mt-2">
              {hasActiveConsent
                ? 'Active monitoring authorized under DPDP guidelines'
                : 'Consent is not active. Check-ins are paused.'}
            </p>
          </div>
          <div className="mt-4">
            <button
              onClick={() => navigate('/consent')}
              className="text-xs font-bold text-teal-700 hover:text-teal-900 transition flex items-center gap-1"
            >
              <span>Manage Consent</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Recent Well-Being Check-in */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Latest Check-In Indicator
              </span>
              <TrendingUp className="w-4 h-4 text-teal-700" />
            </div>
            {loadingVictimData ? (
              <LoadingSpinner size="sm" />
            ) : latestCheckin ? (
              <div>
                <Badge variant={latestCheckin.risk_level || 'routine'} />
                <p className="text-xs text-slate-500 mt-2">
                  Recorded: {new Date(latestCheckin.submitted_at).toLocaleDateString()}
                </p>
              </div>
            ) : (
              <div>
                <span className="text-xs font-medium text-slate-400">No check-ins recorded yet</span>
                <p className="text-xs text-slate-500 mt-1">Ready for your initial well-being check-in</p>
              </div>
            )}
          </div>
          <div className="mt-4">
            <button
              onClick={() => navigate('/assessments')}
              className="text-xs font-bold text-teal-700 hover:text-teal-900 transition flex items-center gap-1"
            >
              <span>View Longitudinal Trends</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Reassuring Crisis and Helpline Banner */}
      <HelplineBanner />

      {/* Advisory Note */}
      <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-600 flex items-start gap-2.5">
        <ShieldCheck className="w-4 h-4 shrink-0 text-teal-800 mt-0.5" />
        <div>
          <strong className="text-slate-800">Responsible AI & Clinical Supervision Notice:</strong>{' '}
          Risk indicators generated by Manas Setu are advisory decision-support signals designed to assist trained caseworkers and mental health professionals. They do not constitute an automated clinical diagnosis.
        </div>
      </div>
    </div>
  );
};
