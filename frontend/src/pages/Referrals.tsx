import React, { useEffect, useState } from 'react';
import { useCase } from '../context/CaseContext';
import { referralsApi } from '../api/referrals';
import { Referral, ReferralCreatePayload, ReferralStatus } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Modal } from '../components/common/Modal';
import {
  HandHeart,
  PlusCircle,
  Building2,
  Calendar,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';

export const Referrals: React.FC = () => {
  const { activeCase, isLoading: caseLoading } = useCase();
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [refType, setRefType] = useState('mental_health');
  const [organization, setOrganization] = useState('');
  const [reason, setReason] = useState('');
  const [priority, setPriority] = useState('routine');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  // Status Update State
  const [selectedReferral, setSelectedReferral] = useState<Referral | null>(null);
  const [newStatus, setNewStatus] = useState<ReferralStatus>('acknowledged');
  const [statusNotes, setStatusNotes] = useState('');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [statusError, setStatusError] = useState<string | null>(null);

  const fetchReferrals = async (caseId: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await referralsApi.getCaseReferrals(caseId);
      setReferrals(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load referrals';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeCase) {
      fetchReferrals(activeCase.id);
    }
  }, [activeCase]);

  const handleCreateReferral = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeCase) return;

    if (!organization.trim() || !reason.trim()) {
      setCreateError('Please provide both the organization name and reason for referral.');
      return;
    }

    setIsSubmitting(true);
    setCreateError(null);

    const payload: ReferralCreatePayload = {
      referral_type: refType,
      organization: organization.trim(),
      reason: reason.trim(),
      priority,
    };

    try {
      await referralsApi.createReferral(activeCase.id, payload);
      setShowCreateModal(false);
      setOrganization('');
      setReason('');
      await fetchReferrals(activeCase.id);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create referral';
      setCreateError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReferral || !activeCase) return;

    setIsUpdatingStatus(true);
    setStatusError(null);

    try {
      await referralsApi.updateReferralStatus(selectedReferral.id, {
        status: newStatus,
        notes: statusNotes.trim() || undefined,
      });
      setSelectedReferral(null);
      setStatusNotes('');
      await fetchReferrals(activeCase.id);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update referral status';
      setStatusError(msg);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  if (caseLoading) {
    return <LoadingSpinner size="lg" label="Loading case..." />;
  }

  if (!activeCase) {
    return (
      <EmptyState
        title="No Active Support Case"
        description="Select a case to inspect and coordinate support service referrals."
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-teal-100 text-teal-800">
              Case #{activeCase.id} • {activeCase.case_code}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Support & Inter-Agency Referrals
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Coordinate specialized external services including mental healthcare, legal aid, protection, and social welfare.
          </p>
        </div>

        <button
          onClick={() => {
            setShowCreateModal(true);
            setCreateError(null);
          }}
          className="self-start sm:self-auto inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-800 hover:bg-teal-900 text-white font-bold text-xs shadow-xs transition"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Referral Request</span>
        </button>
      </div>

      {/* Referrals List */}
      {loading ? (
        <LoadingSpinner label="Loading case referrals..." />
      ) : referrals.length === 0 ? (
        <EmptyState
          icon={HandHeart}
          title="No Referrals Initiated"
          description={`No external care or legal aid referrals have been registered for Case #${activeCase.id}.`}
          action={{
            label: 'Initiate First Referral',
            onClick: () => setShowCreateModal(true),
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {referrals.map((ref) => {
            const isTerminal = ['completed', 'cancelled'].includes(ref.status.toLowerCase());

            return (
              <div
                key={ref.id}
                className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 transition space-y-4"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="font-mono text-xs font-bold text-teal-800">
                      Referral #{ref.id}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <Badge variant={ref.priority} />
                      <Badge variant={ref.status} />
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-slate-900 font-bold text-sm mb-1">
                    <Building2 className="w-4 h-4 text-teal-700 shrink-0" />
                    <span>{ref.organization}</span>
                  </div>

                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">
                    Type: <span className="text-slate-800">{ref.referral_type.replace('_', ' ')}</span>
                  </div>

                  <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100 leading-relaxed">
                    {ref.reason}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    {new Date(ref.created_at).toLocaleDateString()}
                  </span>

                  {!isTerminal && (
                    <button
                      onClick={() => {
                        setSelectedReferral(ref);
                        setStatusNotes('');
                        setStatusError(null);
                      }}
                      className="text-xs font-bold text-teal-700 hover:text-teal-900 transition flex items-center gap-1"
                    >
                      <span>Update Status</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Referral Modal */}
      {showCreateModal && (
        <Modal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          title={`Initiate Referral for Case #${activeCase.id}`}
          description="Connect the beneficiary with specialized mental health or legal aid partners."
        >
          <form onSubmit={handleCreateReferral} className="space-y-4">
            {createError && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
                {createError}
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Referral Category
              </label>
              <select
                aria-label="Referral Category"
                value={refType}
                onChange={(e) => setRefType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              >
                <option value="mental_health">Mental Health & Clinical Psychiatry</option>
                <option value="welfare">Social Welfare & Shelter</option>
                <option value="protection">Protection & Police Liaison</option>
                <option value="legal">Legal Aid & Court Advocacy</option>
                <option value="financial">Financial Assistance & Compensation</option>
                <option value="rehab">Medical Care & Rehabilitation</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Partner Organization / Agency
              </label>
              <input
                type="text"
                required
                placeholder="e.g. District Mental Health Hospital, Legal Services Authority"
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Priority Tier
              </label>
              <select
                aria-label="Priority Tier"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              >
                <option value="routine">Routine Support</option>
                <option value="follow_up">Priority Follow-Up</option>
                <option value="urgent">Urgent Intervention</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Referral Reason & Clinical Summary
              </label>
              <textarea
                rows={3}
                required
                placeholder="Detail the beneficiary's needs and required coordinated services..."
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-5 py-2 rounded-xl bg-teal-800 hover:bg-teal-900 text-white text-xs font-bold shadow-xs transition disabled:opacity-50"
              >
                {isSubmitting ? 'Creating...' : 'Submit Referral'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Update Referral Status Modal */}
      {selectedReferral && (
        <Modal
          isOpen={!!selectedReferral}
          onClose={() => setSelectedReferral(null)}
          title={`Update Referral #${selectedReferral.id}`}
          description={`Update progress for ${selectedReferral.organization} (${selectedReferral.referral_type}).`}
        >
          <form onSubmit={handleUpdateStatus} className="space-y-4">
            {statusError && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
                {statusError}
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Target Status
              </label>
              <select
                aria-label="Target Referral Status"
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value as ReferralStatus)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              >
                <option value="acknowledged">Acknowledged (Partner received)</option>
                <option value="in_progress">In Progress (Active engagement)</option>
                <option value="completed">Completed (Service rendered)</option>
                <option value="cancelled">Cancelled (Closed without service)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Outcome Notes / Update Description
              </label>
              <textarea
                rows={3}
                placeholder="e.g. Appointment scheduled with psychiatrist; initial session completed..."
                value={statusNotes}
                onChange={(e) => setStatusNotes(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setSelectedReferral(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isUpdatingStatus}
                className="px-5 py-2 rounded-xl bg-teal-800 hover:bg-teal-900 text-white text-xs font-bold shadow-xs transition disabled:opacity-50"
              >
                {isUpdatingStatus ? 'Updating...' : 'Update Status'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
