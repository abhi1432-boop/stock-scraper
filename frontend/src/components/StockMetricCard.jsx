import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Shield, Minus } from 'lucide-react'
import ValuationGauge from './ValuationGauge'
import ReasoningAccordion from './ReasoningAccordion'
import { calcRiskScore, riskLabel, riskColor, fmtLarge, fmtNum, fmtPct, fmtPctRaw } from '../utils/metrics'

function ReturnPill({ label, value }) {
  if (value == null) return (
    <div className="text-center">
      <div className="text-[10px] text-slate-600 uppercase tracking-wider mb-0.5">{label}</div>
      <div className="text-xs font-medium text-slate-600">—</div>
    </div>
  )
  const pos = value >= 0
  return (
    <div className="text-center">
      <div className="text-[10px] text-slate-600 uppercase tracking-wider mb-0.5">{label}</div>
      <div className={`text-xs font-semibold ${pos ? 'text-emerald-400' : 'text-rose-400'}`}>
        {pos ? '+' : ''}{value.toFixed(1)}%
      </div>
    </div>
  )
}

function MetricItem({ label, value }) {
  return (
    <div className="text-center">
      <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">{label}</div>
      <div className="text-xs font-medium text-slate-300">{value}</div>
    </div>
  )
}

export default function StockMetricCard({ stock, summary, highlight }) {
  if (!stock) return null

  const {
    symbol, name, price, change, change_percent,
    pe_ttm, forward_pe, eps_ttm, market_cap, beta,
    gross_margin, net_margin, debt_to_equity, free_cash_flow,
    return_5d, return_1m, return_3m, return_ytd, return_1y, return_5y,
  } = stock

  const positive = (change ?? 0) >= 0
  const riskScore = calcRiskScore(beta, debt_to_equity)
  const riskLbl = riskLabel(riskScore)
  const riskCls = riskColor(riskScore)

  return (
    <motion.div
      layout
      className={`relative bg-slate-800/60 border rounded-2xl p-5 transition-colors ${
        highlight
          ? 'border-sky-600/60 shadow-[0_0_24px_rgba(14,165,233,0.15)]'
          : positive
          ? 'border-emerald-800/40 hover:border-emerald-700/60'
          : 'border-rose-900/40 hover:border-rose-800/60'
      }`}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-1">
        <div>
          <div className="text-lg font-bold text-white">{symbol}</div>
          <div className="text-xs text-slate-500 mt-0.5 max-w-[160px] truncate">{name}</div>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold text-white">
            {price != null ? `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'}
          </div>
          <div className={`flex items-center justify-end gap-1 text-sm font-semibold mt-0.5 ${positive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {positive ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
            {change != null ? `${positive ? '+' : ''}${change.toFixed(2)}` : '—'}
            <span className="text-xs font-normal opacity-80">
              ({change_percent != null ? `${positive ? '+' : ''}${change_percent.toFixed(2)}%` : '—'})
            </span>
          </div>
        </div>
      </div>

      {/* Risk Badge */}
      <div className="flex justify-end mb-1">
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-[10px] font-semibold ${riskCls}`}>
          <Shield size={9} />
          Risk: {riskScore ?? '—'}/100 · {riskLbl}
        </span>
      </div>

      {/* Valuation Gauge */}
      <ValuationGauge pe={pe_ttm} forwardPE={forward_pe} />

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-3 gap-3 py-3 border-t border-slate-700/40">
        <MetricItem label="Mkt Cap" value={fmtLarge(market_cap)} />
        <MetricItem label="P/E" value={fmtNum(pe_ttm)} />
        <MetricItem label="EPS" value={eps_ttm != null ? `$${eps_ttm.toFixed(2)}` : '—'} />
        <MetricItem label="Fwd P/E" value={fmtNum(forward_pe)} />
        <MetricItem label="Gross Margin" value={fmtPctRaw(gross_margin)} />
        <MetricItem label="Net Margin" value={fmtPctRaw(net_margin)} />
        <MetricItem label="Free CF" value={fmtLarge(free_cash_flow)} />
        <MetricItem label="Debt/Eq" value={fmtNum(debt_to_equity)} />
        <MetricItem label="Beta" value={fmtNum(beta)} />
      </div>

      {/* Returns */}
      <div className="grid grid-cols-6 gap-1.5 pt-3 border-t border-slate-700/40">
        <ReturnPill label="5D" value={return_5d} />
        <ReturnPill label="1M" value={return_1m} />
        <ReturnPill label="3M" value={return_3m} />
        <ReturnPill label="YTD" value={return_ytd} />
        <ReturnPill label="1Y" value={return_1y} />
        <ReturnPill label="5Y" value={return_5y} />
      </div>

      {/* AI summary for searched stocks */}
      {summary && (
        <div className="mt-4 pt-3 border-t border-sky-800/40">
          <p className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold mb-1.5">AI Valuation Summary</p>
          <p className="text-xs text-slate-300 leading-relaxed line-clamp-4">{summary}</p>
        </div>
      )}

      {/* Reasoning Accordion */}
      <ReasoningAccordion stock={stock} />
    </motion.div>
  )
}
