"""
Test Parameter Mapping and Validation

Tests the CalibrationEngine parameter validation and mapping system.
Verifies all parameters have proper metadata and validation.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.calibration_engine import CalibrationEngine
from app.database import SessionLocal


def test_parameter_metadata():
    """Test parameter metadata completeness"""
    
    print("=" * 80)
    print("🧪 TESTING PARAMETER METADATA & VALIDATION")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    try:
        engine = CalibrationEngine(db)
        
        print("📊 Parameter Coverage Analysis")
        print("-" * 80)
        
        # Get all parameters by category
        categories = engine.get_all_parameters()
        
        total_params = 0
        for category, params in categories.items():
            print(f"\n{category.upper()} ({len(params)} parameters):")
            for param in params:
                total_params += 1
                print(f"   {total_params:2d}. {param['name']}")
                print(f"       Display: {param['display_name']}")
                print(f"       Range: {param['min']}-{param['max']}{param['unit']}")
                print(f"       Default: {param['current_default']}{param['unit']}")
        
        print()
        print("=" * 80)
        print(f"TOTAL PARAMETERS: {total_params}")
        print("=" * 80)
        print()
        
        # Expected coverage
        expected_params = {
            "strategy": 10,  # 4 strategies × 2-3 params each
            "risk": 5,      # Risk management parameters
            "technical": 5   # Technical filter parameters
        }
        
        print("📋 Coverage Verification")
        print("-" * 80)
        
        all_good = True
        for category, expected_count in expected_params.items():
            actual_count = len(categories.get(category, []))
            status = "✅" if actual_count >= expected_count else "❌"
            print(f"{status} {category}: {actual_count}/{expected_count} parameters")
            if actual_count < expected_count:
                all_good = False
        
        print()
        
        # Test parameter validation
        print("=" * 80)
        print("🔍 TESTING PARAMETER VALIDATION")
        print("=" * 80)
        print()
        
        test_cases = [
            ("earnings.profitTarget", 15.0, True, "Valid profit target"),
            ("earnings.profitTarget", 30.0, False, "Too high"),
            ("earnings.profitTarget", 2.0, False, "Too low"),
            ("earnings.stopLoss", 10.0, True, "Valid stop loss"),
            ("riskManagement.maxSinglePosition", 7.0, True, "Valid position size"),
            ("riskManagement.maxSinglePosition", 15.0, False, "Position too large"),
            ("technical.rsiMin", 35.0, True, "Valid RSI"),
            ("unknown.parameter", 10.0, False, "Unknown parameter"),
        ]
        
        passed = 0
        failed = 0
        
        for param, value, should_pass, description in test_cases:
            is_valid, error_msg = engine.validate_parameter(param, value)
            
            if is_valid == should_pass:
                print(f"✅ {description}: {param} = {value}")
                if error_msg:
                    print(f"   Note: {error_msg}")
                passed += 1
            else:
                print(f"❌ {description}: {param} = {value}")
                print(f"   Expected: {'valid' if should_pass else 'invalid'}")
                print(f"   Got: {'valid' if is_valid else 'invalid'}")
                if error_msg:
                    print(f"   Error: {error_msg}")
                failed += 1
        
        print()
        print("=" * 80)
        print(f"Validation Tests: {passed} passed, {failed} failed")
        print("=" * 80)
        print()
        
        # Test config snapshot creation
        print("=" * 80)
        print("🔄 TESTING CONFIG SNAPSHOT CREATION")
        print("=" * 80)
        print()
        
        current_config = {
            "earnings": {
                "profitTarget": 12.0,
                "stopLoss": 8.0,
                "maxWeight": 10.0
            },
            "riskManagement": {
                "maxSinglePosition": 5.0,
                "maxDrawdown": 15.0
            }
        }
        
        recommendations = [
            {
                "parameter": "earnings.profitTarget",
                "recommended_value": 15.0
            },
            {
                "parameter": "riskManagement.maxSinglePosition",
                "recommended_value": 6.5
            }
        ]
        
        before, after = engine.create_config_snapshot(current_config, recommendations)
        
        print("BEFORE:")
        print(f"   earnings.profitTarget: {before['earnings']['profitTarget']}%")
        print(f"   riskManagement.maxSinglePosition: {before['riskManagement']['maxSinglePosition']}%")
        print()
        print("AFTER:")
        print(f"   earnings.profitTarget: {after['earnings']['profitTarget']}%")
        print(f"   riskManagement.maxSinglePosition: {after['riskManagement']['maxSinglePosition']}%")
        print()
        
        # Verify changes
        changes_correct = (
            after['earnings']['profitTarget'] == 15.0 and
            after['riskManagement']['maxSinglePosition'] == 6.5
        )
        
        if changes_correct:
            print("✅ Config snapshot creation working correctly")
        else:
            print("❌ Config snapshot has errors")
        
        print()
        
        # Final summary
        print("=" * 80)
        print("✅ TEST RESULTS SUMMARY")
        print("=" * 80)
        
        if total_params >= 20:
            print(f"✅ Parameter coverage: {total_params} parameters defined")
        else:
            print(f"⚠️  Parameter coverage: Only {total_params} parameters (expected 20+)")
        
        if all_good:
            print("✅ All categories meet minimum requirements")
        else:
            print("⚠️  Some categories below expected counts")
        
        if failed == 0:
            print("✅ All validation tests passed")
        else:
            print(f"⚠️  {failed} validation tests failed")
        
        if changes_correct:
            print("✅ Config snapshot creation working")
        
        print()
        print("🎉 PARAMETER MAPPING & VALIDATION TEST COMPLETE!")
        print("=" * 80)
        
    finally:
        db.close()


if __name__ == "__main__":
    test_parameter_metadata()
