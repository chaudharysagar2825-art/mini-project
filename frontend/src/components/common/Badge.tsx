import React from 'react';

interface BadgeProps {
  variant?:
    | 'routine'
    | 'follow_up'
    | 'urgent'
    | 'granted'
    | 'paused'
    | 'withdrawn'
    | 'open'
    | 'acknowledged'
    | 'assigned'
    | 'escalated'
    | 'resolved'
    | 'dismissed'
    | 'created'
    | 'in_progress'
    | 'completed'
    | 'cancelled'
    | 'active'
    | 'inactive'
    | string;
  text?: string;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'routine', text, className = '' }) => {
  const norm = variant.toLowerCase().replace(/[- ]/g, '_');

  let style = 'bg-slate-100 text-slate-700 border-slate-200';
  let label = text || variant;

  switch (norm) {
    case 'routine':
    case 'low':
      style = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      label = text || 'Routine';
      break;
    case 'follow_up':
    case 'moderate':
      style = 'bg-amber-50 text-amber-700 border-amber-200';
      label = text || 'Follow-Up Needed';
      break;
    case 'urgent':
    case 'crisis':
    case 'elevated':
      style = 'bg-rose-50 text-rose-700 border-rose-200';
      label = text || 'Urgent Priority';
      break;

    // Consent
    case 'granted':
      style = 'bg-teal-50 text-teal-700 border-teal-200';
      label = text || 'Consent Active';
      break;
    case 'paused':
      style = 'bg-amber-50 text-amber-700 border-amber-200';
      label = text || 'Consent Paused';
      break;
    case 'withdrawn':
    case 'not_granted':
      style = 'bg-slate-100 text-slate-700 border-slate-300';
      label = text || 'Consent Withdrawn';
      break;

    // Alerts / Tasks
    case 'open':
      style = 'bg-rose-50 text-rose-700 border-rose-200';
      label = text || 'Open';
      break;
    case 'acknowledged':
      style = 'bg-blue-50 text-blue-700 border-blue-200';
      label = text || 'Acknowledged';
      break;
    case 'assigned':
      style = 'bg-purple-50 text-purple-700 border-purple-200';
      label = text || 'Assigned';
      break;
    case 'escalated':
      style = 'bg-red-50 text-red-700 border-red-200 font-semibold';
      label = text || 'Escalated';
      break;
    case 'resolved':
    case 'completed':
      style = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      label = text || (norm === 'resolved' ? 'Resolved' : 'Completed');
      break;
    case 'dismissed':
    case 'cancelled':
      style = 'bg-slate-100 text-slate-600 border-slate-200';
      label = text || (norm === 'dismissed' ? 'Dismissed' : 'Cancelled');
      break;
    case 'in_progress':
      style = 'bg-indigo-50 text-indigo-700 border-indigo-200';
      label = text || 'In Progress';
      break;
    case 'active':
      style = 'bg-emerald-50 text-emerald-700 border-emerald-200';
      label = text || 'Active';
      break;
    case 'inactive':
      style = 'bg-slate-100 text-slate-500 border-slate-200';
      label = text || 'Inactive';
      break;
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style} ${className}`}
    >
      {label}
    </span>
  );
};
