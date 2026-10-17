import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCase } from '../context/CaseContext';
import { checkinsApi } from '../api/checkins';
import { consentApi } from '../api/consent';
import { CheckIn, Consent } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import {
  ClipboardPenLine,
  ShieldAlert,
  AlertCircle,
  CheckCircle2,
  Lock,
  PhoneCall,
  History,
  Sparkles,
} from 'lucide-react';

export const CheckIns: React.FC = () => {
  const { activeCase, isLoading: caseLoading } = useCase();
  const navigate = useNavigate();

  const [consent, setConsent] = useState<Consent | null>(null);
  const [checkingConsent, setCheckingConsent] = useState(true);
  const [history, setHistory] = useState<CheckIn[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Form inputs
  const [sleepQuality, setSleepQuality] = useState('none');
  const [anxietyIntensity, setAnxietyIntensity] = useState('none');
  const [isolationFeeling, setIsolationFeeling] = useState('none');
  const [copingDifficulty, setCopingDifficulty] = useState('none');
  const [freeReflection, setFreeReflection] = useState('');
  const [directSafety, setDirectSafety] = useState(false);
  const [requestContact, setRequestContact] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<CheckIn | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const loadData = async (caseId: number) => {
    setCheckingConsent(true);
    setLoadingHistory(true);
    try {
      const c = await consentApi.getConsent(caseId);
      setConsent(c);
    } catch {
      setConsent(null);
    } finally {
      setCheckingConsent(false);
    }

    try {
      const chks = await checkinsApi.getCaseCheckIns(caseId);
      setHistory(chks);
    } catch {
      setHistory([]);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    if (activeCase) {
      loadData(activeCase.id);
      setSubmitSuccess(null);
      setSubmitError(null);
    }
  }, [activeCase]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeCase) return;

    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(null);

    const answers = [
      { question_id: 'sleep_quality', answer: sleepQuality },
      { question_id: 'anxiety_intensity', answer: anxietyIntensity },
      { question_id: 'isolation_feeling', answer: isolationFeeling },
      { question_id: 'coping_difficulty', answer: copingDifficulty },
    ];

    if (freeReflection.trim()) {
      answers.push({ question_id: 'free_reflection', answer: freeReflection.trim() });
    }

    try {
      const res = await checkinsApi.submitCheckIn(activeCase.id, {
        questionnaire_version: 'v1',
        answers,
        direct_safety_concern: directSafety,
        requested_human_contact: requestContact,
      });

      setSubmitSuccess(res);
      // Reset optional fields
      setFreeReflection('');
      setDirectSafety(false);
      setRequestContact(false);
      // Reload history
      loadData(activeCase.id);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to submit check-in';
      setSubmitError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (caseLoading || checkingConsent) {
    return <LoadingSpinner size="lg" label="Checking active case and consent status..." />;
  }

  if (!activeCase) {
    return (
      <EmptyState
        title="No Active Support Case"
        description="Please select or generate a support case to start confidential check-ins."
        action={{
          label: 'Go to Dashboard',
          onClick: () => navigate('/dashboard'),
        }}
      />
    );
  }

  const hasActiveConsent = consent?.status === 'granted';

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-teal-100 text-teal-800">
            Case #{activeCase.id} • {activeCase.case_code}
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Confidential Well-Being Check-In
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Reflect on your emotional health and daily experiences. Responses are confidential and monitored with human caseworker oversight.
        </p>
      </div>

      {/* Consent Check Warning */}
      {!hasActiveConsent ? (
        <div className="p-6 bg-amber-50 rounded-2xl border border-amber-200 text-amber-900">
          <div className="flex items-start gap-3">
            <Lock className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <h3 className="text-base font-bold text-amber-900">
                Check-Ins Suspended — Active Consent Required
              </h3>
              <p className="text-xs text-amber-800 mt-1 max-w-xl">
                Under the Digital Personal Data Protection (DPDP) Act, your monitoring consent must be{' '}
                <strong>ACTIVE (GRANTED)</strong> before confidential responses can be processed. Current status:{' '}
                <span className="font-bold uppercase">{consent?.status || 'NOT GRANTED'}</span>.
              </p>
              <div className="mt-4">
                <button
                  onClick={() => navigate('/consent')}
                  className="px-4 py-2 bg-amber-700 hover:bg-amber-800 text-white text-xs font-bold rounded-xl transition shadow-xs"
                >
                  Review & Enable Consent
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Check-in Form Card */
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="p-6 border-b border-slate-100 bg-slate-50/50">
            <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
              <ClipboardPenLine className="w-4 h-4 text-teal-700" />
              Day-to-Day Well-Being Indicators
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Select the option that most accurately represents how you have felt over the last 24–48 hours.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-6">
            {submitError && (
              <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2.5">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
                <div>
                  <strong>Submission Error:</strong> {submitError}
                </div>
              </div>
            )}

            {submitSuccess && (
              <div className="p-5 rounded-2xl bg-teal-50 border border-teal-200 text-teal-900 space-y-2">
                <div className="flex items-center gap-2 font-bold text-sm text-teal-800">
                  <CheckCircle2 className="w-5 h-5 text-teal-600" />
                  <span>Check-In Recorded Successfully (Ref #{submitSuccess.id})</span>
                </div>
                <div className="flex items-center gap-3 pt-1">
                  <span className="text-xs text-teal-700">Advisory Distress Indicator:</span>
                  <Badge variant={submitSuccess.risk_level || 'routine'} />
                </div>
                <p className="text-xs text-teal-800/80 leading-relaxed pt-1">
                  {submitSuccess.risk_level === 'urgent'
                    ? 'Elevated distress or a crisis indicator was recorded. A priority alert has been notified to your support caseworker for follow-up.'
                    : submitSuccess.risk_level === 'follow_up'
                    ? 'Mild to moderate distress was identified. Your care team will review this entry.'
                    : 'Your check-in reflects stable well-being indicators. Thank you for completing your routine check-in.'}
                </p>
              </div>
            )}

            {/* Questions Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Question 1: Sleep */}
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  1. Sleep Quality & Restfulness
                </label>
                <select
                  aria-label="Sleep Quality & Restfulness"
                  value={sleepQuality}
                  onChange={(e) => setSleepQuality(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium text-slate-800 focus:bg-white focus:ring-2 focus:ring-teal-600 focus:outline-none"
                >
                  <option value="none">Restful / Normal — No noticeable sleep disturbance</option>
                  <option value="mild">Mild difficulty falling or staying asleep</option>
                  <option value="moderate">Interrupted sleep, night waking, or distressing dreams</option>
                  <option value="severe">Severe insomnia, frequent nightmares, or exhaustion</option>
                </select>
              </div>

              {/* Question 2: Anxiety */}
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  2. Anxiety & Tension Level
                </label>
                <select
                  aria-label="Anxiety & Tension Level"
                  value={anxietyIntensity}
                  onChange={(e) => setAnxietyIntensity(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium text-slate-800 focus:bg-white focus:ring-2 focus:ring-teal-600 focus:outline-none"
                >
                  <option value="none">Calm / Manageable emotional state</option>
                  <option value="mild">Occasional worry, restlessness, or mild tension</option>
                  <option value="moderate">Frequent nervous exhaustion or panicky sensations</option>
                  <option value="severe">Constant overwhelming anxiety or intense dread</option>
                </select>
              </div>

              {/* Question 3: Isolation */}
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  3. Social Support & Safety Network
                </label>
                <select
                  aria-label="Social Support & Safety Network"
                  value={isolationFeeling}
                  onChange={(e) => setIsolationFeeling(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium text-slate-800 focus:bg-white focus:ring-2 focus:ring-teal-600 focus:outline-none"
                >
                  <option value="none">I feel connected and have safe people to turn to</option>
                  <option value="mild">Mild loneliness, but I have access to support</option>
                  <option value="moderate">Frequently feeling isolated or misunderstood</option>
                  <option value="severe">Completely isolated with no trusted support network</option>
                </select>
              </div>

              {/* Question 4: Coping */}
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  4. Daily Routines & Focus
                </label>
                <select
                  aria-label="Daily Routines & Focus"
                  value={copingDifficulty}
                  onChange={(e) => setCopingDifficulty(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium text-slate-800 focus:bg-white focus:ring-2 focus:ring-teal-600 focus:outline-none"
                >
                  <option value="none">Managing well / Feeling in control of tasks</option>
                  <option value="mild">Slightly harder than usual, but keeping up</option>
                  <option value="moderate">Significant difficulty focusing or doing chores</option>
                  <option value="severe">Unable to manage daily tasks or personal self-care</option>
                </select>
              </div>
            </div>

            {/* Optional Free Reflection */}
            <div className="pt-2">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 flex items-center justify-between">
                <span>5. Personal Reflection (Optional)</span>
                <span className="text-[11px] font-normal text-slate-400">NLP distress detection enabled</span>
              </label>
              <textarea
                rows={3}
                value={freeReflection}
                onChange={(e) => setFreeReflection(e.target.value)}
                placeholder="Share any thoughts, feelings, or challenges you encountered today in your own words..."
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-teal-600 focus:outline-none"
              />
            </div>

            {/* Immediate Safety & Human Request Flags */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
                Immediate Safety & Human Assistance
              </span>

              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  id="directSafety"
                  checked={directSafety}
                  onChange={(e) => setDirectSafety(e.target.checked)}
                  className="mt-0.5 rounded text-rose-600 focus:ring-rose-500 w-4 h-4"
                />
                <label htmlFor="directSafety" className="text-xs text-slate-700 font-medium cursor-pointer">
                  <strong className="text-rose-700">Immediate Safety Concern:</strong> I am currently in immediate distress or feeling unsafe.
                </label>
              </div>

              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  id="requestContact"
                  checked={requestContact}
                  onChange={(e) => setRequestContact(e.target.checked)}
                  className="mt-0.5 rounded text-teal-600 focus:ring-teal-500 w-4 h-4"
                />
                <label htmlFor="requestContact" className="text-xs text-slate-700 font-medium cursor-pointer">
                  <strong className="text-teal-800">Caseworker Outreach:</strong> I would like a caseworker or counsellor to contact me directly.
                </label>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex items-center justify-end pt-2">
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-teal-800 hover:bg-teal-900 text-white font-bold text-sm shadow-sm transition disabled:opacity-50"
              >
                {isSubmitting ? 'Recording Check-In Securely...' : 'Submit Confidential Check-In'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Historical Check-Ins List */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-slate-500" />
            <h2 className="text-base font-bold text-slate-800">Check-In History</h2>
          </div>
          <span className="text-xs font-bold text-slate-400">
            {history.length} Record{history.length === 1 ? '' : 's'}
          </span>
        </div>

        {loadingHistory ? (
          <LoadingSpinner label="Loading check-in history..." />
        ) : history.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">
            No check-in history recorded yet for Case #{activeCase.id}.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-bold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Check-In ID</th>
                  <th className="py-3 px-4">Date & Time</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Distress Indicator</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {history.map((chk) => (
                  <tr key={chk.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4 font-mono font-bold text-teal-800">#{chk.id}</td>
                    <td className="py-3 px-4 text-slate-600">
                      {new Date(chk.submitted_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <span className="capitalize">{chk.status}</span>
                    </td>
                    <td className="py-3 px-4">
                      {chk.risk_level ? (
                        <Badge variant={chk.risk_level} />
                      ) : (
                        <span className="text-slate-400 italic">Assessment unavailable</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
