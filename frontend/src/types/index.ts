// Authentication Types
export interface User {
  id: number;
  username: string;
  role: 'victim' | 'admin' | 'caseworker' | 'counsellor' | string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

// Case Management Types
export interface Case {
  id: number;
  case_code: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CaseCreatePayload {
  case_code: string;
}

// Well-Being Check-In Types
export interface CheckInAnswer {
  question_id: string;
  answer: string;
}

export interface CheckInCreatePayload {
  questionnaire_version: string;
  answers: CheckInAnswer[];
  direct_safety_concern?: boolean | null;
  user_skipped_questions?: string[];
  requested_human_contact: boolean;
}

export interface CheckIn {
  id: number;
  case_id: number;
  questionnaire_version: string;
  status: string;
  submitted_at: string;
  risk_level: string | null;
}

// Risk Assessment Types
export interface Assessment {
  id: number;
  checkin_id: number;
  case_id: number;
  risk_level: 'routine' | 'follow_up' | 'urgent' | string;
  risk_category: 'low' | 'moderate' | 'elevated' | 'crisis' | string;
  direction: 'stable' | 'improving' | 'worsening' | 'unknown' | string;
  score: number;
  confidence?: number | null;
  reason: string;
  model_version: string;
  created_at: string;
}

export interface LongitudinalTrendItem {
  checkin_id: number;
  assessment_id: number | null;
  timestamp: string;
  score: number;
  risk_level: string;
  risk_category: string;
  direction: string;
  reason: string;
}

export interface CaseTrendsResponse {
  case_id: number;
  case_code: string;
  total_checkins: number;
  current_risk_level: string;
  current_risk_category: string;
  overall_direction: string;
  average_score: number;
  history: LongitudinalTrendItem[];
}

// Dashboard Types
export interface DashboardSummary {
  total_cases: number;
  open_alerts: number;
  active_referrals: number;
}

// Alert Types
export interface Alert {
  id: number;
  case_id: number;
  alert_type: string;
  risk_level: 'routine' | 'follow_up' | 'urgent' | string;
  status: 'open' | 'acknowledged' | 'assigned' | 'escalated' | 'resolved' | 'dismissed' | string;
  reason: string;
  direction: string;
  confidence?: number | null;
  assigned_to?: number | null;
  action_reason?: string | null;
  created_at: string;
}

export interface AlertActionPayload {
  action: 'acknowledge' | 'assign' | 'escalate' | 'resolve' | 'dismiss';
  reason?: string | null;
  assigned_to?: number | null;
}

// Referral Types
export type ReferralType =
  | 'mental_health'
  | 'welfare'
  | 'protection'
  | 'legal'
  | 'financial'
  | 'rehab';

export type ReferralPriority = 'routine' | 'follow_up' | 'urgent';

export type ReferralStatus =
  | 'created'
  | 'acknowledged'
  | 'in_progress'
  | 'completed'
  | 'cancelled';

export interface Referral {
  id: number;
  case_id: number;
  referral_type: ReferralType | string;
  organization: string;
  reason: string;
  priority: ReferralPriority | string;
  status: ReferralStatus | string;
  created_at: string;
  updated_at: string;
}

export interface ReferralCreatePayload {
  referral_type: string;
  organization: string;
  reason: string;
  priority: string;
}

export interface ReferralStatusUpdatePayload {
  status: ReferralStatus | string;
  notes?: string;
}

// Consent Types
export type ConsentStatus = 'granted' | 'paused' | 'withdrawn';

export interface Consent {
  id: number;
  case_id: number;
  status: ConsentStatus | string;
  version: string;
  scope: string;
  channel: string;
  consented_at?: string | null;
  paused_at?: string | null;
  withdrawn_at?: string | null;
  created_at: string;
}

export interface ConsentCreatePayload {
  status: ConsentStatus;
  version: string;
  scope: string;
  channel: string;
}

// Safe Contact Types
export interface SafeContact {
  id: number;
  case_id: number;
  contact_name: string;
  relationship: string;
  phone: string;
  preferred_language?: string | null;
  preferred_channel: string;
  safe_time?: string | null;
  neutral_notification: boolean;
  fallback_contact?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SafeContactCreatePayload {
  contact_name: string;
  relationship: string;
  phone: string;
  preferred_language?: string | null;
  preferred_channel: string;
  safe_time?: string | null;
  neutral_notification: boolean;
  fallback_contact?: string | null;
}

// Audit Log Types
export interface AuditLog {
  id: number;
  user_id: number | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  details: string | null;
  ip_address: string | null;
  created_at: string;
}

// Multi-Channel Communication Types
export interface CommunicationStatus {
  sms: {
    provider: string;
    is_mock: boolean;
    gateway_configured: boolean;
  };
  voice_ivr: {
    provider: string;
    is_mock: boolean;
    webhook_security: boolean;
  };
  supported_channels: string[];
}

export interface ReminderRequestPayload {
  case_id: number;
  phone_number: string;
}

export interface InboundSMSSimulationPayload {
  sender_phone: string;
  message: string;
}

export interface VoiceAnalysisResult {
  sentiment: string;
  crisis_signals?: {
    signal_count: number;
    matched_signals: string[];
  };
  distress_indicator?: string;
}
