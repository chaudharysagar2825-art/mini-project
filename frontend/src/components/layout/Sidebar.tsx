import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  ClipboardPenLine,
  TrendingUp,
  HandHeart,
  ShieldCheck,
  Users,
  AlertTriangle,
  FolderKanban,
  Radio,
  FileText,
  Activity,
  HeartPulse,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const role = user?.role.toLowerCase() || 'victim';
  const isStaff = ['admin', 'caseworker', 'counsellor'].includes(role);

  const victimLinks = [
    { to: '/dashboard', label: 'Overview', icon: LayoutDashboard },
    { to: '/checkins', label: 'Well-being Check-In', icon: ClipboardPenLine },
    { to: '/assessments', label: 'My Assessments & Trends', icon: TrendingUp },
    { to: '/referrals', label: 'Support & Referrals', icon: HandHeart },
    { to: '/consent', label: 'Consent & Privacy', icon: ShieldCheck },
    { to: '/safe-contacts', label: 'Safe Contacts', icon: Users },
  ];

  const staffLinks = [
    { to: '/dashboard', label: 'Triage Overview', icon: LayoutDashboard },
    { to: '/monitoring', label: 'Longitudinal Monitoring', icon: Activity },
    { to: '/alerts', label: 'Distress Alert Queue', icon: AlertTriangle },
    { to: '/referrals', label: 'Case Referrals', icon: HandHeart },
    { to: '/cases', label: 'Support Cases', icon: FolderKanban },
    { to: '/communication', label: 'Multi-Channel Comms', icon: Radio },
    { to: '/audit', label: 'Audit & Compliance', icon: FileText },
  ];

  const links = isStaff ? staffLinks : victimLinks;

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-slate-200 transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:h-[calc(100vh-4rem)] flex flex-col justify-between ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-4 space-y-6 overflow-y-auto">
          {/* Section title */}
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-3 mb-2">
              {isStaff ? 'Clinical Triage' : 'Victim Support Portal'}
            </div>

            <nav className="space-y-1">
              {links.map((link) => {
                const Icon = link.icon;
                return (
                  <NavLink
                    key={link.to}
                    to={link.to}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition ${
                        isActive
                          ? 'bg-teal-50 text-teal-800 shadow-xs border border-teal-200/60 font-bold'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0 text-teal-700" />
                    <span className="truncate">{link.label}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Bottom Helpline Box */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50">
          <div className="rounded-xl p-3 bg-teal-900 text-teal-100 text-xs shadow-xs">
            <div className="flex items-center gap-1.5 font-bold text-white mb-1">
              <HeartPulse className="w-3.5 h-3.5 text-teal-300" />
              <span>Confidential Helplines</span>
            </div>
            <p className="text-[11px] text-teal-200/90 leading-tight">
              Tele-MANAS: <strong className="text-white">14416</strong>
              <br />
              Emergency: <strong className="text-white">112</strong>
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};
