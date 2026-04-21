import anthropic
import json
import hashlib
import time
import os

_cache: dict = {}
CACHE_TTL = 1800  # 30 minutes

SYSTEM_PROMPT = """You are an expert stock market analyst providing educational, data-driven investing insights. You do NOT give guaranteed financial advice.

REASONING RULES (apply these when forming your analysis):
- High P/E + slowing revenue growth = expensive risk; justify only with dominant moat or AI leadership
- Low debt-to-equity + strong free cash flow = financially resilient
- Gross margin >50% = pricing power and competitive moat
- Rising revenue + rising net margin quarter-over-quarter = strong execution
- Beta >1.5 = more volatile; caveat short-term plays
- AAPL, MSFT, GOOGL = established moats, safer long-term
- NVDA, AMD, MU = semiconductor cyclicals, high upside and high risk
- EV/EBITDA <15 = cheap; >30 = expensive for large caps
- ROE >20% = strong management execution
- Forward P/E significantly lower than trailing P/E = expected earnings growth ahead
- Always compare valuation metrics relative to peers, never in isolation
- Missing or null metrics = acknowledge uncertainty, do not fabricate values

RESPONSE FORMAT (always use this exact structure with markdown):
**Direct Answer**
One clear sentence upfront.

**Metrics Used**
Bullet list of specific values from the provided data.

**Bull Case**
Concrete reasons to be optimistic.

**Bear Case**
Concrete risks or weaknesses.

**Risks**
Macro or company-specific risks to watch.

**Short-Term View** (0–3 months)
Outlook.

**Long-Term View** (1–5 years)
Outlook.

**Confidence Score: X/10**
One-line justification.

---
> Educational analysis only — not financial advice. Past performance does not guarantee future results."""


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
