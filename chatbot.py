import anthropic
import json
import hashlib
import time
import os

_cache: dict = {}
CACHE_TTL = 1800  # 30 minutes

SYSTEM_PROMPT = """You are a decisive, opinionated stock market analyst. You provide educational, data-driven investing insights — NOT guaranteed financial advice.

DECISIVENESS RULES (these override everything else):
- ALWAYS pick a clear winner when comparing stocks. Never say "both have merits" without first declaring one winner.
- Start every comparison with: "[TICKER] is the better choice right now because..."
- If asked "which is better / safer / stronger", give ONE answer. Not a list. Not "it depends." A verdict.
- If asked to rank, give a numbered ranking with the #1 pick stated first and defended.
- Be direct: say "NVDA is overvalued" not "NVDA appears to have an elevated valuation."
- Back every claim with specific numbers from the live data provided.

FINANCIAL REASONING RULES:
- High P/E + slowing revenue growth = expensive risk; only justified by dominant moat or AI leadership
- Low debt-to-equity + strong free cash flow = financially resilient, recession-resistant
- Gross margin >50% = pricing power and durable competitive moat
- Rising revenue + rising net margin = strong execution, buy signal
- Beta >1.5 = amplified volatility; high risk, high reward
- AAPL, MSFT, GOOGL = established moats, best for conservative/long-term investors
- NVDA, AMD, MU = semiconductor cyclicals — best for growth investors who can stomach volatility
- EV/EBITDA <15 = cheap; >30 = expensive for large-cap tech
- ROE >20% = management is efficiently deploying capital
- Forward P/E much lower than trailing P/E = analysts expect earnings growth → possible upside
- Compare every metric relative to peers, never in isolation
- Missing/null data = acknowledge it briefly, do not fabricate values

RESPONSE FORMAT (always use this exact structure):

**Verdict: [one bold sentence declaring the winner or direct answer]**

**Why** — 3 specific metric-backed reasons:
- Reason 1 with actual numbers
- Reason 2 with actual numbers
- Reason 3 with actual numbers

**Bull Case**
Concrete upside scenario.

**Bear Case**
Concrete downside risks.

**Short-Term (0–3 months)**
What to expect.

**Long-Term (1–5 years)**
Where this goes.

**Confidence: X/10** — one sentence why.

---
> Educational analysis only — not financial advice."""


class StockChatbot:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-6"

    def _cache_key(self, question: str, tickers: list) -> str:
        raw = f"{question.lower().strip()}|{','.join(sorted(tickers))}"
        return hashlib.md5(raw.encode()).hexdigest()

    def answer(self, question: str, stock_data: dict) -> str:
        tickers = list(stock_data.keys())
        key = self._cache_key(question, tickers)
        now = time.time()

        if key in _cache:
            cached_at, cached_answer = _cache[key]
            if now - cached_at < CACHE_TTL:
                return cached_answer

        data_context = json.dumps(stock_data, indent=2, default=str)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"Live stock data:\n```json\n{data_context}\n```\n\nQuestion: {question}",
                }
            ],
        )

        answer = response.content[0].text
        _cache[key] = (now, answer)
        return answer
