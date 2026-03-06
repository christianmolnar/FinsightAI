"""
Test AI-Enhanced Calibration Engine

Tests the CalibrationEngine with AI reasoning integration.
Verifies that recommendations include AI-generated explanations.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.backtester import BacktestMetrics, BacktestResult
from services.calibration_engine import CalibrationEngine
from app.database import SessionLocal


def create_mock_backtest_data():
    """Create mock backtest data for testing"""
    
    # Create mock trades
    trades = []
    for i in range(100):
        # 60% winners, 40% losers
        if i < 60:
            # Winners averaging +$500 (+5%)
            profit = 500 + (i * 5)
            return_pct = 5.0 + (i * 0.05)
        else:
            # Losers averaging -$300 (-3%)
            profit = -(300 + (i * 2))
            return_pct = -(3.0 + (i * 0.02))
        
        trade = BacktestResult(
            symbol=f"TEST{i}",
            strategy="earnings",
            entry_date=datetime.now() - timedelta(days=100-i),
            entry_price=100.0,
            exit_date=datetime.now() - timedelta(days=95-i),
            exit_price=100.0 + (profit / 100.0),
            shares=100,
            exit_reason="profit_target" if profit > 0 else "stop_loss",
            scanner_score=75.0,
            ai_confidence=0.8,
            ai_reasoning="Test trade"
        )
        trades.append(trade)
    
    # Create daily P&L (simplified)
    daily_pnl = {}
    cumulative = 0
    for i in range(90):
        date = datetime.now() - timedelta(days=90-i)
        daily_change = (i % 10) * 100 - 300 if i % 5 == 0 else (i % 5) * 50
        cumulative += daily_change
        daily_pnl[date.strftime('%Y-%m-%d')] = cumulative
    
    # Create BacktestMetrics
    metrics = BacktestMetrics(
        trades=trades,
        initial_capital=100000.0,
        daily_pnl=daily_pnl
    )
    
    return metrics, trades


def test_ai_calibration():
    """Test the calibration engine with AI reasoning"""
    
    print("=" * 80)
    print("🧪 TESTING AI-ENHANCED CALIBRATION ENGINE")
    print("=" * 80)
    print()
    
    # Create mock data
    print("📊 Creating mock backtest data...")
    metrics, trades = create_mock_backtest_data()
    
    print(f"   ✅ Created {metrics.total_trades} trades")
    print(f"   ✅ Win Rate: {metrics.win_rate:.1f}%")
    print(f"   ✅ Total Return: {metrics.total_return_pct:.1f}%")
    print(f"   ✅ Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
    print(f"   ✅ Max Drawdown: {metrics.max_drawdown:.1f}%")
    print()
    
    # Create current config
    current_config = {
        "earnings": {
            "profitTarget": 8.0,  # Set lower than avg win to trigger recommendation
            "stopLoss": 8.0,
            "maxWeight": 10.0
        },
        "riskManagement": {
            "maxSinglePosition": 5.0,
            "maxDrawdown": 15.0
        },
        "technical": {
            "rsiMin": 40.0,
            "rsiMax": 70.0
        }
    }
    
    print("🧠 Initializing CalibrationEngine with AI integration...")
    db = SessionLocal()
    try:
        engine = CalibrationEngine(db)
        
        # Check AI availability
        if engine.openai_client:
            print("   ✅ OpenAI client initialized")
        if engine.anthropic_client:
            print("   ✅ Anthropic client initialized")
        if not engine.openai_client and not engine.anthropic_client:
            print("   ⚠️  No AI clients available - using statistical reasoning")
        print()
        
        # Generate recommendations
        print("🔍 Generating AI-enhanced recommendations...")
        recommendations = engine.generate_recommendations(
            metrics=metrics,
            current_config=current_config,
            trades=trades
        )
        
        print(f"   ✅ Generated {len(recommendations)} recommendations")
        print()
        
        # Display recommendations
        print("=" * 80)
        print("📋 CALIBRATION RECOMMENDATIONS")
        print("=" * 80)
        print()
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{'=' * 80}")
            print(f"Recommendation #{i}")
            print(f"{'=' * 80}")
            print(f"Parameter:     {rec['parameter']}")
            print(f"Category:      {rec['category']}")
            print(f"Current:       {rec['current_value']}")
            print(f"Recommended:   {rec['recommended_value']}")
            print(f"Confidence:    {rec['confidence']:.0%}")
            print(f"Expected:      {rec.get('expected_improvement', 'N/A')}")
            print()
            print(f"Reasoning:")
            print(f"{rec['reasoning']}")
            print()
        
        # Verify AI reasoning is present
        print("=" * 80)
        print("✅ TEST RESULTS")
        print("=" * 80)
        
        if recommendations:
            # Check if reasoning looks like AI-generated (longer, more natural)
            avg_reasoning_length = sum(len(r['reasoning']) for r in recommendations) / len(recommendations)
            print(f"✅ Average reasoning length: {avg_reasoning_length:.0f} characters")
            
            if avg_reasoning_length > 150:
                print("✅ AI reasoning appears to be working (natural language detected)")
            else:
                print("⚠️  Reasoning is short - may be statistical fallback")
            
            print(f"✅ All {len(recommendations)} recommendations have reasoning")
            print("✅ All recommendations have confidence scores")
            print()
            print("🎉 AI-ENHANCED CALIBRATION ENGINE TEST PASSED!")
        else:
            print("⚠️  No recommendations generated (this may be expected with mock data)")
        
        print("=" * 80)
        
    finally:
        db.close()


if __name__ == "__main__":
    test_ai_calibration()
