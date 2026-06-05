"""
Strategy Discovery Service

AI-powered analysis of winning trades to reverse-engineer new signal patterns
and propose new strategy variants.

Phase D — Item 3
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class StrategyDiscovery:
    """
    Analyzes winning backtest trades to discover emergent patterns
    and propose new strategy configurations.

    Flow:
        1. Filter winning trades from backtest results
        2. Group by strategy, symbol characteristics, hold duration, etc.
        3. Ask AI to identify common attributes among winners
        4. Produce a StrategyVariant proposal with a named description
    """

    def __init__(self, db: Session = None, ai_provider: str = "anthropic"):
        self.db = db
        self.ai_provider = ai_provider
        self._client = None

    def _get_client(self):
        if self._client:
            return self._client
        import os
        if self.ai_provider == "anthropic":
            try:
                import anthropic
                key = os.getenv("ANTHROPIC_API_KEY")
                if key:
                    self._client = anthropic.Anthropic(api_key=key)
                    return self._client
            except ImportError:
                pass
        try:
            import openai
            key = os.getenv("OPENAI_API_KEY")
            if key:
                self._client = openai.OpenAI(api_key=key)
                self.ai_provider = "openai"
                return self._client
        except ImportError:
            pass
        return None

    # ── Main Entry Point ──────────────────────────────────────────────────────

    async def discover_from_trades(
        self,
        trades: List[Dict],
        current_config: Dict,
        backtest_metrics: Dict,
        min_winning_trades: int = 5,
    ) -> Dict:
        """
        Analyze winning trades and propose new strategy configurations.

        Args:
            trades: Full list of BacktestResult dicts
            current_config: The strategy config that generated these trades
            backtest_metrics: Top-level metrics (return, win rate, etc.)
            min_winning_trades: Skip analysis if fewer winners than this

        Returns:
            {
                'discovered_patterns': [...],       # Pattern objects
                'variant_proposals': [...],         # StrategyVariant-ready dicts
                'top_proposal': {...},              # Best single proposal
                'analysis_summary': str,
                'winning_trades_analyzed': int
            }
        """
        winning_trades = [t for t in trades if t.get("profit_loss", 0) > 0 or t.get("return_pct", 0) > 0]
        if len(winning_trades) < min_winning_trades:
            return {
                "discovered_patterns": [],
                "variant_proposals": [],
                "top_proposal": None,
                "analysis_summary": (
                    f"Insufficient winning trades for discovery "
                    f"({len(winning_trades)} < {min_winning_trades} required)."
                ),
                "winning_trades_analyzed": len(winning_trades),
            }

        logger.info(f"🔍 Strategy discovery: analyzing {len(winning_trades)} winning trades")

        # Run pattern analysis
        patterns = self._extract_patterns(winning_trades)
        logger.info(f"  Found {len(patterns)} preliminary pattern groups")

        # Ask AI for deeper analysis
        ai_result = await self._ai_analyze_patterns(winning_trades, patterns, current_config, backtest_metrics)

        # Convert AI output to variant proposals
        proposals = self._build_proposals(ai_result, current_config, winning_trades)

        top = proposals[0] if proposals else None
        return {
            "discovered_patterns": patterns,
            "variant_proposals": proposals,
            "top_proposal": top,
            "analysis_summary": ai_result.get("summary", ""),
            "winning_trades_analyzed": len(winning_trades),
        }

    # ── Pattern Extraction (heuristic, no AI) ────────────────────────────────

    def _extract_patterns(self, winning_trades: List[Dict]) -> List[Dict]:
        """
        Group winning trades by observable attributes to seed the AI prompt.
        Returns a list of pattern dicts.
        """
        from collections import defaultdict

        strategy_groups: Dict[str, List] = defaultdict(list)
        hold_buckets: Dict[str, List] = defaultdict(list)

        for t in winning_trades:
            strat = t.get("strategy", "unknown")
            strategy_groups[strat].append(t)
            hold_days = t.get("hold_days", 0) or 0
            bucket = "short (<5d)" if hold_days < 5 else "medium (5-14d)" if hold_days <= 14 else "long (>14d)"
            hold_buckets[bucket].append(t)

        patterns = []

        for strat, group in strategy_groups.items():
            returns = [t.get("return_pct", 0) for t in group]
            avg_ret = sum(returns) / len(returns) if returns else 0
            patterns.append({
                "type": "strategy_cluster",
                "strategy": strat,
                "count": len(group),
                "avg_return_pct": round(avg_ret, 2),
                "description": f"{strat} strategy: {len(group)} wins, avg {avg_ret:.1f}% return",
            })

        for bucket, group in hold_buckets.items():
            returns = [t.get("return_pct", 0) for t in group]
            avg_ret = sum(returns) / len(returns) if returns else 0
            patterns.append({
                "type": "hold_duration",
                "bucket": bucket,
                "count": len(group),
                "avg_return_pct": round(avg_ret, 2),
                "description": f"Hold duration {bucket}: {len(group)} wins, avg {avg_ret:.1f}%",
            })

        return patterns

    # ── AI Analysis ───────────────────────────────────────────────────────────

    async def _ai_analyze_patterns(
        self,
        winning_trades: List[Dict],
        patterns: List[Dict],
        current_config: Dict,
        metrics: Dict,
    ) -> Dict:
        """Call AI to analyze winning trade patterns and propose new configs."""
        client = self._get_client()
        if not client:
            return self._heuristic_analysis(winning_trades, patterns, current_config)

        prompt = self._build_discovery_prompt(winning_trades, patterns, current_config, metrics)
        try:
            if self.ai_provider == "anthropic":
                msg = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}],
                )
                raw = msg.content[0].text
            else:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=2048,
                )
                raw = resp.choices[0].message.content

            result = json.loads(raw)
            logger.info("✅ AI discovery analysis complete")
            return result
        except Exception as e:
            logger.warning(f"AI discovery call failed, using heuristic: {e}")
            return self._heuristic_analysis(winning_trades, patterns, current_config)

    def _build_discovery_prompt(
        self,
        winning_trades: List[Dict],
        patterns: List[Dict],
        current_config: Dict,
        metrics: Dict,
    ) -> str:
        # Truncate trades list to avoid token limits
        sample = winning_trades[:50]
        trade_summary = [
            {
                "symbol": t.get("symbol"),
                "strategy": t.get("strategy"),
                "return_pct": round(t.get("return_pct", 0), 2),
                "hold_days": t.get("hold_days"),
                "exit_reason": t.get("exit_reason"),
                "signal_metadata": t.get("signal_metadata", {}),
                "params_used": t.get("params_used", {}),
            }
            for t in sample
        ]
        return f"""You are an expert quantitative analyst performing strategy discovery.

