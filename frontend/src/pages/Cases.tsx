import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCase } from '../context/CaseContext';
import { useAuth } from '../context/AuthContext';
import { casesApi } from '../api/cases';
import { Case } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Modal } from '../components/common/Modal';
import {
  FolderKanban,
  PlusCircle,
  Search,
  Calendar,
  CheckCircle,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

export const Cases: React.FC = () => {
  const { cases, activeCase, setActiveCase, refreshCases, isLoading } = useCase();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [searchQuery, setSearchQuery] = useState('');
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [customCode, setCustomCode] = useState('');
  const [useAutoCode, setUseAutoCode] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);
    setCreateError(null);

    try {
      let newCase: Case;
      if (useAutoCode) {
        newCase = await casesApi.generateCase();
      } else {
        if (!customCode.trim()) {
          setCreateError('Please specify a case code.');
          setIsCreating(false);
          return;
        }
        newCase = await casesApi.createCase(customCode.trim());
      }

      await refreshCases();
      setActiveCase(newCase);
      setShowGenerateModal(false);
      setCustomCode('');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create case';
      setCreateError(msg);
    } finally {
      setIsCreating(false);
    }
  };

  const filteredCases = cases.filter(
    (c) =>
      c.case_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toString().includes(searchQuery)
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Confidential Support Cases
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Secure, anonymized case records connecting well-being check-ins, risk assessments, and multi-agency care.
          </p>
        </div>

        <button
          onClick={() => {
            setShowGenerateModal(true);
            setCreateError(null);
          }}
          className="self-start sm:self-auto inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-800 hover:bg-teal-900 text-white font-bold text-xs shadow-xs transition"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Support Case</span>
        </button>
      </div>

      {/* Filter / Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
          <input
            type="text"
            placeholder="Search by case ID or code..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
          />
        </div>

        <span className="text-xs font-bold text-slate-400">
          Showing {filteredCases.length} case{filteredCases.length === 1 ? '' : 's'}
        </span>
      </div>

      {/* Cases Grid */}
      {isLoading ? (
        <LoadingSpinner label="Loading support cases..." />
      ) : filteredCases.length === 0 ? (
        <EmptyState
          icon={FolderKanban}
          title="No Cases Found"
          description={
            searchQuery ? 'No cases match your search criteria.' : 'No support cases have been registered yet.'
          }
          action={{
            label: 'Create First Case',
            onClick: () => setShowGenerateModal(true),
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredCases.map((c) => {
            const isActive = activeCase?.id === c.id;

            return (
              <div
                key={c.id}
                className={`bg-white rounded-2xl border p-5 shadow-xs transition flex flex-col justify-between space-y-4 ${
                  isActive
                    ? 'border-teal-600 ring-2 ring-teal-600/10'
                    : 'border-slate-200/80 hover:border-slate-300'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="font-mono text-xs font-bold text-teal-800">
                      Case #{c.id}
                    </span>
                    <Badge variant={c.status} />
                  </div>

                  <h3 className="text-base font-bold text-slate-900 font-mono tracking-wide">
                    {c.case_code}
                  </h3>

                  <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-2">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>Created: {new Date(c.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  {isActive ? (
                    <span className="text-xs font-bold text-teal-800 flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5 text-teal-600" />
                      Active Case
                    </span>
                  ) : (
                    <button
                      onClick={() => setActiveCase(c)}
                      className="text-xs font-bold text-slate-600 hover:text-teal-800 transition"
                    >
                      Set as Active
                    </button>
                  )}

                  <button
                    onClick={() => {
                      setActiveCase(c);
                      navigate('/dashboard');
                    }}
                    className="text-xs font-bold text-teal-700 hover:text-teal-900 transition flex items-center gap-1"
                  >
                    <span>Inspect</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Generate Case Modal */}
      {showGenerateModal && (
        <Modal
          isOpen={showGenerateModal}
          onClose={() => setShowGenerateModal(false)}
          title="Create New Confidential Support Case"
          description="Cases store all check-ins, consent records, and risk assessments under strict access controls."
        >
          <form onSubmit={handleCreateCase} className="space-y-4">
            {createError && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
                {createError}
              </div>
            )}

            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <input
                  type="radio"
                  id="autoCode"
                  name="codeChoice"
                  checked={useAutoCode}
                  onChange={() => setUseAutoCode(true)}
                  className="text-teal-600 focus:ring-teal-500"
                />
                <label htmlFor="autoCode" className="text-xs text-slate-800 font-bold cursor-pointer">
                  Auto-generate anonymized code (e.g. CASE-ABC123)
                </label>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="radio"
                  id="customCode"
                  name="codeChoice"
                  checked={!useAutoCode}
                  onChange={() => setUseAutoCode(false)}
                  className="text-teal-600 focus:ring-teal-500"
                />
                <label htmlFor="customCode" className="text-xs text-slate-800 font-bold cursor-pointer">
                  Specify custom case identifier
                </label>
              </div>
            </div>

            {!useAutoCode && (
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Custom Case Code
                </label>
                <input
                  type="text"
                  placeholder="e.g. CASE-MH-2026-001"
                  value={customCode}
                  onChange={(e) => setCustomCode(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono text-slate-800 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
                />
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowGenerateModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isCreating}
                className="px-5 py-2 rounded-xl bg-teal-800 hover:bg-teal-900 text-white text-xs font-bold shadow-xs transition disabled:opacity-50"
              >
                {isCreating ? 'Generating...' : 'Create Case'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
