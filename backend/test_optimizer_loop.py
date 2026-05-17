"""
test_optimizer_loop.py

End-to-end test of BacktestOptimizer:
  run backtest → AI analysis → apply recommendation → repeat

Tests that the full loop executes without errors and that:
- Method names are correct (analyze_and_recommend exists)
- _apply_recommendation maps both top-level and strategy params
- Optimizer returns a valid best_config after ≥1 iteration
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from unittest.mock import AsyncMock, MagicMock, patch
from services.backtest_optimizer import BacktestOptimizer
from services.backtest_ai_analyzer import BacktestAIAnalyzer


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_mock_backtest_result(return_pct: float = 15.0):
    return {
        'success': True,
        'metrics': {
            'returns': {
                'initial_capital': 10000,
                'final_capital': 10000 * (1 + return_pct / 100),
                'net_profit': 10000 * return_pct / 100,
                'total_return_pct': return_pct
            },
            'summary': {
                'total_trades': 50,
                'winning_trades': 30,
                'losing_trades': 20,
                'win_rate': 60.0
            },
            'performance': {
                'profit_factor': 1.5,
                'avg_win': 200,
                'avg_loss': -100,
                'avg_hold_days': 8
            }
        },
        'trades': [
            {
                'symbol': 'AAPL',
                'strategy': 'earnings',
                'entry_date': '2024-01-15',
                'exit_date': '2024-01-22',
                'entry_price': 185.0,
                'exit_price': 192.0,
                'shares': 10,
                'profit_loss': 70.0,
                'return_pct': 3.78,
                'hold_days': 7,
                'exit_reason': 'profit_target'
            }
        ] * 50,
        'config': {}
    }


def make_mock_recommendations(param='earnings.stopLoss', value='5.5'):
    return {
        'recommendations': [
            {
                'parameter': param,
                'suggested_value': value,
                'reasoning': 'Stop loss is too wide; tighten to reduce drawdown.',
                'priority': 'high',
                'confidence': '85%',
                'expected_impact': 'Reduce max drawdown by ~1%'
            }
        ],
        'total_trades_analyzed': 50,
        'batches_processed': 1,
        'timestamp': '2026-05-16T00:00:00'
    }


# ── Tests ────────────────────────────────────────────────────────────────────

async def test_method_name_fix():
    """Verify BacktestAIAnalyzer has analyze_and_recommend (not analyze_trades)."""
    analyzer = BacktestAIAnalyzer.__new__(BacktestAIAnalyzer)
    assert hasattr(analyzer, 'analyze_and_recommend'), \
        "analyze_and_recommend method missing — method name bug not fixed"
    assert not hasattr(analyzer, 'analyze_trades'), \
        "analyze_trades should not exist"
    print("✅ Method name: analyze_and_recommend exists")


async def test_apply_recommendation_top_level():
    """_apply_recommendation correctly updates top-level params."""
    optimizer = BacktestOptimizer.__new__(BacktestOptimizer)

    params = {'position_size': 1000, 'max_hold_days': 14, 'confidence_threshold': 0.75}

    # position_size
    result = optimizer._apply_recommendation(params, {
        'parameter': 'position_size', 'suggested_value': '1500'
    })
    assert result['position_size'] == 1500, f"Expected 1500, got {result['position_size']}"
    print("✅ Top-level: position_size applied")

    # confidence_threshold as percentage
    result = optimizer._apply_recommendation(params, {
        'parameter': 'confidence_threshold', 'suggested_value': '80%'
    })
    assert abs(result['confidence_threshold'] - 0.80) < 0.001, \
        f"Expected 0.80, got {result['confidence_threshold']}"
    print("✅ Top-level: confidence_threshold (%) applied")

    # enable_compounding
    result = optimizer._apply_recommendation(params, {
        'parameter': 'enable_compounding', 'suggested_value': 'true'
    })
    assert result['enable_compounding'] is True
    print("✅ Top-level: enable_compounding applied")


async def test_apply_recommendation_strategy_params():
    """_apply_recommendation correctly updates strategy-specific params."""
    optimizer = BacktestOptimizer.__new__(BacktestOptimizer)

    params = {
        'strategy_config': {
            'earnings': {
                'enabled': True,
                'params': {
                    'stopLoss': {'value': 8.0},
                    'profitTarget': {'value': 12.0}
                }
            }
        }
    }

    # earnings.stopLoss via dot notation
    result = optimizer._apply_recommendation(params, {
        'parameter': 'earnings.stopLoss', 'suggested_value': '5.0'
    })
    assert result['strategy_config']['earnings']['params']['stopLoss']['value'] == 5.0, \
        f"Expected 5.0, got {result['strategy_config']['earnings']['params']['stopLoss']['value']}"
    print("✅ Strategy param: earnings.stopLoss (dot notation) applied")

    # earnings Stop Loss via human label
    result = optimizer._apply_recommendation(params, {
        'parameter': 'earnings Stop Loss', 'suggested_value': '6.5'
    })
    assert result['strategy_config']['earnings']['params']['stopLoss']['value'] == 6.5
    print("✅ Strategy param: earnings Stop Loss (human label) applied")

    # seasonality.profitTarget — creates nested path if absent
    params2 = {}
    result = optimizer._apply_recommendation(params2, {
        'parameter': 'seasonality.profitTarget', 'suggested_value': '18.0'
    })
    assert result['strategy_config']['seasonality']['params']['profitTarget']['value'] == 18.0
    print("✅ Strategy param: seasonality.profitTarget (auto-creates path) applied")


async def test_optimizer_full_loop():
    """Full optimize() loop runs 2 iterations with mocked backtester and AI."""
    # Mock backtester
    mock_backtester = MagicMock()
    mock_backtester.db = MagicMock()

    # Mock AI analyzer
    mock_analyzer = MagicMock()
    mock_analyzer.analyze_and_recommend = AsyncMock(
        return_value=make_mock_recommendations('earnings.stopLoss', '5.5')
    )

    optimizer = BacktestOptimizer(
        backtester=mock_backtester,
        ai_analyzer=mock_analyzer,
        db=None
    )

    # Patch _run_backtest to return canned results
    call_count = [0]
    async def mock_run(params):
        call_count[0] += 1
        # Second iteration slightly better to avoid early convergence
        ret = 15.0 + call_count[0] * 3.0
        return make_mock_backtest_result(ret)

    optimizer._run_backtest = mock_run

    initial_params = {
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'initial_capital': 10000,
        'position_size': 1000,
        'max_hold_days': 14,
        'confidence_threshold': 0.75,
        'enable_compounding': True,
        'strategy_config': {
            'earnings': {'enabled': True, 'params': {'stopLoss': {'value': 8.0}}}
        }
    }

    result = await optimizer.optimize(
        initial_params=initial_params,
        max_iterations=2,
        save_to_db=False
    )

    assert result['success'], f"Optimizer failed: {result}"
    assert result['total_iterations'] >= 1
    assert result['best_config'] is not None
    assert result['best_return_pct'] > 0

    # Verify AI was called
    assert mock_analyzer.analyze_and_recommend.called, \
        "analyze_and_recommend was never called — method name still broken"

    print(f"✅ Full loop: {result['total_iterations']} iterations, "
          f"best return {result['best_return_pct']:.1f}%, "
          f"improvement +{result['total_improvement']:.1f}%")


async def test_unknown_param_is_safe():
    """Unknown params should warn and return params unchanged."""
    optimizer = BacktestOptimizer.__new__(BacktestOptimizer)
    params = {'position_size': 1000}
    result = optimizer._apply_recommendation(params, {
        'parameter': 'some_totally_unknown_param_xyz', 'suggested_value': '999'
    })
    assert result['position_size'] == 1000, "Params should be unchanged for unknown param"
    print("✅ Unknown param: safely ignored, params unchanged")


# ── Runner ───────────────────────────────────────────────────────────────────

async def main():
    print("\n" + "=" * 60)
    print("🧪 TESTING BACKTEST OPTIMIZER LOOP")
    print("=" * 60 + "\n")

    tests = [
        ("Method name fix",               test_method_name_fix),
        ("Apply top-level params",         test_apply_recommendation_top_level),
        ("Apply strategy-specific params", test_apply_recommendation_strategy_params),
        ("Full optimizer loop",            test_optimizer_full_loop),
        ("Unknown param safety",           test_unknown_param_is_safe),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            await test_fn()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED [{name}]: {e}")
            import traceback; traceback.print_exc()
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


if __name__ == '__main__':
    ok = asyncio.run(main())
    sys.exit(0 if ok else 1)
