from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.database import get_db
from services.calibration_engine import CalibrationEngine
from app.models.backtest import BacktestMetrics

router = APIRouter(prefix="/api/calibration", tags=["calibration"])


class TradeData(BaseModel):
    symbol: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    pnl: float
    pnl_percent: float
    exit_reason: str


class CalibrationRequest(BaseModel):
    metrics: Dict[str, Any]
    current_config: Dict[str, Any]
    trades: List[TradeData]


class CalibrationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    backtest_summary: Dict[str, Any]
    report_id: Optional[int] = None


@router.post("/analyze", response_model=CalibrationResponse)
async def analyze_backtest(
    request: CalibrationRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze backtest results and generate calibration recommendations.
    """
    try:
        # Initialize calibration engine
        engine = CalibrationEngine(db)
        
        # Convert metrics dict to BacktestMetrics object
        metrics_data = request.metrics
        metrics = BacktestMetrics(
            total_trades=metrics_data['summary']['total_trades'],
            winning_trades=metrics_data['summary']['winning_trades'],
            losing_trades=metrics_data['summary']['losing_trades'],
            win_rate=metrics_data['summary']['win_rate'],
            total_return=metrics_data['returns']['net_profit'],
            total_return_pct=metrics_data['returns']['total_return_pct'],
            sharpe_ratio=metrics_data.get('risk', {}).get('sharpe_ratio', 0.0),
            max_drawdown=metrics_data.get('risk', {}).get('max_drawdown', 0.0),
            avg_win=metrics_data['performance']['avg_win'],
            avg_loss=metrics_data['performance']['avg_loss'],
            profit_factor=metrics_data['performance']['profit_factor'],
            avg_hold_days=metrics_data['performance']['avg_hold_days'],
        )
        
        # Convert trades to list of dicts
        trades_list = [trade.dict() for trade in request.trades]
        
        # Generate recommendations
        recommendations = engine.generate_recommendations(
            metrics=metrics,
            current_config=request.current_config,
            trades=trades_list
        )
        
        # Save to database
        report_id = engine.save_backtest_report(
            metrics=metrics,
            config=request.current_config,
            recommendations=recommendations,
            start_date=datetime.now(),  # TODO: Get from request
            end_date=datetime.now(),     # TODO: Get from request
            user_id="default"
        )
        
        return CalibrationResponse(
            recommendations=recommendations,
            backtest_summary={
                "total_trades": metrics.total_trades,
                "win_rate": metrics.win_rate,
                "total_return_pct": metrics.total_return_pct,
                "sharpe_ratio": metrics.sharpe_ratio,
            },
            report_id=report_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calibration analysis failed: {str(e)}")


@router.get("/reports/{report_id}")
async def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a calibration report by ID.
    """
    try:
        engine = CalibrationEngine(db)
        report = engine.get_backtest_report(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "report_id": report.id,
            "created_at": report.created_at,
            "total_trades": report.total_trades,
            "win_rate": report.win_rate,
            "total_return_pct": report.total_return_pct,
            "recommendations": report.recommendations,
            "applied": report.applied,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report: {str(e)}")


@router.get("/reports")
async def get_recent_reports(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent calibration reports.
    """
    try:
        engine = CalibrationEngine(db)
        reports = engine.get_recent_reports(limit=limit)
        
        return {
            "reports": [
                {
                    "report_id": r.id,
                    "created_at": r.created_at,
                    "total_trades": r.total_trades,
                    "win_rate": r.win_rate,
                    "total_return_pct": r.total_return_pct,
                    "applied": r.applied,
                }
                for r in reports
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reports: {str(e)}")


@router.post("/reports/{report_id}/apply")
async def mark_applied(
    report_id: int,
    applied_recs: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Mark recommendations as applied.
    """
    try:
        engine = CalibrationEngine(db)
        success = engine.mark_recommendations_applied(report_id, applied_recs)
        
        if not success:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {"success": True, "message": "Recommendations marked as applied"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark applied: {str(e)}")
