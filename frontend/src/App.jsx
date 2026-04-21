import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { TrendingUp, AlertCircle } from 'lucide-react'
import SearchBar from './components/SearchBar'
import StockMetricCard from './components/StockMetricCard'
import SkeletonCard from './components/SkeletonCard'
import ChatInterface from './components/ChatInterface'

async function fetchAllStocks() {
  try {
    const res = await fetch('/api/stocks')
    if (res.ok) return res.json()
  } catch { /* fall through */ }
  try {
    const res = await fetch('/stock-data.json')
    if (res.ok) return res.json()
  } catch { /* fall through */ }
  return null
}

export default function App() {
  const [stocks, setStocks] = useState({})
  const [loadingStocks, setLoadingStocks] = useState(true)
  const [apiError, setApiError] = useState(false)

  // Search state: null | { isLoading, ticker, stock?, summary? }
  const [searchState, setSearchState] = useState(null)
  const [isSearching, setIsSearching] = useState(false)

  useEffect(() => {
    fetchAllStocks().then(data => {
      if (data) {
        setStocks(data)
      } else {
        setApiError(true)
      }
      setLoadingStocks(false)
    })
  }, [])

  const handleSearch = async (ticker) => {
    if (!ticker) {
      setSearchState(null)
      return
    }
    setIsSearching(true)
    setSearchState({ isLoading: true, ticker })

    try {
      const [stockRes, chatRes] = await Promise.all([
        fetch(`/api/stocks/${ticker}`),
        fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: `In 2 sentences, is ${ticker} currently fairly priced, cheap, or expensive based on its valuation metrics?`,
            tickers: [ticker],
          }),
        }),
      ])

      const stock = stockRes.ok ? await stockRes.json() : null
      const chat = chatRes.ok ? await chatRes.json() : null

      setSearchState({
        isLoading: false,
        ticker,
        stock,
        summary: chat?.answer ?? null,
      })
    } catch {
      setSearchState({ isLoading: false, ticker, stock: null, summary: null })
    } finally {
      setIsSearching(false)
    }
  }

  const symbols = Object.keys(stocks)

  return (
    <div className="min-h-screen bg-slate-900">
      <SearchBar onSearch={handleSearch} isSearching={isSearching} />

      <main className="max-w-6xl mx-auto px-4 py-8 pt-6">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center gap-3 mb-1.5">
            <TrendingUp className="text-emerald-500" size={26} />
            <h1 className="text-2xl font-bold text-white tracking-tight">Stock Tracker</h1>
          </div>
          <p className="text-sm text-slate-500 ml-[38px]">
            AI-powered financial analysis &middot; Live market data via Yahoo Finance
          </p>
        </header>

        {/* Searched stock injection — slides in above the grid */}
        <AnimatePresence mode="wait">
          {searchState && (
            <motion.section
              key="search-section"
              initial={{ opacity: 0, y: -16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16, scale: 0.98 }}
              transition={{ type: 'spring', stiffness: 200, damping: 26 }}
              className="mb-8"
            >
              <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-3">
                Search Result — {searchState.ticker}
              </p>
              <AnimatePresence mode="wait">
                {searchState.isLoading ? (
                  <motion.div key="skel" exit={{ opacity: 0 }}>
                    <SkeletonCard />
                  </motion.div>
                ) : searchState.stock ? (
                  <motion.div key="card" initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ type: 'spring', stiffness: 180, damping: 20 }}>
                    <StockMetricCard stock={searchState.stock} summary={searchState.summary} highlight />
                  </motion.div>
                ) : (
                  <motion.div key="err" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="flex items-center gap-2 bg-rose-950/40 border border-rose-800/50 rounded-xl px-4 py-3 text-rose-400 text-sm"
                  >
                    <AlertCircle size={15} />
                    Ticker &ldquo;{searchState.ticker}&rdquo; not found or backend unavailable.
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.section>
          )}
        </AnimatePresence>

        {/* Market Overview Grid */}
        <section className="mb-12">
          <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-4">
            Market Overview
          </p>

          {apiError && (
            <div className="flex items-center gap-2 bg-amber-950/40 border border-amber-800/50 rounded-xl px-4 py-3 text-amber-400 text-sm mb-4">
              <AlertCircle size={15} />
              Backend unavailable — run <code className="bg-slate-800 px-1.5 py-0.5 rounded text-xs font-mono">python app.py</code> for live data.
            </div>
          )}

          {loadingStocks ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {Array.from({ length: 7 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          ) : (
            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4"
              initial="hidden"
              animate="visible"
              variants={{ visible: { transition: { staggerChildren: 0.07 } } }}
            >
              {symbols.map(sym => (
                <motion.div
                  key={sym}
                  variants={{
                    hidden: { opacity: 0, y: 24 },
                    visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 160, damping: 20 } },
                  }}
                >
                  <StockMetricCard stock={stocks[sym]} />
                </motion.div>
              ))}
            </motion.div>
          )}
        </section>

        {/* Chat Interface */}
        <ChatInterface />

        <p className="text-center text-[11px] text-slate-700 mt-8 pb-8">
          Educational analysis only — not financial advice &middot; Data: Yahoo Finance
        </p>
      </main>
    </div>
  )
}
