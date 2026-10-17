import React, { useEffect, useState } from 'react';
import { useCase } from '../context/CaseContext';
import { consentApi } from '../api/consent';
import { Consent, ConsentCreatePayload } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import {
  ShieldCheck,
  Lock,
  PauseCircle,
  PlayCircle,
  XCircle,
  FileText,
  Calendar,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';

export const ConsentPage: React.FC = () => {
  const { activeCase, isLoading: caseLoading } = useCase();
  const [consent, setConsent] = useState<Consent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const fetchConsent = async (caseId: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await consentApi.getConsent(caseId);
      setConsent(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve consent status';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeCase) {
      fetchConsent(activeCase.id);
      setActionSuccess(null);
    }
  }, [activeCase]);

  const handleCreateInitialConsent = async () => {
    if (!activeCase) return;
    setIsUpdating(true);
    setError(null);
    setActionSuccess(null);

    const payload: ConsentCreatePayload = {
      status: 'granted',
      version: 'v1.0',
      scope: 'Continuous psychological distress monitoring and caseworker coordination under DPDP',
      channel: 'web',
    };

    try {
      const res = await consentApi.createConsent(activeCase.id, payload);
      setConsent(res);
      setActionSuccess('Consent granted successfully. Well-being check-ins are now active.');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to grant consent';
      setError(msg);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleUpdateStatus = async (statusValue: 'granted' | 'paused' | 'withdrawn') => {
    if (!activeCase) return;
    setIsUpdating(true);
    setError(null);
    setActionSuccess(null);

    try {
      const res = await consentApi.updateConsentStatus(activeCase.id, statusValue);
      setConsent(res);
      setActionSuccess(
        statusValue === 'granted'
          ? 'Consent resumed. Confidential check-in processing is now active.'
          : statusValue === 'paused'
          ? 'Consent paused. No new check-ins will be scored until resumed.'
          : 'Consent withdrawn. Case monitoring has been deactivated.'
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update consent status';
      setError(msg);
    } finally {
      setIsUpdating(false);
    }
  };

  if (caseLoading) {
    return <LoadingSpinner size="lg" label="Loading case information..." />;
  }

  if (!activeCase) {
    return (
      <EmptyState
        title="No Active Support Case"
        description="Select a case to inspect and manage privacy & DPDP consent records."
      />
    );
  }

  const status = consent?.status.toLowerCase() || 'not_granted';

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-teal-100 text-teal-800">
            Case #{activeCase.id} • {activeCase.case_code}
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Privacy & DPDP Consent Management
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Transparent data protection controls under the Digital Personal Data Protection (DPDP) Act.
        </p>
      </div>

      {actionSuccess && (
        <div className="p-4 rounded-xl bg-teal-50 border border-teal-200 text-teal-800 text-xs flex items-center gap-2.5">
          <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <LoadingSpinner label="Checking DPDP consent records..." />
      ) : !consent ? (
        /* Unconsented State */
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200/80 shadow-xs space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center shrink-0">
              <Lock className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Monitoring Consent Not Yet Registered
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Before submitting emotional check-ins, please grant voluntary consent for distress assessment.
              </p>
            </div>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-700 space-y-2 leading-relaxed">
            <h4 className="font-bold text-slate-900">Our Privacy Principles:</h4>
            <ul className="list-disc pl-5 space-y-1">
              <li>Your check-ins are encrypted and linked only to your anonymized case code.</li>
              <li>Data is processed exclusively for clinical decision support by authorized human caseworkers.</li>
              <li>You may pause or withdraw consent at any time without compromising access to support services.</li>
            </ul>
          </div>

          <button
            onClick={handleCreateInitialConsent}
            disabled={isUpdating}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-teal-800 hover:bg-teal-900 text-white font-bold text-sm shadow-sm transition disabled:opacity-50"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{isUpdating ? 'Registering Consent...' : 'Grant Voluntary Monitoring Consent'}</span>
          </button>
        </div>
      ) : (
        /* Consented State with Controls */
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
          {/* Status Header */}
          <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-50/50">
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
                Current Consent Status
              </span>
              <div className="flex items-center gap-3">
                <Badge variant={status} className="text-sm px-3 py-1 font-bold" />
                <span className="text-xs text-slate-500">Version: <strong>{consent.version}</strong></span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-2">
              {status !== 'granted' && (
                <button
                  onClick={() => handleUpdateStatus('granted')}
                  disabled={isUpdating}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-teal-800 hover:bg-teal-900 text-white text-xs font-bold transition shadow-xs disabled:opacity-50"
                >
                  <PlayCircle className="w-3.5 h-3.5" />
                  <span>Resume Consent</span>
                </button>
              )}

              {status === 'granted' && (
                <button
                  onClick={() => handleUpdateStatus('paused')}
                  disabled={isUpdating}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold transition shadow-xs disabled:opacity-50"
                >
                  <PauseCircle className="w-3.5 h-3.5" />
                  <span>Pause Check-Ins</span>
                </button>
              )}

              {status !== 'withdrawn' && (
                <button
                  onClick={() => handleUpdateStatus('withdrawn')}
                  disabled={isUpdating}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-rose-50 text-slate-700 hover:text-rose-700 border border-slate-300 text-xs font-bold transition disabled:opacity-50"
                >
                  <XCircle className="w-3.5 h-3.5" />
                  <span>Withdraw Consent</span>
                </button>
              )}
            </div>
          </div>

          {/* Details */}
          <div className="p-6 space-y-5 text-xs text-slate-700">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                <span className="font-bold text-slate-500 uppercase tracking-wider block text-[10px] mb-1">
                  Scope of Authorization
                </span>
                <p className="text-slate-800">{consent.scope}</p>
              </div>

              <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                <span className="font-bold text-slate-500 uppercase tracking-wider block text-[10px] mb-1">
                  Intake Channel
                </span>
                <p className="text-slate-800 capitalize">{consent.channel}</p>
              </div>
            </div>

            {/* Timestamps */}
            <div className="pt-2 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-4 text-slate-500">
              <div>
                <span className="block font-bold text-slate-700 mb-0.5">Consented At:</span>
                <span>{consent.consented_at ? new Date(consent.consented_at).toLocaleString() : 'N/A'}</span>
              </div>
              <div>
                <span className="block font-bold text-slate-700 mb-0.5">Paused At:</span>
                <span>{consent.paused_at ? new Date(consent.paused_at).toLocaleString() : 'None'}</span>
              </div>
              <div>
                <span className="block font-bold text-slate-700 mb-0.5">Withdrawn At:</span>
                <span>{consent.withdrawn_at ? new Date(consent.withdrawn_at).toLocaleString() : 'None'}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
