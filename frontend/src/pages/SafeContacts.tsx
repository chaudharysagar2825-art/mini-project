import React, { useEffect, useState } from 'react';
import { useCase } from '../context/CaseContext';
import { safeContactsApi } from '../api/safeContacts';
import { SafeContact, SafeContactCreatePayload } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Modal } from '../components/common/Modal';
import {
  Users,
  PlusCircle,
  Phone,
  Clock,
  ShieldCheck,
  UserX,
  AlertCircle,
  CheckCircle2,
  Lock,
} from 'lucide-react';

export const SafeContacts: React.FC = () => {
  const { activeCase, isLoading: caseLoading } = useCase();
  const [contacts, setContacts] = useState<SafeContact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Add Contact Modal State
  const [showAddModal, setShowAddModal] = useState(false);
  const [contactName, setContactName] = useState('');
  const [relationship, setRelationship] = useState('');
  const [phone, setPhone] = useState('');
  const [preferredLanguage, setPreferredLanguage] = useState('en');
  const [preferredChannel, setPreferredChannel] = useState('call');
  const [safeTime, setSafeTime] = useState('10:00 - 18:00');
  const [neutralNotification, setNeutralNotification] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  // Deactivate Modal State
  const [deactivatingContact, setDeactivatingContact] = useState<SafeContact | null>(null);
  const [isDeactivating, setIsDeactivating] = useState(false);

  const fetchContacts = async (caseId: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await safeContactsApi.getSafeContacts(caseId);
      setContacts(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load safe contacts';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeCase) {
      fetchContacts(activeCase.id);
    }
  }, [activeCase]);

  const handleAddContact = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeCase) return;

    if (!contactName.trim() || !relationship.trim() || !phone.trim()) {
      setAddError('Please fill in contact name, relationship, and phone number.');
      return;
    }

    setIsSubmitting(true);
    setAddError(null);

    const payload: SafeContactCreatePayload = {
      contact_name: contactName.trim(),
      relationship: relationship.trim(),
      phone: phone.trim(),
      preferred_language: preferredLanguage,
      preferred_channel: preferredChannel,
      safe_time: safeTime.trim() || undefined,
      neutral_notification: neutralNotification,
    };

    try {
      await safeContactsApi.createSafeContact(activeCase.id, payload);
      setShowAddModal(false);
      setContactName('');
      setRelationship('');
      setPhone('');
      await fetchContacts(activeCase.id);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to add safe contact';
      setAddError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfirmDeactivate = async () => {
    if (!activeCase || !deactivatingContact) return;

    setIsDeactivating(true);
    try {
      await safeContactsApi.deactivateSafeContact(activeCase.id, deactivatingContact.id);
      setDeactivatingContact(null);
      await fetchContacts(activeCase.id);
    } catch (err: unknown) {
      console.error(err);
    } finally {
      setIsDeactivating(false);
    }
  };

  if (caseLoading) {
    return <LoadingSpinner size="lg" label="Loading case..." />;
  }

  if (!activeCase) {
    return (
      <EmptyState
        title="No Active Support Case"
        description="Select a case to manage confidential safe contacts."
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
            Confidential Safe Contacts
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Trusted contacts who can be reached discreetly during follow-up or safety outreach.
          </p>
        </div>

        <button
          onClick={() => {
            setShowAddModal(true);
            setAddError(null);
          }}
          className="self-start sm:self-auto inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-800 hover:bg-teal-900 text-white font-bold text-xs shadow-xs transition"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Add Safe Contact</span>
        </button>
      </div>

      {/* Privacy Guarantee Banner */}
      <div className="p-4 rounded-xl bg-teal-50 border border-teal-200 text-xs text-teal-900 flex items-start gap-2.5">
        <ShieldCheck className="w-4 h-4 text-teal-700 shrink-0 mt-0.5" />
        <div>
          <strong className="text-teal-800">Neutral Notification Guarantee:</strong> Communications dispatched to safe contacts never mention sensitive case details, legal charges, or distress assessments. Notifications are framed neutrally (e.g. routine wellness reminder) to protect the victim's safety and privacy.
        </div>
      </div>

      {/* Contacts List */}
      {loading ? (
        <LoadingSpinner label="Loading safe contacts..." />
      ) : contacts.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No Safe Contacts Registered"
          description={`No emergency or trusted support contacts have been designated for Case #${activeCase.id}.`}
          action={{
            label: 'Add First Safe Contact',
            onClick: () => setShowAddModal(true),
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {contacts.map((contact) => (
            <div
              key={contact.id}
              className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 transition space-y-4"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="font-mono text-xs font-bold text-teal-800">
                    Contact #{contact.id}
                  </span>
                  <div className="flex items-center gap-1.5">
                    {contact.neutral_notification && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                        Neutral Alerts
                      </span>
                    )}
                    <Badge variant={contact.is_active ? 'active' : 'inactive'} />
                  </div>
                </div>

                <h3 className="text-base font-bold text-slate-900">{contact.contact_name}</h3>
                <span className="text-xs text-slate-500 font-medium capitalize block mb-3">
                  Relationship: {contact.relationship}
                </span>

                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1.5 text-xs text-slate-700">
                  <div className="flex items-center gap-2">
                    <Phone className="w-3.5 h-3.5 text-slate-400" />
                    <span className="font-mono font-medium">{contact.phone}</span>
                  </div>
                  {contact.safe_time && (
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      <span>Safe Contact Hours: {contact.safe_time}</span>
                    </div>
                  )}
                  <div className="text-[11px] text-slate-400 capitalize">
                    Preferred Channel: <strong>{contact.preferred_channel}</strong> • Language:{' '}
                    <strong>{contact.preferred_language || 'English'}</strong>
                  </div>
                </div>
              </div>

              {contact.is_active && (
                <div className="pt-3 border-t border-slate-100 flex justify-end">
                  <button
                    onClick={() => setDeactivatingContact(contact)}
                    className="text-xs font-bold text-rose-600 hover:text-rose-800 transition flex items-center gap-1"
                  >
                    <UserX className="w-3.5 h-3.5" />
                    <span>Deactivate Contact</span>
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add Safe Contact Modal */}
      {showAddModal && (
        <Modal
          isOpen={showAddModal}
          onClose={() => setShowAddModal(false)}
          title="Add Trusted Safe Contact"
          description="Safe contacts receive neutral wellness notifications without disclosing sensitive case details."
        >
          <form onSubmit={handleAddContact} className="space-y-4">
            {addError && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
                {addError}
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Full Name / Alias
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. S. Sharma"
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Relationship
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Sister, Trusted Friend, Community Elder"
                  value={relationship}
                  onChange={(e) => setRelationship(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Phone Number
                </label>
                <input
                  type="tel"
                  required
                  placeholder="e.g. +91 9876543210"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 font-mono focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Safe Contact Hours
                </label>
                <input
                  type="text"
                  placeholder="e.g. 10:00 - 18:00"
                  value={safeTime}
                  onChange={(e) => setSafeTime(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Preferred Channel
                </label>
                <select
                  aria-label="Preferred Channel"
                  value={preferredChannel}
                  onChange={(e) => setPreferredChannel(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
                >
                  <option value="call">Voice Call</option>
                  <option value="sms">SMS Text</option>
                  <option value="whatsapp">WhatsApp / Messaging</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Language
                </label>
                <select
                  aria-label="Preferred Language"
                  value={preferredLanguage}
                  onChange={(e) => setPreferredLanguage(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
                >
                  <option value="hi">Hindi (हिंदी)</option>
                  <option value="en">English</option>
                  <option value="mr">Marathi (मराठी)</option>
                  <option value="ta">Tamil (தமிழ்)</option>
                  <option value="te">Telugu (తెలుగు)</option>
                </select>
              </div>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center gap-3">
              <input
                type="checkbox"
                id="neutralNotif"
                checked={neutralNotification}
                onChange={(e) => setNeutralNotification(e.target.checked)}
                className="rounded text-teal-600 focus:ring-teal-500 w-4 h-4"
              />
              <label htmlFor="neutralNotif" className="text-xs text-slate-700 font-medium cursor-pointer">
                <strong>Enforce Neutral Notification:</strong> Omit all sensitive case identifiers in dispatched messages.
              </label>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-5 py-2 rounded-xl bg-teal-800 hover:bg-teal-900 text-white text-xs font-bold shadow-xs transition disabled:opacity-50"
              >
                {isSubmitting ? 'Registering...' : 'Save Safe Contact'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Deactivate Confirmation Modal */}
      {deactivatingContact && (
        <Modal
          isOpen={!!deactivatingContact}
          onClose={() => setDeactivatingContact(null)}
          title="Deactivate Safe Contact"
          description={`Are you sure you want to deactivate ${deactivatingContact.contact_name}?`}
        >
          <div className="space-y-4">
            <p className="text-xs text-slate-600 leading-relaxed">
              Deactivating this contact will immediately halt automated wellness notifications and emergency follow-up dispatches to this phone number.
            </p>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setDeactivatingContact(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmDeactivate}
                disabled={isDeactivating}
                className="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-xs transition disabled:opacity-50"
              >
                {isDeactivating ? 'Deactivating...' : 'Confirm Deactivation'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
