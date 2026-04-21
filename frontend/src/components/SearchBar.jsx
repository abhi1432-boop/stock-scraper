import { useState, useEffect, useRef } from 'react'
import { Search, X, Loader2 } from 'lucide-react'
import { useDebounce } from '../hooks/useDebounce'

const SUPPORTED = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'AMD', 'MU']
const TICKER_RE = /^[A-Z]{1,5}$/

export default function SearchBar({ onSearch, isSearching }) {
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)
  const debounced = useDebounce(value.toUpperCase().trim(), 300)
  const inputRef = useRef(null)

  useEffect(() => {
    if (!debounced) {
      onSearch(null)
      return
    }
    if (TICKER_RE.test(debounced)) {
      onSearch(debounced)
    }
  }, [debounced]) // eslint-disable-line

  const clear = () => {
    setValue('')
    onSearch(null)
    inputRef.current?.focus()
  }

  const suggestions = value
    ? SUPPORTED.filter(s => s.startsWith(value.toUpperCase()))
    : []

  return (
    <div className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800/80">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="relative">
          <div className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border transition-all ${
            focused ? 'border-sky-600 bg-slate-800 shadow-[0_0_0_3px_rgba(2,132,199,0.15)]' : 'border-slate-700 bg-slate-800/60'
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
              placeholder="Search ticker… (AAPL, NVDA, MSFT)"
              maxLength={8}
              className="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 outline-none"
            />
            {value && (
              <button onClick={clear} className="text-slate-500 hover:text-slate-300 transition-colors">
                <X size={14} />
              </button>
            )}
          </div>

          {/* Suggestions dropdown */}
          {focused && suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-2xl">
              {suggestions.map(s => (
                <button
                  key={s}
                  onMouseDown={() => { setValue(s); onSearch(s) }}
                  className="w-full text-left px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors flex items-center gap-2"
                >
                  <span className="font-semibold text-white">{s}</span>
                  <span className="text-slate-500 text-xs">{
                    { AAPL:'Apple', GOOGL:'Alphabet', MSFT:'Microsoft', AMZN:'Amazon', NVDA:'NVIDIA', AMD:'AMD', MU:'Micron' }[s]
                  }</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
