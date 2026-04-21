// P/E → 0–1 position on the undervalued→overvalued gauge
export function calcValuationScore(pe, forwardPE) {
  const ratio = forwardPE ?? pe
  if (ratio == null) return null
  if (ratio <= 10) return 0.05
  if (ratio <= 15) return 0.18
  if (ratio <= 20) return 0.32
  if (ratio <= 25) return 0.48
  if (ratio <= 35) return 0.63
  if (ratio <= 50) return 0.78
  if (ratio <= 70) return 0.88
  return 0.96
}

export function valuationLabel(score) {
  if (score == null) return 'N/A'
  if (score < 0.2) return 'Undervalued'
  if (score < 0.38) return 'Fair Value'
  if (score < 0.55) return 'Slightly Elevated'
  if (score < 0.75) return 'Overvalued'
  return 'Very Overvalued'
}

export function valuationColor(score) {
  if (score == null) return 'text-slate-500'
  if (score < 0.2) return 'text-emerald-400'
  if (score < 0.38) return 'text-sky-400'
  if (score < 0.55) return 'text-amber-400'
  if (score < 0.75) return 'text-orange-400'
  return 'text-rose-400'
}

// Beta + debt → 1–100 risk score
export function calcRiskScore(beta, debtToEquity) {
  if (beta == null) return null
  let score = Math.min(95, Math.max(5, beta * 48))
  if (debtToEquity && debtToEquity > 150) score = Math.min(100, score + 10)
  return Math.round(score)
}

export function riskLabel(score) {
  if (score == null) return 'N/A'
  if (score < 20) return 'Very Low'
  if (score < 38) return 'Low'
  if (score < 58) return 'Moderate'
  if (score < 75) return 'High'
  return 'Very High'
}

export function riskColor(score) {
  if (score == null) return 'bg-slate-600 text-slate-300'
  if (score < 38) return 'bg-emerald-900/60 text-emerald-400 border-emerald-700'
  if (score < 58) return 'bg-amber-900/60 text-amber-400 border-amber-700'
  return 'bg-rose-900/60 text-rose-400 border-rose-700'
}

// Metric formatting
export function fmt$(v) {
  if (v == null) return '—'
  return `$${v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export function fmtLarge(v) {
  if (v == null) return '—'
  const av = Math.abs(v)
  if (av >= 1e12) return `$${(v / 1e12).toFixed(2)}T`
  if (av >= 1e9) return `$${(v / 1e9).toFixed(2)}B`
  if (av >= 1e6) return `$${(v / 1e6).toFixed(2)}M`
  return `$${v.toLocaleString()}`
}

export function fmtPct(v) {
  if (v == null) return '—'
  const sign = v >= 0 ? '+' : ''
  return `${sign}${v.toFixed(2)}%`
}

export function fmtNum(v, d = 2) {
  if (v == null) return '—'
  return v.toFixed(d)
}

export function fmtPctRaw(v) {
  if (v == null) return '—'
  return `${(v * 100).toFixed(1)}%`
}

// Auto-generate 3-point reasoning from live stock data
export function generateReasoning(stock) {
  const { pe_ttm, forward_pe, beta, gross_margin, net_margin, debt_to_equity, free_cash_flow } = stock
  const points = []

  // Valuation point
  if (pe_ttm != null) {
    if (pe_ttm < 15) {
      points.push({
        point: `Trading at ${pe_ttm.toFixed(1)}x trailing earnings — well below the tech sector average of ~25x, suggesting potential undervaluation`,
        metric: 'P/E (TTM)',
        source: 'Yahoo Finance',
      })
    } else if (pe_ttm > 50) {
      points.push({
        point: `Trading at ${pe_ttm.toFixed(1)}x trailing earnings — significantly above the 25x sector average, implying the market is pricing in aggressive future growth`,
        metric: 'P/E (TTM)',
        source: 'Yahoo Finance',
      })
    } else {
      const cmp = pe_ttm > 25 ? 'above' : 'in line with'
      points.push({
        point: `Trading at ${pe_ttm.toFixed(1)}x trailing earnings — ${cmp} the sector average of ~25x, indicating ${pe_ttm > 25 ? 'a premium valuation' : 'reasonable pricing'}`,
        metric: 'P/E (TTM)',
        source: 'Yahoo Finance',
      })
    }
  } else if (forward_pe != null) {
    points.push({
      point: `Forward P/E of ${forward_pe.toFixed(1)}x reflects analyst consensus on next-year earnings; compare to sector peers for context`,
      metric: 'Forward P/E',
      source: 'Yahoo Finance',
    })
  }

  // Margin / moat point
  if (gross_margin != null) {
    const pct = (gross_margin * 100).toFixed(1)
    if (gross_margin > 0.55) {
      points.push({
        point: `${pct}% gross margin signals exceptional pricing power and a durable competitive moat`,
        metric: 'Gross Margin',
        source: 'Yahoo Finance',
      })
    } else if (gross_margin > 0.35) {
      points.push({
        point: `${pct}% gross margin is healthy but not dominant — some pricing power without a wide moat`,
        metric: 'Gross Margin',
        source: 'Yahoo Finance',
      })
    } else {
      points.push({
        point: `Thin ${pct}% gross margin reflects commodity-like competition and limited pricing leverage`,
        metric: 'Gross Margin',
        source: 'Yahoo Finance',
      })
    }
  } else if (net_margin != null) {
    const pct = (net_margin * 100).toFixed(1)
    points.push({
      point: `Net margin of ${pct}% reflects overall profitability after all costs; ${net_margin > 0.15 ? 'strong bottom-line execution' : 'margins have room to improve'}`,
      metric: 'Net Margin',
      source: 'Yahoo Finance',
    })
  }

  // Risk / balance sheet point
  if (beta != null) {
    const extra =
      debt_to_equity != null && debt_to_equity > 150
        ? ` Combined with a debt/equity of ${debt_to_equity.toFixed(0)}, leverage amplifies downside risk.`
        : free_cash_flow != null && free_cash_flow > 0
        ? ` Positive free cash flow provides a cushion during downturns.`
        : ''
    if (beta > 1.5) {
      points.push({
        point: `Beta of ${beta.toFixed(2)} — moves ${((beta - 1) * 100).toFixed(0)}% more than the market in either direction; reward and risk are both amplified.${extra}`,
        metric: 'Beta',
        source: 'Yahoo Finance',
      })
    } else if (beta < 0.75) {
      points.push({
        point: `Low beta of ${beta.toFixed(2)} — defensive characteristics; loses less during sell-offs but may lag in bull runs.${extra}`,
        metric: 'Beta',
        source: 'Yahoo Finance',
      })
    } else {
      points.push({
        point: `Beta of ${beta.toFixed(2)} tracks the market closely — moderate volatility with limited systemic hedging benefit.${extra}`,
        metric: 'Beta',
        source: 'Yahoo Finance',
      })
    }
  }

  return points.slice(0, 3)
}
