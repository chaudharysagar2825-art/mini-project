import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useCase } from '../context/CaseContext';
import { alertsApi } from '../api/alerts';
import { Alert, AlertActionPayload } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Modal } from '../components/common/Modal';
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  Calendar,
  Filter,
  UserCheck,
  FileEdit,
  Info,
} from 'lucide-react';

export const Alerts: React.FC = () => {
  const { user } = useAuth();
  const { activeCase } = useCase();
  const isAdmin = user?.role === 'admin';
  const isStaff = user && ['admin', 'caseworker', 'counsellor'].includes(user.role.toLowerCase());

  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');

  // Action Modal State
  const [actionAlert, setActionAlert] = useState<Alert | null>(null);
  const [actionChoice, setActionChoice] = useState<'acknowledge' | 'assign' | 'escalate' | 'resolve' | 'dismiss'>('acknowledge');
  const [actionReason, setActionReason] = useState('');
  const [assigneeId, setAssigneeId] = useState<number>(user?.id || 1);
  const [isSubmittingAction, setIsSubmittingAction] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const fetchAlerts = async () => {
    setLoading(true);
    setError(null);
    try {
      let data: Alert[] = [];
      if (isStaff) {
        data = await alertsApi.getAlertsQueue();
      } else if (activeCase) {
        data = await alertsApi.getCaseAlerts(activeCase.id);
      }
      setAlerts(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load alerts';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [isStaff, activeCase]);

  const handleOpenActionModal = (alertItem: Alert) => {
    setActionAlert(alertItem);
    setActionChoice('acknowledge');
    setActionReason('');
    setAssigneeId(user?.id || 1);
    setActionError(null);
  };

  const handleConfirmAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actionAlert) return;

    setIsSubmittingAction(true);
    setActionError(null);

    const payload: AlertActionPayload = {
      action: actionChoice,
      reason: actionReason.trim() || null,
      assigned_to: actionChoice === 'assign' ? Number(assigneeId) : null,
    };

    try {
      await alertsApi.actionAlert(actionAlert.id, payload);
      setActionAlert(null);
      await fetchAlerts();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Action submission failed';
      setActionError(msg);
    } finally {
      setIsSubmittingAction(false);
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" label="Loading alerts queue..." />;
  }

  // Filter alerts
  const filteredAlerts = alerts.filter((a) => {
    const matchStatus = statusFilter === 'all' || a.status.toLowerCase() === statusFilter.toLowerCase();
    const matchPriority = priorityFilter === 'all' || a.risk_level.toLowerCase() === priorityFilter.toLowerCase();
    return matchStatus && matchPriority;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {isStaff ? 'Distress Alert Triage Queue' : 'Case Alerts & Follow-Ups'}
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            {isStaff
              ? 'Review priority distress signals flagged by deterministic scoring and NLP crisis analysis.'
              : 'Notifications and review status for high-priority well-being indicators.'}
          </p>
        </div>

        <button
          onClick={fetchAlerts}
          className="self-start sm:self-auto px-4 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold rounded-xl transition shadow-xs"
        >
          Refresh Queue
        </button>
      </div>

      {/* Advisory Info Note */}
      <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-600 flex items-start gap-2.5">
        <Info className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-800">Triage Governance:</strong> Alerts require human review and escalation.
          {!isAdmin && isStaff && (
            <span className="text-amber-700 font-medium block mt-0.5">
              ℹ️ Caseworkers and counsellors have queue triage access. Triage state transitions and assignment require administrator authorization.
            </span>
          )}
        </div>
      </div>

      {/* Filters (Staff view) */}
      {isStaff && (
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
            <Filter className="w-3.5 h-3.5" />
            <span>Filter By:</span>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-600 font-medium">Status:</label>
            <select
              aria-label="Filter by Alert Status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-semibold text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
            >
              <option value="all">All Statuses</option>
              <option value="open">Open</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="assigned">Assigned</option>
              <option value="escalated">Escalated</option>
              <option value="resolved">Resolved</option>
              <option value="dismissed">Dismissed</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-600 font-medium">Priority:</label>
            <select
              aria-label="Filter by Alert Priority"
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-semibold text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
            >
              <option value="all">All Priorities</option>
              <option value="urgent">Urgent</option>
              <option value="follow_up">Follow-Up</option>
            </select>
          </div>

          <div className="ml-auto text-xs text-slate-400 font-semibold">
            Showing {filteredAlerts.length} alert{filteredAlerts.length === 1 ? '' : 's'}
          </div>
        </div>
      )}

      {/* Alerts Queue */}
      {filteredAlerts.length === 0 ? (
        <EmptyState
          icon={CheckCircle2}
          title="No Alerts Found"
          description={
            statusFilter !== 'all' || priorityFilter !== 'all'
              ? 'No alerts match the selected filter criteria.'
              : 'The distress alert triage queue is clear. No active alerts requiring review.'
          }
        />
      ) : (
        <div className="space-y-4">
          {filteredAlerts.map((a) => {
            const isTerminal = ['resolved', 'dismissed'].includes(a.status.toLowerCase());

            return (
              <div
                key={a.id}
                className="bg-white rounded-2xl border border-slate-200/80 p-5 sm:p-6 shadow-xs hover:border-slate-300 transition space-y-3"
              >
                {/* Header row */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
                      <AlertTriangle className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-base font-bold text-slate-900">
                          Alert #{a.id} • Case #{a.case_id}
                        </h3>
                        <Badge variant={a.risk_level} />
                        <Badge variant={a.status} />
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-2">
                        <Calendar className="w-3.5 h-3.5" />
                        <span>{new Date(a.created_at).toLocaleString()}</span>
                        <span>• Type: <strong className="text-slate-600 capitalize">{a.alert_type}</strong></span>
                        {a.confidence !== null && a.confidence !== undefined && (
                          <span>• Confidence: {(a.confidence * 100).toFixed(0)}%</span>
                        )}
                      </p>
                    </div>
                  </div>

                  {/* Action button (Admins only for active alerts) */}
                  {isAdmin && !isTerminal && (
                    <button
                      onClick={() => handleOpenActionModal(a)}
                      className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-teal-800 hover:bg-teal-900 text-white text-xs font-bold transition shadow-xs self-start sm:self-auto"
                    >
                      <FileEdit className="w-3.5 h-3.5" />
                      <span>Take Triage Action</span>
                    </button>
                  )}
                </div>

                {/* Decision Rationale */}
                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs text-slate-700">
                  <strong className="block text-slate-900 mb-0.5">Clinical Decision Support Rationale:</strong>
                  {a.reason || 'Elevated distress threshold reached.'}
                </div>

                {/* Assignee & Action notes */}
                <div className="flex flex-wrap items-center justify-between text-xs text-slate-500 pt-1 border-t border-slate-100">
                  <div className="flex items-center gap-2">
                    <UserCheck className="w-3.5 h-3.5 text-slate-400" />
                    <span>
                      Assigned To:{' '}
                      <strong className="text-slate-700">
                        {a.assigned_to ? `Staff User #${a.assigned_to}` : 'Unassigned'}
                      </strong>
                    </span>
                  </div>

                  {a.action_reason && (
                    <span className="italic text-slate-500">
                      Note: "{a.action_reason}"
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Admin Action Modal */}
      {actionAlert && (
        <Modal
          isOpen={!!actionAlert}
          onClose={() => setActionAlert(null)}
          title={`Triage Action — Alert #${actionAlert.id}`}
          description={`Update status, assign caseworker, or resolve alert for Case #${actionAlert.case_id}.`}
        >
          <form onSubmit={handleConfirmAction} className="space-y-4">
            {actionError && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
                {actionError}
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Select Triage Action
              </label>
              <select
                aria-label="Triage Action Option"
                value={actionChoice}
                onChange={(e) => setActionChoice(e.target.value as any)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              >
                <option value="acknowledge">Acknowledge Alert</option>
                <option value="assign">Assign to Caseworker</option>
                <option value="escalate">Escalate Priority</option>
                <option value="resolve">Resolve Alert (Issue Addressed)</option>
                <option value="dismiss">Dismiss Alert (False Positive / Inactive)</option>
              </select>
            </div>

            {actionChoice === 'assign' && (
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Assign to Staff User ID
                </label>
                <input
                  type="number"
                  min={1}
                  required
                  value={assigneeId}
                  onChange={(e) => setAssigneeId(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Action Rationale / Clinical Justification
              </label>
              <textarea
                rows={3}
                value={actionReason}
                onChange={(e) => setActionReason(e.target.value)}
                placeholder="e.g. Outreach completed via telephone; victim linked to local counseling centre..."
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setActionAlert(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmittingAction}
                className="px-5 py-2 rounded-xl bg-teal-800 hover:bg-teal-900 text-white text-xs font-bold shadow-xs transition disabled:opacity-50"
              >
                {isSubmittingAction ? 'Updating...' : 'Confirm Action'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
