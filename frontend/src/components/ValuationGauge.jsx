import { motion } from 'framer-motion'
import { calcValuationScore, valuationLabel, valuationColor } from '../utils/metrics'

export default function ValuationGauge({ pe, forwardPE }) {
  const score = calcValuationScore(pe, forwardPE)
  const label = valuationLabel(score)
  const labelCls = valuationColor(score)
  const pct = score != null ? score * 100 : null

  return (
    <div className="my-4">
      <div className="flex justify-between items-center text-xs mb-1.5">
        <span className="text-slate-500">Undervalued</span>
        <span className={`font-semibold ${labelCls}`}>{label}</span>
        <span className="text-slate-500">Overvalued</span>
      </div>

      {/* Gradient track */}
      <div className="relative h-2 rounded-full bg-gradient-to-r from-emerald-500 via-amber-400 to-rose-500">
        {pct != null && (
          <motion.div
            className="absolute top-1/2 w-3.5 h-3.5 bg-white rounded-full border-2 border-slate-900 shadow-[0_0_6px_rgba(255,255,255,0.4)]"
            style={{ left: `${pct}%`, y: '-50%', x: '-50%' }}
            initial={{ left: '50%', opacity: 0 }}
            animate={{ left: `${pct}%`, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 80, damping: 18, delay: 0.25 }}
          />
        )}
        {pct == null && (
          <div className="absolute top-1/2 left-1/2 w-3.5 h-3.5 -translate-x-1/2 -translate-y-1/2 bg-slate-600 rounded-full border-2 border-slate-700" />
        )}
      </div>

      <div className="flex justify-between text-xs text-slate-600 mt-1.5">
        <span>P/E: {pe != null ? pe.toFixed(1) : '—'}</span>
        <span>Fwd P/E: {forwardPE != null ? forwardPE.toFixed(1) : '—'}</span>
      </div>
    </div>
  )
}
