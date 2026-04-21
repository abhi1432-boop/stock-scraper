import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, FlaskConical, Database } from 'lucide-react'
import { generateReasoning } from '../utils/metrics'

export default function ReasoningAccordion({ stock }) {
  const [open, setOpen] = useState(false)
  const reasons = generateReasoning(stock)

  if (!reasons.length) return null

  return (
    <div className="mt-4 border-t border-slate-700/50 pt-3">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center justify-between w-full text-xs text-slate-400 hover:text-slate-200 transition-colors group"
      >
        <span className="flex items-center gap-1.5">
          <FlaskConical size={12} className="text-sky-500" />
          <span className="font-semibold uppercase tracking-wider">Why this valuation?</span>
        </span>
        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown size={14} />
        </motion.div>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <ul className="mt-3 space-y-3">
              {reasons.map((r, i) => (
                <li key={i} className="flex gap-2.5">
                  <span className="mt-0.5 flex-shrink-0 w-4 h-4 rounded-full bg-sky-900/60 border border-sky-700 flex items-center justify-center text-sky-400 text-[10px] font-bold">
                    {i + 1}
                  </span>
                  <div>
                    <p className="text-xs text-slate-300 leading-relaxed">{r.point}</p>
                    <div className="flex items-center gap-1.5 mt-1">
                      <Database size={9} className="text-slate-600" />
                      <span className="text-[10px] text-slate-600">
                        {r.metric} · {r.source}
                      </span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
