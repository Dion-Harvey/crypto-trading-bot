# =============================================================================
# INSTITUTIONAL STRATEGY TESTING SUITE
# =============================================================================

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from institutional_strategies import (
    MarketRegimeDetector, 
    CrossAssetCorrelationAnalyzer,
    KellyCriterionSizer,
    MachineLearningSignalGenerator,
    ValueAtRiskCalculator,
    InstitutionalStrategyManager
)

def create_test_data(length=200):
    """Create synthetic test data for validation"""
    np.random.seed(42)  # For reproducible results
    
    # Generate realistic crypto price data
    dates = pd.date_range(start='2024-01-01', periods=length, freq='1h')
    
    # Start with base price trend
    base_price = 45000
    trend = np.linspace(0, 0.2, length)  # 20% upward trend over period
    
    # Add volatility and noise
    volatility = 0.02
    noise = np.random.normal(0, volatility, length)
    
    # Create realistic price movements
    returns = trend + noise
    prices = [base_price]
    
    for i in range(1, length):
        new_price = prices[-1] * (1 + returns[i])
        prices.append(max(1000, new_price))  # Prevent negative prices
    
    # Generate volume data
    base_volume = 1000000
    volume = np.random.normal(base_volume, base_volume * 0.3, length)
    volume = np.maximum(volume, base_volume * 0.1)  # Minimum volume
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': volume
    })
    
    return df

def test_market_regime_detector():
    """Test market regime detection functionality"""
    print("🔍 Testing Market Regime Detector...")
    
    detector = MarketRegimeDetector()
    df = create_test_data(150)
    
    regime_result = detector.detect_regime(df)
    
    # Validate results
    assert 'regime' in regime_result, "Missing regime in result"
    assert 'confidence' in regime_result, "Missing confidence in result"
    assert 'features' in regime_result, "Missing features in result"
    assert regime_result['regime'] in detector.regimes, f"Invalid regime: {regime_result['regime']}"
    assert 0 <= regime_result['confidence'] <= 1, f"Invalid confidence: {regime_result['confidence']}"
    
    print(f"   ✅ Detected regime: {regime_result['regime']} (confidence: {regime_result['confidence']:.2f})")
    print(f"   📊 Features calculated: {len(regime_result['features'])} indicators")
    return True

def test_cross_asset_correlation():
    """Test cross-asset correlation analysis"""
    print("📈 Testing Cross-Asset Correlation Analyzer...")
    
    analyzer = CrossAssetCorrelationAnalyzer()
    df = create_test_data(100)
    btc_returns = df['close'].pct_change().dropna()
    
    corr_result = analyzer.analyze_cross_correlations(btc_returns)
    
    # Validate results
    assert 'correlations' in corr_result, "Missing correlations"
    assert 'regime' in corr_result, "Missing correlation regime"
    assert 'signals' in corr_result, "Missing signals"
    assert 'risk_factors' in corr_result, "Missing risk factors"
    
    print(f"   ✅ Correlation regime: {corr_result['regime']}")
    print(f"   🔗 Asset correlations: {len(corr_result['correlations'])} assets analyzed")
    print(f"   ⚠️ Risk score: {corr_result['risk_factors']['risk_score']:.2f}")
    return True

def test_kelly_criterion_sizer():
    """Test Kelly Criterion position sizing"""
    print("💰 Testing Kelly Criterion Sizer...")
    
    sizer = KellyCriterionSizer()
    
    # Simulate some trade history
    trade_results = [0.02, -0.01, 0.03, -0.015, 0.025, -0.01, 0.04, -0.02, 0.015, -0.01]
    for result in trade_results:
        sizer.add_trade_result(result)
    
    # Test position sizing
    kelly_size = sizer.calculate_kelly_size(
        win_probability=0.65,
        avg_win=0.025,
        avg_loss=0.015,
        base_amount=1000
    )
    
    # Validate results
    assert kelly_size > 0, "Kelly size should be positive"
    assert kelly_size <= 250, "Kelly size should be capped for safety"  # 25% max
    
    print(f"   ✅ Kelly position size: ${kelly_size:.2f}")
    print(f"   📈 Trade history: {len(sizer.trade_history)} trades recorded")
    return True

def test_machine_learning_generator():
    """Test machine learning signal generation"""
    print("🤖 Testing Machine Learning Signal Generator...")
    
    ml_gen = MachineLearningSignalGenerator()
    df = create_test_data(150)
    
    # Try to train the model
    forward_returns = df['close'].pct_change(5).shift(-5)
    training_success = ml_gen.train_model(df, forward_returns)
    
    # Generate signal
    ml_signal = ml_gen.generate_ml_signal(df)
    
    # Validate results
    assert 'action' in ml_signal, "Missing action in ML signal"
    assert 'confidence' in ml_signal, "Missing confidence in ML signal"
    assert 'reason' in ml_signal, "Missing reason in ML signal"
    assert ml_signal['action'] in ['BUY', 'SELL', 'HOLD'], f"Invalid action: {ml_signal['action']}"
    
    print(f"   ✅ ML Model trained: {training_success}")
    print(f"   🎯 ML Signal: {ml_signal['action']} (confidence: {ml_signal['confidence']:.2f})")
    if 'ml_metadata' in ml_signal:
        print(f"   🧠 Feature importance available: {len(ml_signal['ml_metadata']['feature_importance'])} features")
    return True

