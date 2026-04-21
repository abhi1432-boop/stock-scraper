import { useState, useEffect, useRef } from 'react'
import { Search, X, Loader2, CornerDownLeft } from 'lucide-react'
import { useDebounce } from '../hooks/useDebounce'

const SUPPORTED = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'AMD', 'MU']
const NAMES = { AAPL: 'Apple', GOOGL: 'Alphabet', MSFT: 'Microsoft', AMZN: 'Amazon', NVDA: 'NVIDIA', AMD: 'AMD', MU: 'Micron' }
const TICKER_RE = /^[A-Z]{1,5}$/

export default function SearchBar({ onTickerSearch, onFreeQuery, isSearching }) {
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)
  const inputRef = useRef(null)
  const debounced = useDebounce(value.trim().toUpperCase(), 300)

  // Auto-trigger stock lookup for pure ticker patterns as user types
  useEffect(() => {
    if (!debounced) {
      onTickerSearch(null)
      return
    }
    if (TICKER_RE.test(debounced) && SUPPORTED.includes(debounced)) {
      onTickerSearch(debounced)
    }
  }, [debounced]) // eslint-disable-line

  const clear = () => {
    setValue('')
    onTickerSearch(null)
    inputRef.current?.focus()
  }

  const submit = () => {
    const raw = value.trim()
    if (!raw) return
    const upper = raw.toUpperCase()
    if (TICKER_RE.test(upper)) {
      // Treat as ticker lookup (even if not in SUPPORTED — backend will handle it)
      onTickerSearch(upper)
    } else {
      // Free-text question → route to chat
      onFreeQuery(raw)
      setValue('')
    }
  }

  const suggestions = value
    ? SUPPORTED.filter(s => s.startsWith(value.trim().toUpperCase()))
    : []

  const isQuery = value.trim().length > 5 && !TICKER_RE.test(value.trim().toUpperCase())

  return (
    <div className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800/80">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="relative">
          <div className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border transition-all ${
            focused
              ? 'border-sky-600 bg-slate-800 shadow-[0_0_0_3px_rgba(2,132,199,0.12)]'
              : 'border-slate-700 bg-slate-800/60'
          }`}>
            {isSearching
              ? <Loader2 size={16} className="text-sky-400 animate-spin flex-shrink-0" />
              : <Search size={16} className="text-slate-500 flex-shrink-0" />
            }
            <input
              ref={inputRef}
              type="text"
              value={value}
              onChange={e => setValue(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setTimeout(() => setFocused(false), 150)}
              onKeyDown={e => e.key === 'Enter' && submit()}
              placeholder="Search ticker or ask anything… (NVDA, 'compare AMD vs MU')"
              className="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 outline-none min-w-0"
            />
            {value && (
              <button onClick={clear} className="text-slate-500 hover:text-slate-300 transition-colors flex-shrink-0">
                <X size={14} />
              </button>
            )}
            {value && (
              <button
                onClick={submit}
                className={`flex items-center gap-1 flex-shrink-0 px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors ${
                  isQuery
                    ? 'bg-amber-600/80 hover:bg-amber-500 text-white'
                    : 'bg-sky-700/80 hover:bg-sky-600 text-white'
                }`}
              >
                <CornerDownLeft size={11} />
                {isQuery ? 'Ask' : 'Look up'}
              </button>
            )}
          </div>

          {/* Hint text */}
          {focused && !value && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-slate-800/95 border border-slate-700 rounded-xl p-3 shadow-2xl">
              <p className="text-xs text-slate-500 mb-2 font-semibold">Quick access</p>
              <div className="flex flex-wrap gap-1.5">
                {SUPPORTED.map(s => (
                  <button
                    key={s}
                    onMouseDown={() => { setValue(s); onTickerSearch(s) }}
                    className="px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded text-xs text-slate-300 hover:text-white transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
              <p className="text-[11px] text-slate-600 mt-2">Or type any question and press Enter to ask the AI agent</p>
            </div>
          )}

          {/* Ticker suggestions dropdown */}
          {focused && value && suggestions.length > 0 && !isQuery && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-2xl">
              {suggestions.map(s => (
                <button
                  key={s}
                  onMouseDown={() => { setValue(s); onTickerSearch(s) }}
                  className="w-full text-left px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors flex items-center gap-2"
                >
                  <span className="font-semibold text-white">{s}</span>
                  <span className="text-slate-500 text-xs">{NAMES[s]}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
