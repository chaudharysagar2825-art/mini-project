import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useCase } from '../../context/CaseContext';
import { authApi } from '../../api/auth';
import { Badge } from '../common/Badge';
import {
  ShieldCheck,
  LogOut,
  FolderLock,
  ChevronDown,
  Menu,
  Activity,
  User as UserIcon,
} from 'lucide-react';

export const Navbar: React.FC<{ onToggleMobileMenu: () => void }> = ({ onToggleMobileMenu }) => {
  const { user, logout } = useAuth();
  const { cases, activeCase, setActiveCase } = useCase();
  const [backendStatus, setBackendStatus] = useState<'checking' | 'healthy' | 'offline'>('checking');

  useEffect(() => {
    let isMounted = true;
    authApi
      .checkHealth()
      .then((res) => {
        if (isMounted) {
          setBackendStatus(res.status === 'healthy' ? 'healthy' : 'offline');
        }
      })
      .catch(() => {
        if (isMounted) setBackendStatus('offline');
      });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-slate-200">
      <div className="px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Mobile hamburger & Logo */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleMobileMenu}
            className="lg:hidden p-2 rounded-lg text-slate-500 hover:bg-slate-100 focus:outline-none"
            aria-label="Toggle navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-teal-800 text-white flex items-center justify-center font-bold shadow-xs">
              <ShieldCheck className="w-5 h-5 text-teal-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-slate-900 tracking-tight text-base sm:text-lg">
                  Manas Setu
                </span>
                <span className="hidden sm:inline-block text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-teal-100 text-teal-800">
                  SIH26094
                </span>
              </div>
              <p className="text-[11px] text-slate-500 -mt-0.5 hidden sm:block font-medium">
                मानस सेतु • Mental Health & Distress Monitoring
              </p>
            </div>
          </div>
        </div>

        {/* Middle: Active Case Selector */}
        <div className="flex items-center gap-2 max-w-xs sm:max-w-md">
          {cases.length > 0 && (
            <div className="relative flex items-center">
              <FolderLock className="w-4 h-4 text-teal-700 absolute left-3 pointer-events-none" />
              <select
                aria-label="Active Support Case"
                value={activeCase?.id || ''}
                onChange={(e) => {
                  const selectedId = Number(e.target.value);
                  const found = cases.find((c) => c.id === selectedId);
                  if (found) setActiveCase(found);
                }}
                className="pl-9 pr-8 py-1.5 bg-slate-50 border border-slate-300 hover:border-slate-400 rounded-lg text-xs font-semibold text-slate-800 focus:ring-2 focus:ring-teal-500 focus:outline-none appearance-none cursor-pointer truncate max-w-[180px] sm:max-w-[240px]"
              >
                {cases.map((c) => (
                  <option key={c.id} value={c.id}>
                    Case #{c.id} ({c.case_code})
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 pointer-events-none" />
            </div>
          )}
        </div>

        {/* Right: Backend status, User Profile, Sign Out */}
        <div className="flex items-center gap-3">
          {/* Health Pill */}
          <div
            className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border"
            style={{
              backgroundColor: backendStatus === 'healthy' ? '#f0fdf4' : '#fef2f2',
              borderColor: backendStatus === 'healthy' ? '#bbf7d0' : '#fecaca',
              color: backendStatus === 'healthy' ? '#166534' : '#991b1b',
            }}
          >
            <Activity className="w-3 h-3 animate-pulse" />
            <span>{backendStatus === 'healthy' ? 'API Online' : 'API Offline'}</span>
          </div>

          {/* User badge */}
          {user && (
            <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
              <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 font-bold text-xs border border-slate-200">
                <UserIcon className="w-4 h-4 text-slate-600" />
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-xs font-bold text-slate-800 leading-tight">
                  {user.username}
                </div>
                <div className="mt-0.5">
                  <Badge variant={user.role} text={user.role.toUpperCase()} />
                </div>
              </div>

              <button
                onClick={logout}
                title="Sign Out"
                className="ml-2 p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
