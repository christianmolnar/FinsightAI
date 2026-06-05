"""
AI Trade Scorer — Phase C

Scores every trade signal before entry using AI, providing a per-trade
confidence gate that sits between signal generation (StrategyExecutor)
and trade execution (Backtester / LiveScanner).

Architecture:
    StrategyExecutor (signal)
        ↓
    AITradeScorer  ← HERE (Phase C)
        ↓
    Backtester / LiveScanner

Returns:
    score       0–100   (int)
    approved    bool    (score >= threshold)
    reasoning   str     (AI explanation, 1-2 sentences)
    provider    str     ("anthropic" | "openai" | "fallback")
"""

import json
import logging
import os
from typing import Dict, Optional

import anthropic
from openai import OpenAI

logger = logging.getLogger(__name__)

# Default threshold — trades scoring below this are rejected
DEFAULT_THRESHOLD = 60


class AITradeScorer:
    """
    Scores a single trade signal using Claude or GPT.

    Usage:
        scorer = AITradeScorer()
        result = await scorer.score(signal, threshold=60)
        if result["approved"]:
            # execute trade
    """

    def __init__(self, ai_provider: str = "anthropic"):
        """
        Args:
            ai_provider: "anthropic" (Claude, default) or "openai" (GPT-4o-mini)
        """
        self.ai_provider = ai_provider
        self._client = None
        self._model = None
        self._init_client()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_client(self) -> None:
        """Lazy-init AI client — falls back gracefully if keys are missing."""
        if self.ai_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self._client = anthropic.Anthropic(api_key=api_key)
                self._model = "claude-3-haiku-20240307"   # Fast + cheap for per-trade scoring
                logger.info("🤖 AITradeScorer: using Claude 3 Haiku")
            else:
                logger.warning("⚠️  ANTHROPIC_API_KEY not set — will try OpenAI fallback")
                self.ai_provider = "openai"
                self._init_openai()
        else:
            self._init_openai()

    def _init_openai(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self._client = OpenAI(api_key=api_key)
            self._model = "gpt-4o-mini"
            logger.info("🤖 AITradeScorer: using GPT-4o-mini")
        else:
            logger.warning("⚠️  No AI API keys available — AITradeScorer will use heuristic fallback")
            self._client = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def score(
        self,
        signal: Dict,
        threshold: int = DEFAULT_THRESHOLD,
        market_context: Optional[Dict] = None,
    ) -> Dict:
        """
        Score a trade signal.

        Args:
            signal:          Opportunity dict from StrategyExecutor (has symbol, strategy,
                             score, reason, signal_metadata, params_used, exit_params).
            threshold:       Minimum score (0–100) to approve the trade.
            market_context:  Optional extra market data (VIX, sector trend, etc.).

        Returns:
            {
                "score":      int (0–100),
                "approved":   bool,
                "reasoning":  str,
                "provider":   str,
            }
        """
        if self._client is None:
            return self._heuristic_score(signal, threshold)

        try:
            prompt = self._build_prompt(signal, market_context)

            if self.ai_provider == "anthropic":
                raw = self._call_claude(prompt)
            else:
                raw = self._call_openai(prompt)

            result = self._parse_response(raw)
            result["approved"] = result["score"] >= threshold
            return result

        except Exception as e:
            logger.warning(f"AITradeScorer AI call failed for {signal.get('symbol')}: {e} — using heuristic")
            return self._heuristic_score(signal, threshold)

    # ------------------------------------------------------------------
    # AI calls (synchronous — avoids async complexity in hot path)
    # ------------------------------------------------------------------

    def _call_claude(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def _call_openai(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=256,
        )
        return response.choices[0].message.content

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_prompt(self, signal: Dict, market_context: Optional[Dict]) -> str:
        symbol = signal.get("symbol", "UNKNOWN")
        strategy = signal.get("strategy", "unknown")
        scanner_score = signal.get("score", 0)
        reason = signal.get("reason", "")
        signal_meta = signal.get("signal_metadata", {})
        params_used = signal.get("params_used", {})
        exit_params = signal.get("exit_params", {})

        context_block = ""
        if market_context:
            context_block = f"\nMARKET CONTEXT:\n{json.dumps(market_context, indent=2)}\n"

        return f"""You are a quantitative trader evaluating a single trade signal.
Score this signal 0–100 based on quality, risk/reward, and conviction.

SIGNAL:
- Symbol:         {symbol}
- Strategy:       {strategy}
- Scanner score:  {scanner_score:.1f}/100
- Reason:         {reason}
- Signal detail:  {json.dumps(signal_meta, indent=2)}
- Params used:    {json.dumps(params_used, indent=2)}
- Exit params:    profit_target={exit_params.get('profit_target')}%, stop_loss={exit_params.get('stop_loss')}%
{context_block}
SCORING GUIDE:
  80–100  Very high conviction — strong setup, good risk/reward
  60–79   Moderate conviction — entry acceptable
  40–59   Marginal — borderline, flag as weak
  0–39    Reject — insufficient evidence or poor risk/reward

Respond ONLY in this exact JSON format (no extra text):
{{
  "score": <integer 0-100>,
  "reasoning": "<one concise sentence explaining the score>"
}}"""

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _parse_response(self, raw: str) -> Dict:
        """Parse AI JSON response, returning fallback on error."""
        try:
            data = json.loads(raw.strip())
            score = int(data.get("score", 50))
            score = max(0, min(100, score))
            reasoning = str(data.get("reasoning", "AI scored this signal."))
            return {"score": score, "reasoning": reasoning, "provider": self.ai_provider}
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse AITradeScorer response: {e}. Raw: {raw[:200]}")
            return {"score": 50, "reasoning": "AI response parse error — neutral score assigned.", "provider": self.ai_provider}

    # ------------------------------------------------------------------
    # Heuristic fallback (no AI keys available)
    # ------------------------------------------------------------------

    def _heuristic_score(self, signal: Dict, threshold: int) -> Dict:
        """
        Pure heuristic score when no AI is available.
        Mirrors the scanner score with a small penalty for uncertainty.
        """
        scanner_score = signal.get("score", 50)
        # Apply a small uncertainty discount
        score = int(scanner_score * 0.85)
        score = max(0, min(100, score))
        return {
            "score": score,
            "approved": score >= threshold,
            "reasoning": f"Heuristic fallback: scanner score {scanner_score:.1f} → adjusted {score}.",
            "provider": "fallback",
        }


# ---------------------------------------------------------------------------
# Module-level singleton (shared across backtester + live scanner)
# ---------------------------------------------------------------------------

_scorer: Optional[AITradeScorer] = None


def get_ai_trade_scorer(ai_provider: str = "anthropic") -> AITradeScorer:
    """Return a cached AITradeScorer instance."""
    global _scorer
    if _scorer is None:
        _scorer = AITradeScorer(ai_provider=ai_provider)
    return _scorer
