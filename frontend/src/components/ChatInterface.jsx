import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Zap } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import SkeletonCard from './SkeletonCard'

const QUICK_PROMPTS = [
  'Is NVDA overvalued right now?',
  'Compare AAPL vs MSFT long term.',
  'Which stock has the strongest balance sheet?',
  'Compare NVDA vs AMD in AI chips.',
  'Which stock looks safest in a recession?',
  'Rank these companies by growth potential.',
  'Which has stronger margins: AMD or MU?',
  'Best stock to buy for $1000 today?',
]

const SUPPORTED = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'AMD', 'MU']

function ThinkingBubble() {
  return (
    <motion.div
      key="thinking"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10, scale: 0.96 }}
      transition={{ duration: 0.2 }}
      className="space-y-3"
    >
      <div className="flex items-center gap-2 text-sky-400">
        <Bot size={14} />
        <span className="text-xs font-semibold uppercase tracking-wider">Analyzing live data…</span>
        <span className="flex gap-1">
          {[0, 1, 2].map(i => (
            <motion.span
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-sky-500"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
            />
          ))}
        </span>
      </div>
      <SkeletonCard />
    </motion.div>
  )
}

function AssistantMessage({ content }) {
  return (
    <motion.div
      key="answer"
      initial={{ opacity: 0, y: 16, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 180, damping: 22 }}
      className="bg-slate-800/70 border border-slate-700/60 rounded-2xl p-5"
    >
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-700/50">
        <Bot size={14} className="text-sky-400" />
        <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider">Investment Agent</span>
      </div>
      <div className="prose prose-sm prose-invert max-w-none text-slate-300 leading-relaxed
        [&_h1]:text-white [&_h1]:text-base [&_h1]:font-bold [&_h1]:mt-4 [&_h1]:mb-2
        [&_h2]:text-white [&_h2]:text-sm [&_h2]:font-semibold [&_h2]:mt-3 [&_h2]:mb-1.5
        [&_h3]:text-slate-200 [&_h3]:text-xs [&_h3]:font-semibold [&_h3]:mt-2 [&_h3]:mb-1
        [&_strong]:text-white
        [&_ul]:my-1.5 [&_ul]:pl-4
        [&_ol]:my-1.5 [&_ol]:pl-4
        [&_li]:my-0.5 [&_li]:text-xs
        [&_p]:my-1.5 [&_p]:text-xs
        [&_blockquote]:border-l-2 [&_blockquote]:border-slate-600 [&_blockquote]:pl-3 [&_blockquote]:my-2 [&_blockquote]:text-slate-500 [&_blockquote]:italic [&_blockquote]:text-xs
        [&_hr]:border-slate-700 [&_hr]:my-3
        [&_code]:bg-slate-700 [&_code]:px-1 [&_code]:rounded [&_code]:text-emerald-400 [&_code]:text-xs">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </div>
    </motion.div>
  )
}

function UserMessage({ content }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.18 }}
      className="flex justify-end"
    >
      <div className="flex items-start gap-2 max-w-[85%]">
        <div className="bg-sky-900/60 border border-sky-800/60 rounded-2xl rounded-tr-md px-4 py-2.5 text-sm text-sky-100">
          {content}
        </div>
        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-slate-700 flex items-center justify-center mt-0.5">
          <User size={12} className="text-slate-400" />
        </div>
      </div>
    </motion.div>
  )
}

export default function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isThinking])

  const send = async (question) => {
    const q = question?.trim() || input.trim()
    if (!q || isThinking) return
    setInput('')
    setMessages(m => [...m, { type: 'user', content: q }])
    setIsThinking(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, tickers: SUPPORTED }),
      })
      if (res.ok) {
        const data = await res.json()
        setMessages(m => [...m, { type: 'assistant', content: data.answer }])
      } else {
        const err = await res.json().catch(() => ({}))
        setMessages(m => [...m, { type: 'error', content: err.error || 'Request failed.' }])
      }
    } catch {
      setMessages(m => [...m, {
        type: 'error',
        content: 'Could not reach the AI backend. Make sure `python app.py` is running.',
      }])
    } finally {
      setIsThinking(false)
    }
  }

  return (
    <section>
      <div className="flex items-center gap-2 mb-4">
        <Zap size={16} className="text-amber-400" />
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Investment Agent</h2>
      </div>

      <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl overflow-hidden">
        {/* Quick prompts */}
        <div className="flex flex-wrap gap-2 p-4 border-b border-slate-700/50">
          {QUICK_PROMPTS.map(p => (
            <button
              key={p}
              onClick={() => send(p)}
              disabled={isThinking}
              className="px-3 py-1.5 text-xs border border-slate-700 rounded-full text-slate-400 hover:border-sky-700 hover:text-sky-300 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Message history */}
        <div className="min-h-[200px] max-h-[560px] overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && !isThinking && (
            <div className="text-center py-8 text-slate-600 text-sm">
              <Bot size={32} className="mx-auto mb-2 opacity-30" />
              <p>Ask anything about these 7 stocks — powered by live financial data and Claude AI.</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i}>
              {msg.type === 'user' && <UserMessage content={msg.content} />}
              {msg.type === 'assistant' && <AssistantMessage content={msg.content} />}
              {msg.type === 'error' && (
                <div className="bg-rose-900/30 border border-rose-800 rounded-xl px-4 py-3 text-rose-400 text-xs">
                  {msg.content}
                </div>
              )}
            </div>
          ))}

          {/* Thinking state — AnimatePresence ensures it cleanly disappears */}
          <AnimatePresence mode="wait">
            {isThinking && <ThinkingBubble />}
          </AnimatePresence>

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-slate-700/50">
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
              placeholder="Ask about valuations, comparisons, risks…"
              disabled={isThinking}
              className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-sky-600 disabled:opacity-50 transition-colors"
            />
            <button
              onClick={() => send()}
              disabled={!input.trim() || isThinking}
              className="flex items-center justify-center w-10 h-10 rounded-xl bg-sky-600 hover:bg-sky-500 disabled:bg-slate-700 disabled:text-slate-600 text-white transition-colors"
            >
              <Send size={15} />
            </button>
          </div>
          <p className="text-[10px] text-slate-700 mt-2 text-center">
            Educational analysis only — not financial advice.
          </p>
        </div>
      </div>
    </section>
  )
}
