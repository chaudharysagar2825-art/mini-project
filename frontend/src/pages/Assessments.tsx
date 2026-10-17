import React, { useEffect, useState } from 'react';
import { useCase } from '../context/CaseContext';
import { assessmentsApi } from '../api/assessments';
import { dashboardApi } from '../api/dashboard';
import { Assessment, CaseTrendsResponse } from '../types';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import {
  TrendingUp,
  Activity,
  ShieldAlert,
  Calendar,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
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

export const Assessments: React.FC = () => {
  const { activeCase, isLoading: caseLoading } = useCase();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [trends, setTrends] = useState<CaseTrendsResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeCase) {
      setLoading(true);
      Promise.all([
        assessmentsApi.getCaseAssessments(activeCase.id).catch(() => []),
        dashboardApi.getCaseTrends(activeCase.id).catch(() => null),
      ])
        .then(([asmList, trnd]) => {
          setAssessments(asmList);
          setTrends(trnd);
        })
        .finally(() => setLoading(false));
    }
  }, [activeCase]);

  if (caseLoading || loading) {
    return <LoadingSpinner size="lg" label="Loading distress trajectories and assessments..." />;
  }

  if (!activeCase) {
    return (
      <EmptyState
        title="No Active Support Case"
        description="Select a case to inspect well-being assessments and longitudinal progress."
      />
    );
  }

  // Format history for Recharts
  const chartData =
    trends?.history.map((item, idx) => ({
      name: `#${item.checkin_id}`,
      date: new Date(item.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
      score: item.score,
      risk_level: item.risk_level,
    })) || [];

  const getDirectionIcon = (direction: string) => {
    switch (direction?.toLowerCase()) {
      case 'improving':
        return <ArrowDownRight className="w-4 h-4 text-emerald-600" />;
      case 'worsening':
        return <ArrowUpRight className="w-4 h-4 text-rose-600" />;
      default:
        return <Minus className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-teal-100 text-teal-800">
            Case #{activeCase.id} • {activeCase.case_code}
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Well-Being & Distress Trajectory
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Longitudinal view of distress score progressions and advisory clinical decision-support indicators.
        </p>
      </div>

      {/* Advisory Warning Alert */}
      <div className="p-4 rounded-xl bg-teal-50 border border-teal-200 text-xs text-teal-900 flex items-start gap-2.5">
        <ShieldAlert className="w-4 h-4 text-teal-700 shrink-0 mt-0.5" />
        <div>
          <strong className="text-teal-800">Clinical Decision Support Notice:</strong> Risk levels and scores displayed here are deterministic and algorithmic monitoring aids designed for human caseworker supervision. They do not constitute a medical diagnosis.
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Total Check-Ins
          </span>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {trends?.total_checkins ?? assessments.length}
          </div>
          <span className="text-[11px] text-slate-500">Evaluated data points</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Average Distress Score
          </span>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {trends?.average_score?.toFixed(1) ?? '0.0'}{' '}
            <span className="text-xs font-medium text-slate-400">/ 10</span>
          </div>
          <span className="text-[11px] text-slate-500">Scale of 0 (Calm) to 10 (Crisis)</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Trajectory Direction
          </span>
          <div className="flex items-center gap-1.5 text-lg font-bold text-slate-800 mt-1 capitalize">
            {getDirectionIcon(trends?.overall_direction || 'stable')}
            <span>{trends?.overall_direction || 'Stable'}</span>
          </div>
          <span className="text-[11px] text-slate-500">Longitudinal movement</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Current Risk Level
          </span>
          <div className="mt-2">
            <Badge variant={trends?.current_risk_level || 'routine'} />
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Latest recorded status</span>
        </div>
      </div>

      {/* Recharts Longitudinal Trajectory */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-teal-700" />
              Distress Score Progression (0–10 Scale)
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Lower scores indicate emotional stability; higher scores trigger caseworker review.
            </p>
          </div>
        </div>

        {chartData.length < 2 ? (
          <div className="py-12 text-center text-xs text-slate-500 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            {chartData.length === 1
              ? 'Only 1 check-in recorded. Additional check-ins will render the longitudinal trajectory.'
              : 'No check-in scores available yet to plot.'}
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

      {/* Structured Assessments List */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-slate-500" />
            <h2 className="text-base font-bold text-slate-800">Historical Assessments</h2>
          </div>
          <span className="text-xs font-bold text-slate-400">
            {assessments.length} Entry{assessments.length === 1 ? '' : 'ies'}
          </span>
        </div>

        {assessments.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">
            No formal assessments generated yet for this case.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {assessments.map((asm) => (
              <div key={asm.id} className="p-5 hover:bg-slate-50/60 transition space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-bold text-xs text-teal-800">
                      Assessment #{asm.id} (Check-In #{asm.checkin_id})
                    </span>
                    <Badge variant={asm.risk_level} />
                    <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">
                      Category: <strong className="capitalize">{asm.risk_category}</strong>
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{new Date(asm.created_at).toLocaleString()}</span>
                  </div>
                </div>

                {/* Score and explanation */}
                <div className="flex items-start gap-4 pt-1">
                  <div className="w-14 shrink-0 text-center py-1 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Score</span>
                    <span className="text-lg font-black text-slate-900">{asm.score}</span>
                  </div>
                  <div className="flex-1 text-xs text-slate-600 bg-slate-50/70 p-3 rounded-xl border border-slate-200/60">
                    <strong className="text-slate-800 block mb-0.5">Clinical Decision Support Rationale:</strong>
                    {asm.reason || 'Routine indicators observed with stable baseline.'}
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1">
                  <span>Engine: {asm.model_version}</span>
                  {asm.confidence !== null && asm.confidence !== undefined && (
                    <span>Confidence: {(asm.confidence * 100).toFixed(0)}%</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
