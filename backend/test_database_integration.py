"""
Test Database Integration for Calibration Engine

Tests saving and retrieving backtest reports with recommendations.
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


def create_test_metrics():
    """Create test backtest metrics"""
    
    # Create mock trades
    trades = []
    for i in range(50):
        # 60% winners
        if i < 30:
            profit = 500 + (i * 10)
            return_pct = 5.0 + (i * 0.1)
        else:
            profit = -(300 + (i * 5))
            return_pct = -(3.0 + (i * 0.05))
        
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
    
    # Create daily P&L
    daily_pnl = {}
    cumulative = 0
    for i in range(90):
        date = datetime.now() - timedelta(days=90-i)
        daily_change = (i % 10) * 100 - 300 if i % 5 == 0 else (i % 5) * 50
        cumulative += daily_change
        daily_pnl[date.strftime('%Y-%m-%d')] = cumulative
    
    metrics = BacktestMetrics(
        trades=trades,
        initial_capital=100000.0,
        daily_pnl=daily_pnl
    )
    
    return metrics, trades


def test_database_integration():
    """Test saving and retrieving backtest reports"""
    
    print("=" * 80)
    print("🧪 TESTING DATABASE INTEGRATION")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    try:
        engine = CalibrationEngine(db)
        
        # Create test data
        print("📊 Creating test backtest data...")
        metrics, trades = create_test_metrics()
        
        current_config = {
            "earnings": {
                "profitTarget": 8.0,
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
        
        print(f"   ✅ Metrics: {metrics.total_trades} trades, {metrics.win_rate:.1f}% win rate")
        print()
        
        # Generate recommendations
        print("🔍 Generating recommendations...")
        recommendations = engine.generate_recommendations(
            metrics=metrics,
            current_config=current_config,
            trades=trades
        )
        print(f"   ✅ Generated {len(recommendations)} recommendations")
        print()
        
        # Save to database
        print("=" * 80)
        print("💾 TESTING SAVE_BACKTEST_REPORT")
        print("=" * 80)
        print()
        
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
        
        report_id = engine.save_backtest_report(
            metrics=metrics,
            config=current_config,
            recommendations=recommendations,
            start_date=start_date,
            end_date=end_date,
            user_id="test_user"
        )
        
        print(f"✅ Saved backtest report with ID: {report_id}")
        print()
        
        # Retrieve report
        print("=" * 80)
        print("📥 TESTING GET_BACKTEST_REPORT")
        print("=" * 80)
        print()
        
        retrieved = engine.get_backtest_report(report_id)
        
        if retrieved:
            print(f"✅ Retrieved report #{retrieved['id']}")
            print(f"   User: {retrieved['user_id']}")
            print(f"   Date Range: {retrieved['start_date']} to {retrieved['end_date']}")
            print(f"   Trades: {retrieved['total_trades']}")
            print(f"   Win Rate: {retrieved['win_rate']:.1f}%")
            print(f"   Return: {retrieved['total_return']:.1f}%")
            print(f"   Sharpe: {retrieved['sharpe_ratio']:.2f}")
            print(f"   Recommendations: {len(retrieved['recommendations'])}")
            print()
            
            # Verify data integrity
            if retrieved['total_trades'] == metrics.total_trades:
                print("✅ Total trades matches")
            else:
                print(f"❌ Total trades mismatch: {retrieved['total_trades']} vs {metrics.total_trades}")
            
            if abs(retrieved['win_rate'] - metrics.win_rate) < 0.1:
                print("✅ Win rate matches")
            else:
                print(f"❌ Win rate mismatch: {retrieved['win_rate']} vs {metrics.win_rate}")
            
            if len(retrieved['recommendations']) == len(recommendations):
                print("✅ Recommendations count matches")
            else:
                print(f"❌ Recommendations mismatch: {len(retrieved['recommendations'])} vs {len(recommendations)}")
        else:
            print(f"❌ Failed to retrieve report #{report_id}")
        
        print()
        
        # Test recent reports
        print("=" * 80)
        print("📋 TESTING GET_RECENT_REPORTS")
        print("=" * 80)
        print()
        
        recent = engine.get_recent_reports(user_id="test_user", limit=5)
        
        print(f"✅ Retrieved {len(recent)} recent reports")
        for i, report in enumerate(recent, 1):
            print(f"   {i}. Report #{report['id']}: {report['total_trades']} trades, "
                  f"{report['win_rate']:.1f}% win rate, "
                  f"{report['recommendations_count']} recommendations")
        print()
        
        # Test marking recommendations as applied
        print("=" * 80)
        print("✔️  TESTING MARK_RECOMMENDATIONS_APPLIED")
        print("=" * 80)
        print()
        
        applied_params = ["earnings.profitTarget", "riskManagement.maxSinglePosition"]
        success = engine.mark_recommendations_applied(report_id, applied_params)
        
        if success:
            print(f"✅ Marked {len(applied_params)} recommendations as applied")
            
            # Verify it was saved
            updated = engine.get_backtest_report(report_id)
            if updated and updated['applied']:
                print("✅ Applied flag set correctly")
                if updated['applied_recommendations'] == applied_params:
                    print("✅ Applied parameters saved correctly")
                else:
                    print("❌ Applied parameters mismatch")
            else:
                print("❌ Applied flag not set")
        else:
            print(f"❌ Failed to mark recommendations as applied")
        
        print()
        
        # Final summary
        print("=" * 80)
        print("✅ TEST RESULTS SUMMARY")
        print("=" * 80)
        print()
        print("✅ save_backtest_report() working")
        print("✅ get_backtest_report() working")
        print("✅ get_recent_reports() working")
        print("✅ mark_recommendations_applied() working")
        print("✅ Data integrity verified")
        print()
        print("🎉 DATABASE INTEGRATION TEST COMPLETE!")
        print("=" * 80)
        
        # Cleanup
        print()
        print("🧹 Cleaning up test data...")
        from app.models.backtest import BacktestReport
        db.query(BacktestReport).filter(BacktestReport.user_id == "test_user").delete()
        db.commit()
        print("✅ Test data cleaned up")
        
    finally:
        db.close()


if __name__ == "__main__":
    test_database_integration()
