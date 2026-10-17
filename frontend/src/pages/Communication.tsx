import React, { useEffect, useState } from 'react';
import { communicationApi } from '../api/communication';
import { CommunicationStatus } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  Radio,
  Send,
  FlaskConical,
  MessageSquare,
  Sparkles,
  PhoneCall,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
} from 'lucide-react';

export const Communication: React.FC = () => {
  const [status, setStatus] = useState<CommunicationStatus | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(true);

  // Dispatch Reminder Form
  const [remCaseId, setRemCaseId] = useState<number>(1);
  const [remPhone, setRemPhone] = useState('+91 9876543210');
  const [sendingReminder, setSendingReminder] = useState(false);
  const [reminderResult, setReminderResult] = useState<string | null>(null);
  const [reminderError, setReminderError] = useState<string | null>(null);

  // Inbound SMS Simulator Form
  const [simPhone, setSimPhone] = useState('+91 9876543210');
  const [simMessage, setSimMessage] = useState('I feel scared and alone, please help me reach my caseworker');
  const [simulating, setSimulating] = useState(false);
  const [simResult, setSimResult] = useState<any>(null);
  const [simError, setSimError] = useState<string | null>(null);

  // Text / Voice Analyzer Form
  const [analyzeText, setAnalyzeText] = useState('I have not been able to sleep and feel overwhelmed with panic');
  const [analyzing, setAnalyzing] = useState(false);
  const [nlpResult, setNlpResult] = useState<any>(null);
  const [nlpError, setNlpError] = useState<string | null>(null);

  useEffect(() => {
    communicationApi
      .getStatus()
      .then((res) => setStatus(res))
      .catch(() =>
        setStatus({
          sms: { provider: 'MockSMSProvider', is_mock: true, gateway_configured: false },
          voice_ivr: { provider: 'MockIVRProvider', is_mock: true, webhook_security: false },
          supported_channels: ['web', 'sms', 'ivr'],
        })
      )
      .finally(() => setLoadingStatus(false));
  }, []);

  const handleSendReminder = async (e: React.FormEvent) => {
    e.preventDefault();
    setSendingReminder(true);
    setReminderResult(null);
    setReminderError(null);

    try {
      const res = await communicationApi.sendReminder(remCaseId, remPhone.trim());
      setReminderResult(
        `Reminder dispatched successfully! Provider: ${res.provider} (Status: ${res.status}, ID: ${res.message_id})`
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to dispatch reminder';
      setReminderError(msg);
    } finally {
      setSendingReminder(false);
    }
  };

  const handleSimulateInbound = async (e: React.FormEvent) => {
    e.preventDefault();
    setSimulating(true);
    setSimResult(null);
    setSimError(null);

    try {
      const res = await communicationApi.simulateInboundSMS(simPhone.trim(), simMessage.trim());
      setSimResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Simulation failed';
      setSimError(msg);
    } finally {
      setSimulating(false);
    }
  };

  const handleAnalyzeText = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!analyzeText.trim()) return;

    setAnalyzing(true);
    setNlpResult(null);
    setNlpError(null);

    try {
      const res = await communicationApi.analyzeVoiceText(analyzeText.trim());
      setNlpResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Analysis failed';
      setNlpError(msg);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Multi-Channel Communication Hub
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Unified intake and notification status across SMS, Voice/IVR, and Web channels with neutral notification safety.
        </p>
      </div>

      {/* Integration Telemetry Status */}
      {loadingStatus ? (
        <LoadingSpinner label="Checking multi-channel gateway status..." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  SMS Gateway Status
                </span>
                <Radio className="w-4 h-4 text-teal-700" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <Badge
                  variant="routine"
                  text={status?.sms.is_mock ? 'MOCK DEV PROVIDER' : 'PRODUCTION GATEWAY'}
                />
              </div>
              <p className="text-xs text-slate-600">
                Active Provider: <code className="font-mono text-teal-800">{status?.sms.provider}</code>
              </p>
            </div>
            <div className="text-[11px] text-slate-400 pt-3 border-t border-slate-100 mt-4">
              Gateway Configured: {status?.sms.gateway_configured ? 'Yes' : 'Mock Fallback Mode'}
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Voice / IVR Telephony
                </span>
                <PhoneCall className="w-4 h-4 text-purple-700" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <Badge
                  variant="routine"
                  text={status?.voice_ivr.is_mock ? 'MOCK IVR ACTIVE' : 'LIVE TELEPHONY'}
                />
              </div>
              <p className="text-xs text-slate-600">
                Active Provider:{' '}
                <code className="font-mono text-purple-800">{status?.voice_ivr.provider}</code>
              </p>
            </div>
            <div className="text-[11px] text-slate-400 pt-3 border-t border-slate-100 mt-4">
              Webhook Cryptographic Verification:{' '}
              {status?.voice_ivr.webhook_security ? 'Enforced' : 'Dev Bypass'}
            </div>
          </div>
        </div>
      )}

      {/* 2 Interactive Tools: Safe Reminder & Inbound Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Dispatch Safe SMS Reminder */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center gap-2">
            <Send className="w-4 h-4 text-teal-700" />
            <h2 className="text-base font-bold text-slate-800">Dispatch Routine Wellness SMS</h2>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            Dispatches a privacy-preserving check-in reminder SMS to a verified safe contact. Sensitive case terms and mental health labels are strictly omitted.
          </p>

          {reminderResult && (
            <div className="p-3 bg-teal-50 border border-teal-200 text-teal-800 text-xs rounded-xl flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0" />
              <span>{reminderResult}</span>
            </div>
          )}

          {reminderError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{reminderError}</span>
            </div>
          )}

          <form onSubmit={handleSendReminder} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Victim Case ID
              </label>
              <input
                type="number"
                min={1}
                required
                value={remCaseId}
                onChange={(e) => setRemCaseId(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Destination Phone Number
              </label>
              <input
                type="tel"
                required
                placeholder="+91 9876543210"
                value={remPhone}
                onChange={(e) => setRemPhone(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              />
            </div>

            <button
              type="submit"
              disabled={sendingReminder}
              className="w-full py-2.5 px-4 rounded-xl bg-teal-800 hover:bg-teal-900 text-white font-bold text-xs shadow-xs transition disabled:opacity-50"
            >
              {sendingReminder ? 'Dispatching SMS...' : 'Send Neutral Reminder SMS'}
            </button>
          </form>
        </div>

        {/* Interactive Inbound SMS Simulator */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center gap-2">
            <FlaskConical className="w-4 h-4 text-purple-700" />
            <h2 className="text-base font-bold text-slate-800">Inbound SMS Pipeline Simulator</h2>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            Simulate an incoming text message from a beneficiary. Demonstrates automated NLP crisis signal extraction, check-in ingestion, and triage alert creation.
          </p>

          {simResult && (
            <div className="p-3 bg-purple-50 border border-purple-200 text-purple-900 text-xs rounded-xl space-y-1">
              <div className="font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-purple-700" />
                <span>Ingestion Status: {simResult.status}</span>
              </div>
              {simResult.checkin_id && (
                <p>
                  Check-in <strong>#{simResult.checkin_id}</strong> registered for Case{' '}
                  <strong>#{simResult.case_id}</strong>.
                </p>
              )}
              {simResult.message && <p className="italic">{simResult.message}</p>}
            </div>
          )}

          {simError && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{simError}</span>
            </div>
          )}

          <form onSubmit={handleSimulateInbound} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Sender Phone Number
              </label>
              <input
                type="tel"
                required
                value={simPhone}
                onChange={(e) => setSimPhone(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Simulated Incoming Text Message
              </label>
              <textarea
                rows={2}
                required
                value={simMessage}
                onChange={(e) => setSimMessage(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
              />
            </div>

            <button
              type="submit"
              disabled={simulating}
              className="w-full py-2.5 px-4 rounded-xl bg-purple-800 hover:bg-purple-900 text-white font-bold text-xs shadow-xs transition disabled:opacity-50"
            >
              {simulating ? 'Processing Inbound SMS...' : 'Simulate Inbound SMS Intake'}
            </button>
          </form>
        </div>
      </div>

      {/* NLP Text & Voice Sentiment Analyzer */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-teal-700" />
          <h2 className="text-base font-bold text-slate-800">
            Natural Language Sentiment & Crisis Signal Tester
          </h2>
        </div>
        <p className="text-xs text-slate-500">
          Direct testbed for the backend's NLP classifier and distress marker matching pipeline.
        </p>

        {nlpResult && (
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs">
            <div className="font-bold text-slate-800">NLP Analysis Results:</div>
            <pre className="p-3 bg-white rounded-lg border border-slate-200 text-slate-800 font-mono overflow-x-auto text-[11px]">
              {JSON.stringify(nlpResult.result, null, 2)}
            </pre>
          </div>
        )}

        {nlpError && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
            {nlpError}
          </div>
        )}

        <form onSubmit={handleAnalyzeText} className="space-y-4">
          <div>
            <textarea
              rows={2}
              required
              value={analyzeText}
              onChange={(e) => setAnalyzeText(e.target.value)}
              placeholder="Enter sample reflection text to classify..."
              className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={analyzing}
              className="px-5 py-2 rounded-xl bg-teal-800 hover:bg-teal-900 text-white font-bold text-xs shadow-xs transition disabled:opacity-50"
            >
              {analyzing ? 'Analyzing...' : 'Run NLP Classifier'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