def test_var_calculator():
    """Test Value at Risk calculation"""
    print("⚠️ Testing Value at Risk Calculator...")
    
    var_calc = ValueAtRiskCalculator()
    df = create_test_data(100)
    returns = df['close'].pct_change().dropna()
    portfolio_value = 10000
    
    var_result = var_calc.calculate_var(returns, portfolio_value)
    
    # Validate results
    assert 'var_daily' in var_result, "Missing daily VaR"
    assert 'var_weekly' in var_result, "Missing weekly VaR"
    assert 'var_monthly' in var_result, "Missing monthly VaR"
    assert 'risk_assessment' in var_result, "Missing risk assessment"
    
    assert var_result['var_daily'] > 0, "Daily VaR should be positive"
    assert var_result['var_weekly'] > var_result['var_daily'], "Weekly VaR should be higher than daily"
    assert var_result['risk_assessment'] in ['LOW', 'MEDIUM', 'HIGH'], f"Invalid risk assessment: {var_result['risk_assessment']}"
    
    print(f"   ✅ Daily VaR: ${var_result['var_daily']:.2f}")
    print(f"   📊 Risk Assessment: {var_result['risk_assessment']}")
    print(f"   📈 Confidence Level: {var_result['confidence_level']*100:.0f}%")
    return True

def test_institutional_strategy_manager():
    """Test the main institutional strategy manager"""
    print("🏛️ Testing Institutional Strategy Manager...")
    
    manager = InstitutionalStrategyManager()
    df = create_test_data(200)
    portfolio_value = 15000
    base_position_size = 1000
    
    # Get comprehensive institutional signal
    institutional_signal = manager.get_institutional_signal(df, portfolio_value, base_position_size)
    
    # Validate comprehensive signal
    assert 'action' in institutional_signal, "Missing action"
    assert 'confidence' in institutional_signal, "Missing confidence"
    assert 'position_size' in institutional_signal, "Missing position size"
    assert 'institutional_analysis' in institutional_signal, "Missing institutional analysis"
    assert 'risk_score' in institutional_signal, "Missing risk score"
    
    # Validate institutional analysis components
    analysis = institutional_signal['institutional_analysis']
    assert 'market_regime' in analysis, "Missing market regime analysis"
    assert 'correlation_analysis' in analysis, "Missing correlation analysis"
    assert 'ml_signal' in analysis, "Missing ML signal"
    assert 'risk_analysis' in analysis, "Missing risk analysis"
    
    print(f"   ✅ Institutional Signal: {institutional_signal['action']}")
    print(f"   🎯 Overall Confidence: {institutional_signal['confidence']:.2f}")
    print(f"   💰 Recommended Position: ${institutional_signal['position_size']:.2f}")
    print(f"   ⚠️ Risk Score: {institutional_signal['risk_score']}")
    
    # Test trade result update
    manager.add_trade_result(0.025)  # 2.5% profit
    print(f"   📈 Trade result recorded successfully")
    
    # Test risk metrics
    risk_metrics = manager.get_risk_metrics(df, portfolio_value)
    assert 'var_analysis' in risk_metrics, "Missing VaR analysis in risk metrics"
    assert 'recommended_max_position' in risk_metrics, "Missing position recommendation"
    
    print(f"   📊 Max Recommended Position: ${risk_metrics['recommended_max_position']:.2f}")
    
    return True

def run_all_institutional_tests():
    """Run comprehensive test suite for institutional strategies"""
    print("="*80)
    print("🏛️ INSTITUTIONAL TRADING STRATEGIES - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    tests = [
        ("Market Regime Detection", test_market_regime_detector),
        ("Cross-Asset Correlation", test_cross_asset_correlation),
        ("Kelly Criterion Sizing", test_kelly_criterion_sizer),
        ("Machine Learning Signals", test_machine_learning_generator),
        ("Value at Risk Calculation", test_var_calculator),
        ("Institutional Strategy Manager", test_institutional_strategy_manager)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 Running: {test_name}")
            result = test_func()
            if result:
                passed += 1
                print(f"   ✅ PASSED: {test_name}")
            else:
                failed += 1
                print(f"   ❌ FAILED: {test_name}")
        except Exception as e:
            failed += 1
            print(f"   ❌ ERROR in {test_name}: {str(e)}")
    
    # Summary
    print("\n" + "="*80)
    print(f"📊 TEST RESULTS SUMMARY:")
    print(f"   ✅ Passed: {passed}/{len(tests)}")
    print(f"   ❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("🎉 ALL INSTITUTIONAL STRATEGY TESTS PASSED!")
        print("🏛️ Bot is ready for hedge fund-grade trading!")
    else:
        print(f"⚠️ {failed} test(s) failed. Please review the errors above.")
    
    print("="*80)
    return failed == 0

if __name__ == "__main__":
    success = run_all_institutional_tests()
    sys.exit(0 if success else 1)
