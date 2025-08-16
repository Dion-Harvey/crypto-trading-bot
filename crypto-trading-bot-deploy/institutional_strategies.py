# =============================================================================
# INSTITUTIONAL-GRADE TRADING STRATEGIES
# =============================================================================

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class MarketRegimeDetector:
    """
    Advanced market regime detection using multiple statistical methods
    Used by quantitative hedge funds for strategy switching
    """
    
    def __init__(self, lookback_period=100):
        self.lookback_period = lookback_period
        self.regimes = ['trending_up', 'trending_down', 'mean_reverting', 'volatile', 'stable']
        
    def detect_regime(self, df):
        """
        Detect current market regime using multiple indicators
        """
        try:
            if len(df) < self.lookback_period:
                result = {'regime': 'stable', 'confidence': 0.5, 'features': {}, 'recommendation': 'Wait for more data'}
                print(f"🔍 DEBUG: Early return regime result: {result}")
                return result
                
            # Calculate regime features
            features = self._calculate_regime_features(df)
            
            # Regime classification logic
            regime, confidence = self._classify_regime(features)
            
            # Get recommendation
            recommendation = self._get_regime_recommendation(regime)
            
            result = {
                'regime': regime,
                'confidence': confidence,
                'features': features,
                'recommendation': recommendation
            }
            print(f"🔍 DEBUG: Full regime result: {result}")
            return result
            
        except Exception as e:
            print(f"❌ DEBUG: Error in detect_regime: {e}")
            # Return safe fallback
            return {'regime': 'stable', 'confidence': 0.5, 'features': {}, 'recommendation': 'Error in regime detection'}
    
    def _calculate_regime_features(self, df):
        """Calculate statistical features for regime detection"""
        returns = df['close'].pct_change().dropna()
        prices = df['close']
        
        # Trend features
        ma_short = prices.rolling(10).mean()
        ma_long = prices.rolling(50).mean()
        trend_strength = (ma_short.iloc[-1] - ma_long.iloc[-1]) / ma_long.iloc[-1]
        
        # Volatility features  
        volatility = returns.rolling(20).std().iloc[-1]
        volatility_regime = volatility > returns.std() * 1.5
        
        # Mean reversion features
        bollinger_upper = prices.rolling(20).mean() + 2 * prices.rolling(20).std()
        bollinger_lower = prices.rolling(20).mean() - 2 * prices.rolling(20).std()
        bb_position = (prices.iloc[-1] - bollinger_lower.iloc[-1]) / (bollinger_upper.iloc[-1] - bollinger_lower.iloc[-1])
        
        # Momentum features
        momentum_5 = (prices.iloc[-1] - prices.iloc[-6]) / prices.iloc[-6]
        momentum_20 = (prices.iloc[-1] - prices.iloc[-21]) / prices.iloc[-21]
        
        # Market microstructure (approximated)
        price_efficiency = self._calculate_price_efficiency(returns)
        
        # Hurst exponent for mean reversion detection
        hurst_exp = self._calculate_hurst_exponent(returns.tail(50))
        
        return {
            'trend_strength': trend_strength,
            'volatility': volatility,
            'volatility_regime': volatility_regime,
            'bb_position': bb_position,
            'momentum_5': momentum_5,
            'momentum_20': momentum_20,
            'price_efficiency': price_efficiency,
            'hurst_exponent': hurst_exp,
            'volume_trend': self._calculate_volume_trend(df)
        }
    
    def _calculate_price_efficiency(self, returns):
        """Calculate price efficiency ratio"""
        if len(returns) < 10:
            return 0.5
            
        # Price efficiency = actual move / sum of absolute moves
        actual_move = abs(returns.sum())
        total_moves = returns.abs().sum()
        
        return actual_move / total_moves if total_moves > 0 else 0.5
    
    def _calculate_hurst_exponent(self, returns):
        """Calculate Hurst exponent for mean reversion detection"""
        if len(returns) < 20:
            return 0.5
            
        try:
            # Simplified Hurst calculation
            lags = range(2, min(20, len(returns)//2))
            tau = [np.sqrt(np.mean((returns[lag:] - returns[:-lag])**2)) for lag in lags]
            
            # Linear regression in log space
            m = np.polyfit(np.log(lags), np.log(tau), 1)[0]
            return max(0.1, min(0.9, m))  # Constrain between 0.1 and 0.9
        except:
            return 0.5
    
    def _calculate_volume_trend(self, df):
        """Calculate volume trend indicator"""
        if 'volume' not in df.columns:
            return 0.0
            
        volume = df['volume']
        volume_ma = volume.rolling(20).mean()
        
        return (volume.iloc[-5:].mean() - volume_ma.iloc[-1]) / volume_ma.iloc[-1]
    
    def _classify_regime(self, features):
        """Classify market regime based on features"""
        # Trending up regime
        if (features['trend_strength'] > 0.02 and 
            features['momentum_5'] > 0.01 and 
            features['momentum_20'] > 0.02):
            return 'trending_up', 0.8
            
        # Trending down regime
        elif (features['trend_strength'] < -0.02 and 
              features['momentum_5'] < -0.01 and 
              features['momentum_20'] < -0.02):
            return 'trending_down', 0.8
            
        # Mean reverting regime (Hurst < 0.5 indicates mean reversion)
        elif (features['hurst_exponent'] < 0.4 and 
              features['price_efficiency'] < 0.3):
            return 'mean_reverting', 0.7
            
        # Volatile regime
        elif features['volatility_regime'] and features['volatility'] > 0.03:
            return 'volatile', 0.75
            
        # Default to stable
        else:
            return 'stable', 0.6
    
    def _get_regime_recommendation(self, regime):
        """Get trading recommendations for each regime"""
        recommendations = {
            'trending_up': 'Use momentum/trend following strategies',
            'trending_down': 'Use short momentum or defensive strategies', 
            'mean_reverting': 'Use contrarian/mean reversion strategies',
            'volatile': 'Reduce position sizes, use wider stops',
            'stable': 'Use normal strategies with standard sizing'
        }
        return recommendations.get(regime, 'Monitor market conditions')

class CrossAssetCorrelationAnalyzer:
    """
    Cross-asset correlation analysis for crypto trading
    Incorporates traditional market signals (DXY, Gold, SPY, etc.)
    """
    
    def __init__(self):
        self.correlation_window = 30
        self.traditional_assets = ['DXY', 'GOLD', 'SPY', 'VIX']
    
    def analyze_cross_correlations(self, btc_returns):
        """
        Analyze correlations between BTC and traditional assets
        Note: In practice, you'd fetch real data for these assets
        """
        # For demo purposes, we'll simulate correlation analysis
        # In production, integrate with APIs for traditional market data
        
        correlations = self._simulate_correlations()
        
        # Calculate correlation regime
        regime = self._determine_correlation_regime(correlations)
        
        # Generate cross-asset signals
        signals = self._generate_cross_asset_signals(correlations, regime)
        
        return {
            'correlations': correlations,
            'regime': regime,
            'signals': signals,
            'risk_factors': self._assess_risk_factors(correlations)
        }
    
    def _simulate_correlations(self):
        """Simulate correlations (replace with real data in production)"""
        return {
            'DXY': np.random.uniform(-0.7, -0.3),  # BTC typically negatively correlated with USD
            'GOLD': np.random.uniform(0.2, 0.6),   # Often positively correlated
            'SPY': np.random.uniform(-0.2, 0.4),   # Variable correlation
            'VIX': np.random.uniform(-0.5, -0.1)   # Usually negatively correlated
        }
    
    def _determine_correlation_regime(self, correlations):
        """Determine current correlation regime"""
        avg_correlation = np.mean([abs(corr) for corr in correlations.values()])
        
        if avg_correlation > 0.6:
            return 'high_correlation'  # Risk-on/risk-off regime
        elif avg_correlation < 0.3:
            return 'low_correlation'   # Crypto-specific regime
        else:
            return 'moderate_correlation'
    
    def _generate_cross_asset_signals(self, correlations, regime):
        """Generate signals based on cross-asset analysis"""
        signals = []
        
        # DXY signal (strong USD typically bearish for crypto)
        if correlations['DXY'] < -0.5:
            signals.append({
                'asset': 'DXY',
                'signal': 'bearish' if correlations['DXY'] < -0.6 else 'neutral',
                'strength': abs(correlations['DXY']),
                'reasoning': 'Strong USD pressure on crypto'
            })
        
        # VIX signal (high fear can be contrarian bullish)
        if correlations['VIX'] < -0.4:
            signals.append({
                'asset': 'VIX',
                'signal': 'contrarian_bullish',
                'strength': abs(correlations['VIX']),
                'reasoning': 'High fear potentially oversold condition'
            })
        
        return signals
    
    def _assess_risk_factors(self, correlations):
        """Assess systemic risk factors"""
        risk_score = 0
        factors = []
        
        # High correlation with traditional assets increases systemic risk
        for asset, corr in correlations.items():
            if abs(corr) > 0.7:
                risk_score += 0.25
                factors.append(f'High correlation with {asset}')
        
        return {
            'risk_score': min(1.0, risk_score),
            'factors': factors,
            'recommendation': 'Reduce leverage' if risk_score > 0.5 else 'Normal risk levels'
        }

class KellyCriterionSizer:
    """
    Kelly Criterion position sizing - optimal bet sizing used by hedge funds
    """
    
    def __init__(self, lookback_trades=50):
        self.lookback_trades = lookback_trades
        self.trade_history = []
        
    def calculate_kelly_size(self, win_probability, avg_win, avg_loss, base_amount=100):
        """
        Calculate optimal position size using Kelly Criterion
        Kelly% = (bp - q) / b
        where: b = odds, p = win probability, q = loss probability
        """
        if len(self.trade_history) < 10:
            return base_amount * 0.5  # Conservative sizing with limited data
        
        # Calculate empirical parameters from trade history
        wins = [trade for trade in self.trade_history if trade > 0]
        losses = [abs(trade) for trade in self.trade_history if trade < 0]
        
        if not wins or not losses:
            return base_amount * 0.5
            
        actual_win_prob = len(wins) / len(self.trade_history)
        actual_avg_win = np.mean(wins)
        actual_avg_loss = np.mean(losses)
        
        # Kelly formula
        win_loss_ratio = actual_avg_win / actual_avg_loss if actual_avg_loss > 0 else 1
        kelly_fraction = (actual_win_prob * win_loss_ratio - (1 - actual_win_prob)) / win_loss_ratio
        
        # Apply safety constraints
        kelly_fraction = max(0, min(0.25, kelly_fraction))  # Cap at 25% of capital
        
        # Adjust for signal confidence
        confidence_adjustment = win_probability  # Use current signal confidence
        final_fraction = kelly_fraction * confidence_adjustment
        
        return base_amount * final_fraction
    
    def add_trade_result(self, pnl_percentage):
        """Add trade result to history for Kelly calculation"""
        self.trade_history.append(pnl_percentage)
        
        # Keep only recent trades
        if len(self.trade_history) > self.lookback_trades:
            self.trade_history.pop(0)

class MachineLearningSignalGenerator:
    """
    Machine Learning signal generation using ensemble methods
    Similar to what quantitative hedge funds use
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_importance = {}
        
    def extract_ml_features(self, df):
        """Extract ML features from price data"""
        if len(df) < 50:
            return None
            
        # Create a copy to avoid modifying original
        df_work = df.copy()
        
        # Technical indicators as features
        df_work['rsi'] = self._calculate_rsi(df_work['close'], 14)
        df_work['bb_position'] = self._calculate_bb_position(df_work)
        df_work['volume_ratio'] = df_work['volume'] / df_work['volume'].rolling(20).mean() if 'volume' in df_work.columns else 1
        
        # Price action features
        df_work['price_change_1'] = df_work['close'].pct_change(1)
        df_work['price_change_5'] = df_work['close'].pct_change(5)
        df_work['price_change_20'] = df_work['close'].pct_change(20)
        
        # Volatility features
        df_work['volatility'] = df_work['close'].pct_change().rolling(20).std()
        df_work['vol_ratio'] = df_work['volatility'] / df_work['volatility'].rolling(50).mean()
        
        # Momentum features
        df_work['momentum'] = df_work['close'] / df_work['close'].shift(10) - 1
        
        # MA features
        df_work['ma_ratio_fast'] = df_work['close'] / df_work['close'].rolling(7).mean()
        df_work['ma_ratio_slow'] = df_work['close'] / df_work['close'].rolling(25).mean()
        
        feature_columns = ['rsi', 'bb_position', 'volume_ratio', 'price_change_1', 
                          'price_change_5', 'volatility', 'momentum', 'ma_ratio_fast', 'ma_ratio_slow']
        
        # Get latest features - ensure we have valid data
        latest_row = df_work[feature_columns].iloc[-1]
        
        # Replace NaN with reasonable defaults
        latest_features = []
        for col in feature_columns:
            value = latest_row[col]
            if pd.isna(value):
                if col == 'rsi':
                    latest_features.append(50.0)  # Neutral RSI
                elif 'ratio' in col:
                    latest_features.append(1.0)   # Neutral ratio
                else:
                    latest_features.append(0.0)   # Neutral change
            else:
                latest_features.append(float(value))
        
        return np.array(latest_features).reshape(1, -1)
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_bb_position(self, df):
        """Calculate Bollinger Band position"""
        ma = df['close'].rolling(20).mean()
        std = df['close'].rolling(20).std()
        upper = ma + 2 * std
        lower = ma - 2 * std
        return (df['close'] - lower) / (upper - lower)
    
    def train_model(self, df, forward_returns):
        """Train the ML model on historical data"""
        if len(df) < 100:
            return False
        
        # Create a copy to avoid modifying original
        df_work = df.copy()
            
        # Create features for training
        features_list = []
        labels_list = []
        
        # Add required columns to working dataframe
        df_work['rsi'] = self._calculate_rsi(df_work['close'], 14)
        df_work['bb_position'] = self._calculate_bb_position(df_work)
        df_work['volume_ratio'] = df_work['volume'] / df_work['volume'].rolling(20).mean() if 'volume' in df_work.columns else 1
        df_work['price_change_1'] = df_work['close'].pct_change(1)
        df_work['price_change_5'] = df_work['close'].pct_change(5)
        df_work['price_change_20'] = df_work['close'].pct_change(20)
        df_work['volatility'] = df_work['close'].pct_change().rolling(20).std()
        df_work['vol_ratio'] = df_work['volatility'] / df_work['volatility'].rolling(50).mean()
        df_work['momentum'] = df_work['close'] / df_work['close'].shift(10) - 1
        df_work['ma_ratio_fast'] = df_work['close'] / df_work['close'].rolling(7).mean()
        df_work['ma_ratio_slow'] = df_work['close'] / df_work['close'].rolling(25).mean()
        
        feature_columns = ['rsi', 'bb_position', 'volume_ratio', 'price_change_1', 
                          'price_change_5', 'volatility', 'momentum', 'ma_ratio_fast', 'ma_ratio_slow']
        
        for i in range(50, len(df_work) - 5):  # Need future returns for labels
            # Extract features for this point
            feature_row = df_work[feature_columns].iloc[i]
            
            # Check if we have valid features (not all NaN)
            if not feature_row.isna().all():
                # Replace NaN with reasonable defaults
                features = []
                for col in feature_columns:
                    value = feature_row[col]
                    if pd.isna(value):
                        if col == 'rsi':
                            features.append(50.0)  # Neutral RSI
                        elif 'ratio' in col:
                            features.append(1.0)   # Neutral ratio
                        else:
                            features.append(0.0)   # Neutral change
                    else:
                        features.append(float(value))
                
                # Label: 1 if price goes up >1% in next 5 periods, 0 otherwise
                if i + 5 < len(df_work):
                    future_return = (df_work['close'].iloc[i+5] - df_work['close'].iloc[i]) / df_work['close'].iloc[i]
                    label = 1 if future_return > 0.01 else 0
                    
                    features_list.append(features)
                    labels_list.append(label)
        
        if len(features_list) < 20:
            return False
            
        X = np.array(features_list)
        y = np.array(labels_list)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Store feature importance
        feature_names = ['rsi', 'bb_position', 'volume_ratio', 'price_change_1', 
                        'price_change_5', 'volatility', 'momentum', 'ma_ratio_fast', 'ma_ratio_slow']
        self.feature_importance = dict(zip(feature_names, self.model.feature_importances_))
        
        return True
    
    def generate_ml_signal(self, df):
        """Generate ML-based trading signal"""
        if not self.is_trained:
            # Try to train on available data
            if len(df) >= 100:
                forward_returns = df['close'].pct_change(5).shift(-5)
                self.train_model(df, forward_returns)
            
            if not self.is_trained:
                return {'action': 'HOLD', 'confidence': 0.3, 'reason': 'ML model not trained'}
        
        # Extract current features
        features = self.extract_ml_features(df)
        if features is None:
            return {'action': 'HOLD', 'confidence': 0.3, 'reason': 'Insufficient data for ML features'}
        
        try:
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get prediction and probability
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0]
            
            # Ensure we have valid probabilities
            if len(probability) != 2:
                return {'action': 'HOLD', 'confidence': 0.3, 'reason': 'ML model prediction error'}
            
            # Convert to trading signal
            if prediction == 1 and probability[1] > 0.65:
                action = 'BUY'
                confidence = probability[1]
                reason = f'ML model predicts upward movement (prob: {probability[1]:.3f})'
            elif prediction == 0 and probability[0] > 0.65:
                action = 'SELL'
                confidence = probability[0]
                reason = f'ML model predicts downward movement (prob: {probability[0]:.3f})'
            else:
                action = 'HOLD'
                confidence = max(probability)
                reason = f'ML model uncertain (prob: {max(probability):.3f})'
            
            return {
                'action': action,
                'confidence': confidence,
                'reason': reason,
                'ml_metadata': {
                    'prediction': prediction,
                    'probabilities': probability.tolist(),
                    'feature_importance': self.feature_importance
                }
            }
        except Exception as e:
            return {'action': 'HOLD', 'confidence': 0.3, 'reason': f'ML prediction error: {str(e)}'}

class ValueAtRiskCalculator:
    """
    Value at Risk (VaR) calculation for risk management
    Standard risk measure used by institutional traders
    """
    
    def __init__(self, confidence_level=0.95, lookback_days=252):
        self.confidence_level = confidence_level
        self.lookback_days = lookback_days
        
    def calculate_var(self, returns, portfolio_value):
        """
        Calculate Value at Risk using historical simulation
        """
        if len(returns) < 30:
            return {
                'var_daily': portfolio_value * 0.02,  # 2% default
                'var_weekly': portfolio_value * 0.05,
                'var_monthly': portfolio_value * 0.10,
                'confidence_level': self.confidence_level
            }
        
        # Use recent returns for calculation
        recent_returns = returns.tail(min(len(returns), self.lookback_days))
        
        # Calculate VaR at different time horizons
        daily_var = self._calculate_period_var(recent_returns, portfolio_value, 1)
        weekly_var = self._calculate_period_var(recent_returns, portfolio_value, 7)
        monthly_var = self._calculate_period_var(recent_returns, portfolio_value, 30)
        
        return {
            'var_daily': daily_var,
            'var_weekly': weekly_var,
            'var_monthly': monthly_var,
            'confidence_level': self.confidence_level,
            'max_expected_loss': daily_var,
            'risk_assessment': self._assess_risk_level(daily_var, portfolio_value)
        }
    
    def _calculate_period_var(self, returns, portfolio_value, days):
        """Calculate VaR for specific time period"""
        # Scale returns for time period
        scaled_returns = returns * np.sqrt(days)
        
        # Calculate percentile
        var_percentile = (1 - self.confidence_level) * 100
        var_return = np.percentile(scaled_returns, var_percentile)
        
        # Convert to dollar amount
        var_amount = abs(var_return * portfolio_value)
        
        return var_amount
    
    def _assess_risk_level(self, daily_var, portfolio_value):
        """Assess risk level based on VaR"""
        var_percentage = daily_var / portfolio_value
        
        if var_percentage > 0.05:
            return 'HIGH'
        elif var_percentage > 0.03:
            return 'MEDIUM'
        else:
            return 'LOW'

class InstitutionalStrategyManager:
    """
    Main class coordinating all institutional strategies
    """
    
    def __init__(self):
        self.regime_detector = MarketRegimeDetector()
        self.correlation_analyzer = CrossAssetCorrelationAnalyzer()
        self.kelly_sizer = KellyCriterionSizer()
        self.ml_generator = MachineLearningSignalGenerator()
        self.var_calculator = ValueAtRiskCalculator()
        
    def get_institutional_signal(self, df, portfolio_value=1000, base_position_size=100):
        """
        Generate comprehensive institutional-grade trading signal
        """
        # 1. Market Regime Analysis
        regime_analysis = self.regime_detector.detect_regime(df)
        
        # 2. Cross-Asset Correlation Analysis
        btc_returns = df['close'].pct_change().dropna()
        correlation_analysis = self.correlation_analyzer.analyze_cross_correlations(btc_returns)
        
        # 3. Machine Learning Signal
        ml_signal = self.ml_generator.generate_ml_signal(df)
        
        # 4. Risk Assessment
        var_analysis = self.var_calculator.calculate_var(btc_returns, portfolio_value)
        
        # 5. Position Sizing
        kelly_size = self.kelly_sizer.calculate_kelly_size(
            win_probability=ml_signal['confidence'],
            avg_win=0.03,  # 3% average win
            avg_loss=0.02,  # 2% average loss
            base_amount=base_position_size
        )
        
        # 6. Combine all signals
        final_signal = self._combine_institutional_signals(
            regime_analysis, correlation_analysis, ml_signal, var_analysis, kelly_size
        )
        
        return final_signal
    
    def _combine_institutional_signals(self, regime, correlation, ml_signal, var_analysis, kelly_size):
        """
        Intelligently combine all institutional signals
        """
        # Start with ML signal as base
        action = ml_signal['action']
        confidence = ml_signal['confidence']
        reasons = [ml_signal['reason']]
        
        # Adjust based on market regime
        if regime['regime'] == 'trending_up' and action == 'SELL':
            confidence *= 0.7  # Reduce confidence for contrarian trades in uptrend
            reasons.append(f"Reduced confidence due to {regime['regime']} regime")
        elif regime['regime'] == 'trending_down' and action == 'BUY':
            confidence *= 0.7
            reasons.append(f"Reduced confidence due to {regime['regime']} regime")
        elif regime['regime'] == 'mean_reverting' and action in ['BUY', 'SELL']:
            confidence *= 1.1  # Boost contrarian signals in mean-reverting regime
            reasons.append(f"Boosted confidence for mean reversion in {regime['regime']} regime")
        
        # Adjust based on correlation analysis
        if correlation['regime'] == 'high_correlation':
            confidence *= 0.9  # Slightly reduce confidence in high correlation regime
            reasons.append("Adjusted for high cross-asset correlation regime")
        
        # Risk management override
        if var_analysis['risk_assessment'] == 'HIGH':
            if action in ['BUY', 'SELL']:
                confidence *= 0.6  # Significantly reduce position in high risk environment
                kelly_size *= 0.5
                reasons.append("Position reduced due to high VaR")
        
        # Final position sizing
        final_position_size = kelly_size
        
        return {
            'action': action,
            'confidence': min(0.95, confidence),  # Cap confidence at 95%
            'position_size': final_position_size,
            'reason': ' | '.join(reasons),
            'institutional_analysis': {
                'market_regime': regime,
                'correlation_analysis': correlation,
                'ml_signal': ml_signal,
                'risk_analysis': var_analysis,
                'kelly_position_size': kelly_size
            },
            'risk_score': var_analysis['risk_assessment'],
            'regime_confidence': regime['confidence']
        }
    
    def add_trade_result(self, pnl_percentage):
        """Update Kelly Criterion with trade result"""
        self.kelly_sizer.add_trade_result(pnl_percentage)
    
    def get_risk_metrics(self, df, portfolio_value):
        """Get comprehensive risk metrics"""
        returns = df['close'].pct_change().dropna()
        var_analysis = self.var_calculator.calculate_var(returns, portfolio_value)
        regime_analysis = self.regime_detector.detect_regime(df)
        
        return {
            'var_analysis': var_analysis,
            'regime_risk': regime_analysis,
            'recommended_max_position': portfolio_value * 0.1 if var_analysis['risk_assessment'] == 'HIGH' else portfolio_value * 0.2
        }
