import React, { useEffect, useState } from 'react';
import { casesApi } from '../api/cases';
import { assessmentsApi } from '../api/assessments';
import { dashboardApi } from '../api/dashboard';
import { Case, Assessment, CaseTrendsResponse } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import {
  Activity,
  TrendingUp,
  FolderKanban,
  ShieldCheck,
  Calendar,
  Search,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export const LongitudinalMonitoring: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loadingCases, setLoadingCases] = useState(true);

  const [trends, setTrends] = useState<CaseTrendsResponse | null>(null);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loadingData, setLoadingData] = useState(false);

  useEffect(() => {
    casesApi
      .listAllCases()
      .then((res) => {
        setCases(res);
        if (res.length > 0) setSelectedCase(res[0]);
      })
      .catch(() => setCases([]))
      .finally(() => setLoadingCases(false));
  }, []);

  useEffect(() => {
    if (selectedCase) {
      setLoadingData(true);
      Promise.all([
        dashboardApi.getCaseTrends(selectedCase.id).catch(() => null),
        assessmentsApi.getCaseAssessments(selectedCase.id).catch(() => []),
      ])
        .then(([trnd, asms]) => {
          setTrends(trnd);
          setAssessments(asms);
        })
        .finally(() => setLoadingData(false));
    }
  }, [selectedCase]);

  if (loadingCases) {
    return <LoadingSpinner size="lg" label="Loading registered cases..." />;
  }

  const filteredCases = cases.filter(
    (c) =>
      c.case_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toString().includes(searchQuery)
  );

  const chartData =
    trends?.history.map((item) => ({
      name: `#${item.checkin_id}`,
      date: new Date(item.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
      score: item.score,
      risk_level: item.risk_level,
    })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Longitudinal Distress Monitoring
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Clinical decision support: Inspect persisted distress scores (0–10 scale), risk categories, and trajectory over time.
        </p>
      </div>

      {/* Case Selector Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <FolderKanban className="w-5 h-5 text-teal-700 shrink-0" />
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Select Case for Clinical Review:
          </span>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="text"
              placeholder="Search case code..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-600"
            />
          </div>

          <select
            aria-label="Select Support Case"
            value={selectedCase?.id || ''}
            onChange={(e) => {
              const found = cases.find((c) => c.id === Number(e.target.value));
              if (found) setSelectedCase(found);
            }}
            className="px-3 py-1.5 bg-teal-50 border border-teal-200 text-teal-900 rounded-lg text-xs font-bold focus:outline-none focus:ring-2 focus:ring-teal-600 cursor-pointer"
          >
            {filteredCases.map((c) => (
              <option key={c.id} value={c.id}>
                Case #{c.id} ({c.case_code})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loadingData ? (
        <LoadingSpinner label={`Loading trajectory for Case #${selectedCase?.id}...`} />
      ) : !selectedCase ? (
        <EmptyState title="No Case Selected" description="Select a case from the list above." />
      ) : (
        <div className="space-y-6">
          {/* Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Check-Ins</span>
              <div className="text-2xl font-black text-slate-900 mt-1">{trends?.total_checkins ?? 0}</div>
              <span className="text-[11px] text-slate-400">Total recorded responses</span>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Average Score</span>
              <div className="text-2xl font-black text-slate-900 mt-1">
                {trends?.average_score?.toFixed(1) ?? '0.0'} <span className="text-xs font-medium text-slate-400">/ 10</span>
              </div>
              <span className="text-[11px] text-slate-400">Mean longitudinal score</span>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Overall Trajectory</span>
              <div className="text-lg font-bold text-slate-900 mt-1 capitalize">{trends?.overall_direction || 'Stable'}</div>
              <span className="text-[11px] text-slate-400">Directional trend</span>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Current Priority</span>
              <div className="mt-2">
                <Badge variant={trends?.current_risk_level || 'routine'} />
              </div>
              <span className="text-[11px] text-slate-400 mt-1 block">Latest recorded risk</span>
            </div>
          </div>

          {/* Chart */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-teal-700" />
                  Longitudinal Trajectory Chart — Case #{selectedCase.id}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Distress score trajectory plotted across sequential check-in submissions.
                </p>
              </div>
            </div>

            {chartData.length < 2 ? (
              <div className="py-12 text-center text-xs text-slate-500 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                {chartData.length === 1
                  ? 'Only 1 check-in recorded for this case. More data needed for trajectory line.'
                  : 'No check-in history found for this case.'}
              </div>
            ) : (
              <div className="h-64 sm:h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 10, right: 20, left: -20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} />
                    <YAxis domain={[0, 10]} stroke="#94a3b8" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#ffffff',
                        borderColor: '#cbd5e1',
                        borderRadius: '0.75rem',
                        fontSize: '12px',
                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                      }}
                      formatter={(val: number) => [`${val} / 10`, 'Distress Score']}
                    />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="#0f766e"
                      strokeWidth={3}
                      dot={{ r: 4, fill: '#0f766e', strokeWidth: 2, stroke: '#fff' }}
                      activeDot={{ r: 6, fill: '#0f4c5c' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Historical Assessments Table with Rationale */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Activity className="w-4 h-4 text-slate-500" />
                Structured Clinical Assessments
              </h3>
              <span className="text-xs text-slate-400 font-bold">{assessments.length} Records</span>
            </div>

            {assessments.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">
                No structured assessments generated for this case yet.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {assessments.map((asm) => (
                  <div key={asm.id} className="p-5 hover:bg-slate-50/60 transition space-y-2">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-3">
                        <span className="font-mono font-bold text-xs text-teal-800">
                          Assessment #{asm.id} (Check-in #{asm.checkin_id})
                        </span>
                        <Badge variant={asm.risk_level} />
                        <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">
                          Category: <strong className="capitalize">{asm.risk_category}</strong>
                        </span>
                      </div>
                      <span className="text-xs text-slate-400 flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5" />
                        {new Date(asm.created_at).toLocaleString()}
                      </span>
                    </div>

                    <div className="flex items-start gap-3 pt-1">
                      <div className="w-14 text-center py-1 rounded-lg bg-slate-100 border border-slate-200 shrink-0">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block">Score</span>
                        <span className="text-lg font-black text-slate-900">{asm.score}</span>
                      </div>
                      <div className="flex-1 text-xs text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-200">
                        <strong className="block text-slate-800 mb-0.5">Clinical Decision Support Rationale:</strong>
                        {asm.reason}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