CURRENT STRATEGY CONFIG:
{json.dumps(current_config, indent=2)}

OVERALL BACKTEST METRICS:
{json.dumps(metrics, indent=2)}

PRELIMINARY PATTERN GROUPS:
{json.dumps(patterns, indent=2)}

WINNING TRADES SAMPLE (top {len(sample)} of total):
{json.dumps(trade_summary, indent=2)}

TASK:
1. Identify the 2-3 most distinctive patterns shared by the winning trades
2. For each pattern, propose a specific named strategy variant (a modified config)
3. Explain in plain English what makes these trades special
4. Name each variant clearly (e.g., "Tight Earnings Momentum", "Long Seasonal Swing")

Return JSON:
{{
  "summary": "2-3 sentence narrative of what you found",
  "discovered_patterns": [
    {{
      "name": "Short descriptive name",
      "description": "What this pattern is",
      "key_attributes": {{"attr": "value"}},
      "supporting_trade_count": 10
    }}
  ],
  "variant_proposals": [
    {{
      "name": "Variant Name",
      "rationale": "Why this config should outperform",
      "param_overrides": {{
        "strategy_name.paramName": new_value
      }}
    }}
  ]
}}"""

    def _heuristic_analysis(
        self, winning_trades: List[Dict], patterns: List[Dict], current_config: Dict
    ) -> Dict:
        """Fallback when AI is unavailable — simple heuristic analysis."""
        if not winning_trades:
            return {"summary": "No winning trades to analyze.", "variant_proposals": [], "discovered_patterns": []}

        # Find best-performing strategy
        from collections import defaultdict
        strat_returns = defaultdict(list)
        for t in winning_trades:
            strat_returns[t.get("strategy", "unknown")].append(t.get("return_pct", 0))
        best_strat = max(strat_returns, key=lambda s: sum(strat_returns[s]) / len(strat_returns[s]))
        avg = sum(strat_returns[best_strat]) / len(strat_returns[best_strat])

        return {
            "summary": (
                f"Heuristic analysis: '{best_strat}' strategy produced the highest average winning "
                f"return ({avg:.1f}%). Consider amplifying its parameters."
            ),
            "discovered_patterns": patterns,
            "variant_proposals": [
                {
                    "name": f"Amplified {best_strat.title()}",
                    "rationale": f"Focus on {best_strat} signals which averaged {avg:.1f}% per win.",
                    "param_overrides": {},
                }
            ],
        }

    # ── Proposal Builder ──────────────────────────────────────────────────────

    def _build_proposals(
        self, ai_result: Dict, current_config: Dict, winning_trades: List[Dict]
    ) -> List[Dict]:
        """
        Convert AI variant proposals into StrategyVariant-ready dicts.
        Merges param_overrides into a copy of current_config.
        """
        import copy

        proposals = []
        for raw in ai_result.get("variant_proposals", []):
            merged_config = copy.deepcopy(current_config)
            overrides = raw.get("param_overrides", {})
            # Apply overrides: keys like "earnings.profitTarget" → nested path
            for key, val in overrides.items():
                parts = key.split(".")
                if len(parts) == 2:
                    strat, param = parts
                    sc = merged_config.setdefault("strategy_config", {})
                    sc.setdefault(strat, {}).setdefault("params", {}).setdefault(param, {})
                    if isinstance(sc[strat]["params"][param], dict):
                        sc[strat]["params"][param]["value"] = val
                    else:
                        sc[strat]["params"][param] = val

            proposals.append({
                "name": raw.get("name", "Discovered Variant"),
                "source": "ai_discovery",
                "config": merged_config,
                "ai_summary": raw.get("rationale", ""),
                "ai_proposed_changes": overrides,
                "backtest_total_trades": len(winning_trades),
            })

        return proposals

    # ── DB Save Helper ────────────────────────────────────────────────────────

    def save_proposals_to_db(
        self, proposals: List[Dict], user_id: str = "default"
    ) -> List[str]:
        """
        Save discovered variant proposals as StrategyVariant records.
        Returns list of saved variant IDs.
        """
        if not self.db:
            logger.warning("No DB session — cannot save discovery proposals")
            return []

        from app.models.strategy_variant import StrategyVariant
        import uuid

        saved_ids = []
        for prop in proposals:
            existing_count = self.db.query(StrategyVariant).filter(
                StrategyVariant.name == prop["name"],
                StrategyVariant.user_id == user_id,
            ).count()
            variant = StrategyVariant(
                id=str(uuid.uuid4()),
                name=prop["name"],
                source="ai_discovery",
                user_id=user_id,
                version=existing_count + 1,
                config=prop["config"],
                ai_summary=prop.get("ai_summary"),
                ai_proposed_changes=prop.get("ai_proposed_changes"),
                backtest_total_trades=prop.get("backtest_total_trades"),
                is_active=False,
            )
            self.db.add(variant)
            saved_ids.append(variant.id)

        try:
            self.db.commit()
            logger.info(f"💡 Saved {len(saved_ids)} discovery proposals to DB")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save discovery proposals: {e}")
            return []

        return saved_ids


# ── Singleton ─────────────────────────────────────────────────────────────────

_discovery_instance: Optional[StrategyDiscovery] = None


def get_strategy_discovery(db: Session = None, ai_provider: str = "anthropic") -> StrategyDiscovery:
    global _discovery_instance
    if _discovery_instance is None or db is not None:
        _discovery_instance = StrategyDiscovery(db=db, ai_provider=ai_provider)
    return _discovery_instance
