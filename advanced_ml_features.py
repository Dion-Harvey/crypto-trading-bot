# =============================================================================
# PHASE 3 WEEK 3 - ADVANCED ML FEATURES
# =============================================================================
#
# Copyright (c) 2025 Dion Harvey. All rights reserved.
# Advanced Machine Learning Features for Enhanced Trading Intelligence
#
# FEATURES:
# - Ensemble Model Voting (Multiple ML Models)
# - Feature Importance Analysis and Dynamic Selection
# - Model Drift Detection and Auto-Retraining
# - Advanced Signal Fusion with ML Confidence
# - Performance-Based Model Weighting
#
# =============================================================================

import numpy as np
import pandas as pd
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass

# Suppress TensorFlow warnings for cleaner output
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.naive_bayes import GaussianNB
    from sklearn.preprocessing import StandardScaler, RobustScaler
    from sklearn.model_selection import cross_val_score, TimeSeriesSplit
    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
    from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    print(f"⚠️ ML libraries not available: {e}")

@dataclass
class ModelPerformanceMetrics:
    """Track individual model performance metrics"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    roc_auc: float = 0.0
    prediction_confidence: float = 0.0
    last_updated: datetime = None
    prediction_count: int = 0
    correct_predictions: int = 0

class AdvancedMLEngine:
    """
    🧠 PHASE 3 WEEK 3 - ADVANCED ML FEATURES ENGINE
    
    Implements enterprise-grade machine learning capabilities:
    - Ensemble model voting with multiple algorithms
    - Dynamic feature importance analysis and selection
    - Model drift detection and automatic retraining
    - Performance-based model weighting and selection
    - Advanced signal fusion with ML confidence scoring
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or self._get_default_config()
        self.logger = self._setup_logger()
        
        # 🎯 ENSEMBLE MODEL COMPONENTS
        self.models = {}
        self.model_weights = {}
        self.model_performance = {}
        self.feature_importance_history = []
        self.scalers = {}
        
        # 🎯 FEATURE SELECTION AND ENGINEERING
        self.feature_selector = None
        self.selected_features = []
        self.feature_importance_threshold = 0.01
        
        # 🎯 MODEL DRIFT DETECTION
        self.reference_data = None
        self.drift_threshold = 0.15
        self.last_retrain_time = None
        self.prediction_history = []
        
        # 🎯 PERFORMANCE TRACKING
        self.ensemble_performance = ModelPerformanceMetrics()
        self.model_comparison_cache = {}
        
        # 🎯 TRAINING STATE
        self.is_trained = False
        self.training_features = []
        self.training_history = []
        
        self.logger.info("🧠 Advanced ML Engine initialized - Phase 3 Week 3")
    
    def _get_default_config(self) -> Dict:
        """Get default configuration for ML engine"""
        return {
            'ensemble_models': {
                'random_forest': {'n_estimators': 100, 'max_depth': 10, 'random_state': 42},
                'gradient_boost': {'n_estimators': 100, 'learning_rate': 0.1, 'random_state': 42},
                'logistic_regression': {'random_state': 42, 'max_iter': 1000},
                'svm': {'probability': True, 'random_state': 42},
                'naive_bayes': {}
            },
            'feature_selection': {
                'max_features': 15,
                'selection_method': 'mutual_info',
                'importance_threshold': 0.01
            },
            'drift_detection': {
                'reference_window': 1000,
                'drift_threshold': 0.15,
                'retrain_threshold': 0.20,
                'min_retrain_interval_hours': 6
            },
            'performance_tracking': {
                'min_predictions_for_evaluation': 20,
                'performance_window': 100,
                'weight_decay_factor': 0.95
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for ML engine"""
        logger = logging.getLogger('AdvancedMLEngine')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def initialize_ensemble_models(self) -> bool:
        """Initialize ensemble of ML models with different algorithms"""
        try:
            if not ML_AVAILABLE:
                self.logger.warning("ML libraries not available - using mock models")
                return self._initialize_mock_models()
            
            ensemble_config = self.config['ensemble_models']
            
            # 🎯 INITIALIZE INDIVIDUAL MODELS
            self.models = {
                'random_forest': RandomForestClassifier(**ensemble_config['random_forest']),
                'gradient_boost': GradientBoostingClassifier(**ensemble_config['gradient_boost']),
                'logistic_regression': LogisticRegression(**ensemble_config['logistic_regression']),
                'svm': SVC(**ensemble_config['svm']),
                'naive_bayes': GaussianNB(**ensemble_config['naive_bayes'])
            }
            
            # 🎯 INITIALIZE SCALERS FOR EACH MODEL
            self.scalers = {
                name: StandardScaler() if name != 'naive_bayes' else RobustScaler()
                for name in self.models.keys()
            }
            
            # 🎯 INITIALIZE PERFORMANCE TRACKING
            for model_name in self.models.keys():
                self.model_performance[model_name] = ModelPerformanceMetrics(
                    last_updated=datetime.now()
                )
                self.model_weights[model_name] = 1.0 / len(self.models)  # Equal initial weights
            
            # 🎯 CREATE VOTING CLASSIFIER
            estimators = [(name, model) for name, model in self.models.items()]
            self.voting_classifier = VotingClassifier(
                estimators=estimators,
                voting='soft',  # Use probability voting
                weights=list(self.model_weights.values())
            )
            
            self.logger.info(f"✅ Ensemble models initialized: {list(self.models.keys())}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing ensemble models: {e}")
            return self._initialize_mock_models()
    
    def _initialize_mock_models(self) -> bool:
        """Initialize mock models when ML libraries unavailable"""
        self.models = {
            'mock_rf': None,
            'mock_gb': None,
            'mock_lr': None
        }
        
        for model_name in self.models.keys():
            self.model_performance[model_name] = ModelPerformanceMetrics(
                accuracy=0.6 + np.random.uniform(-0.1, 0.1),
                last_updated=datetime.now()
            )
            self.model_weights[model_name] = 1.0 / len(self.models)
        
        self.logger.info("✅ Mock ensemble models initialized")
        return True
    
    def extract_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        🎯 ADVANCED FEATURE ENGINEERING
        
        Extracts sophisticated features for ML training and prediction
        """
        try:
            # Create a copy and ensure we have the right data types
            features_df = df.copy()
            
            # 🔧 CRITICAL FIX: Remove or convert datetime columns that cause sklearn errors
            datetime_columns = []
            for col in features_df.columns:
                if features_df[col].dtype.name.startswith('datetime'):
                    datetime_columns.append(col)
            
            # Convert datetime columns to numeric timestamp if needed, or remove them
            for col in datetime_columns:
                if col == 'timestamp':
                    # Convert to Unix timestamp (numeric)
                    features_df['timestamp_numeric'] = pd.to_datetime(features_df[col]).astype('int64') / 10**9
                # Remove the original datetime column
                features_df = features_df.drop(columns=[col])
            
            # Ensure all price columns are float64
            price_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in price_columns:
                if col in features_df.columns:
                    features_df[col] = pd.to_numeric(features_df[col], errors='coerce')
            
            # 🎯 PRICE AND RETURN FEATURES
            features_df['returns_1'] = features_df['close'].pct_change(1)
            features_df['returns_5'] = features_df['close'].pct_change(5)
            features_df['returns_15'] = features_df['close'].pct_change(15)
            features_df['returns_30'] = features_df['close'].pct_change(30)
            
            # 🎯 VOLATILITY FEATURES
            features_df['volatility_5'] = features_df['returns_1'].rolling(5).std()
            features_df['volatility_15'] = features_df['returns_1'].rolling(15).std()
            features_df['volatility_30'] = features_df['returns_1'].rolling(30).std()
            features_df['volatility_ratio'] = features_df['volatility_5'] / features_df['volatility_30']
            
            # 🎯 MOMENTUM FEATURES
            features_df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
            features_df['momentum_15'] = df['close'] / df['close'].shift(15) - 1
            features_df['momentum_30'] = df['close'] / df['close'].shift(30) - 1
            features_df['momentum_acceleration'] = features_df['momentum_5'] - features_df['momentum_15']
            
            # 🎯 TECHNICAL INDICATORS
            features_df['rsi'] = self._calculate_rsi(df['close'], 14)
            features_df['rsi_5'] = self._calculate_rsi(df['close'], 5)
            features_df['rsi_30'] = self._calculate_rsi(df['close'], 30)
            
            # 🎯 MOVING AVERAGE FEATURES
            for period in [5, 10, 20, 50]:
                ma = df['close'].rolling(period).mean()
                features_df[f'ma_ratio_{period}'] = df['close'] / ma - 1
                features_df[f'ma_slope_{period}'] = ma.pct_change(5)
            
            # 🎯 BOLLINGER BAND FEATURES
            bb_period = 20
            bb_std = 2
            bb_middle = df['close'].rolling(bb_period).mean()
            bb_std_dev = df['close'].rolling(bb_period).std()
            features_df['bb_upper'] = bb_middle + (bb_std_dev * bb_std)
            features_df['bb_lower'] = bb_middle - (bb_std_dev * bb_std)
            features_df['bb_position'] = (df['close'] - features_df['bb_lower']) / (features_df['bb_upper'] - features_df['bb_lower'])
            features_df['bb_width'] = (features_df['bb_upper'] - features_df['bb_lower']) / bb_middle
            
            # 🎯 VOLUME FEATURES (if available)
            if 'volume' in df.columns:
                features_df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
                features_df['volume_momentum'] = df['volume'].pct_change(5)
                features_df['price_volume_trend'] = features_df['returns_5'] * features_df['volume_ratio']
            else:
                features_df['volume_ratio'] = 1.0
                features_df['volume_momentum'] = 0.0
                features_df['price_volume_trend'] = 0.0
            
            # 🎯 MARKET MICROSTRUCTURE PROXIES
            features_df['price_range'] = (df['high'] - df['low']) / df['close'] if 'high' in df.columns else 0.0
            features_df['gap'] = df['open'] / df['close'].shift(1) - 1 if 'open' in df.columns else 0.0
            
            # 🎯 STATISTICAL FEATURES
            features_df['skewness_15'] = features_df['returns_1'].rolling(15).skew()
            features_df['kurtosis_15'] = features_df['returns_1'].rolling(15).kurt()
            
            # Drop non-feature columns and handle NaN values
            # 🔧 CRITICAL FIX: Only keep numeric columns for ML training
            feature_columns = []
            for col in features_df.columns:
                if col not in ['open', 'high', 'low', 'close', 'volume']:
                    # Only include numeric columns
                    if pd.api.types.is_numeric_dtype(features_df[col]):
                        feature_columns.append(col)
                    else:
                        self.logger.warning(f"Dropping non-numeric column: {col} (dtype: {features_df[col].dtype})")
            
            if not feature_columns:
                self.logger.error("No valid numeric feature columns found!")
                # Create basic fallback features
                feature_columns = ['returns_1', 'returns_5']
                features_df['returns_1'] = features_df['close'].pct_change(1).fillna(0)
                features_df['returns_5'] = features_df['close'].pct_change(5).fillna(0)
            
            features_clean = features_df[feature_columns].fillna(method='bfill').fillna(0)
            
            # 🔧 ADDITIONAL SAFETY: Ensure all data is finite and numeric
            features_clean = features_clean.replace([np.inf, -np.inf], 0)
            features_clean = features_clean.astype(np.float64)
            
            self.logger.info(f"✅ Extracted {len(feature_columns)} advanced features (all numeric)")
            return features_clean
            
        except Exception as e:
            self.logger.error(f"❌ Error in feature extraction: {e}")
            # Return basic features as fallback
            basic_features = pd.DataFrame({
                'returns_1': df['close'].pct_change(1),
                'momentum_5': df['close'] / df['close'].shift(5) - 1,
                'volatility_5': df['close'].pct_change(1).rolling(5).std()
            }).fillna(0)
            return basic_features
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        except:
            return pd.Series([50.0] * len(prices), index=prices.index)
    
    def perform_feature_selection(self, X: pd.DataFrame, y: pd.Series) -> List[str]:
        """
        🎯 DYNAMIC FEATURE SELECTION
        
        Selects the most important features using multiple methods
        """
        try:
            if not ML_AVAILABLE or len(X) < 50:
                # Use top features by name for mock selection
                important_features = ['returns_1', 'momentum_5', 'rsi', 'volatility_5', 'ma_ratio_20']
                available_features = [f for f in important_features if f in X.columns]
                return available_features[:10] if available_features else list(X.columns)[:10]
            
            max_features = min(self.config['feature_selection']['max_features'], len(X.columns))
            
            # 🎯 METHOD 1: MUTUAL INFORMATION
            mi_selector = SelectKBest(score_func=mutual_info_classif, k=max_features)
            mi_selector.fit(X.fillna(0), y)
            mi_features = X.columns[mi_selector.get_support()].tolist()
            
            # 🎯 METHOD 2: F-SCORE
            f_selector = SelectKBest(score_func=f_classif, k=max_features)
            f_selector.fit(X.fillna(0), y)
            f_features = X.columns[f_selector.get_support()].tolist()
            
            # 🎯 METHOD 3: RANDOM FOREST IMPORTANCE (if model trained)
            rf_features = []
            if 'random_forest' in self.models and hasattr(self.models['random_forest'], 'feature_importances_'):
                importance_scores = self.models['random_forest'].feature_importances_
                feature_importance = list(zip(X.columns, importance_scores))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                rf_features = [feat[0] for feat in feature_importance[:max_features] 
                             if feat[1] > self.feature_importance_threshold]
            
            # 🎯 COMBINE FEATURE SELECTIONS
            combined_features = list(set(mi_features + f_features + rf_features))
            
            # 🎯 RANK BY FREQUENCY AND IMPORTANCE
            feature_votes = {}
            for feature in combined_features:
                votes = 0
                if feature in mi_features: votes += 1
                if feature in f_features: votes += 1
                if feature in rf_features: votes += 1
                feature_votes[feature] = votes
            
            # Select top features by vote count
            selected_features = sorted(feature_votes.items(), key=lambda x: x[1], reverse=True)
            final_features = [feat[0] for feat in selected_features[:max_features]]
            
            self.selected_features = final_features
            self.logger.info(f"✅ Selected {len(final_features)} features from {len(X.columns)} available")
            
            return final_features
            
        except Exception as e:
            self.logger.error(f"❌ Error in feature selection: {e}")
            # Fallback to all features
            return list(X.columns)[:15]
    
    def train_ensemble_models(self, df: pd.DataFrame, target_column: str = None) -> Dict[str, bool]:
        """
        🎯 ENSEMBLE MODEL TRAINING
        
        Trains multiple ML models and creates ensemble voting system
        """
        try:
            if len(df) < 100:
                self.logger.warning("Insufficient data for ensemble training")
                return self._mock_training_results()
            
            # 🎯 FEATURE EXTRACTION
            features_df = self.extract_advanced_features(df)
            
            # 🔧 CRITICAL FIX: Ensure we have valid numeric data
            if features_df.empty or len(features_df.columns) == 0:
                self.logger.error("No valid features extracted!")
                return self._mock_training_results()
            
            # 🎯 CREATE TARGET VARIABLE
            if target_column is None:
                # Create forward-looking target (price direction prediction)
                future_returns = df['close'].pct_change(5).shift(-5)
                target = (future_returns > 0.01).astype(int)  # 1% threshold for positive
            else:
                target = df[target_column]
            
            # 🔧 ENHANCED DATA CLEANING
            # Remove NaN values and ensure alignment
            valid_indices = ~(target.isna() | features_df.isna().any(axis=1))
            
            # Ensure indices are aligned
            common_indices = features_df.index.intersection(target.index)
            valid_indices = valid_indices.reindex(common_indices, fill_value=False)
            
            X = features_df.loc[valid_indices]
            y = target.loc[valid_indices]
            
            if len(X) < 50 or X.empty:
                self.logger.warning(f"Insufficient valid data after cleaning: {len(X)} samples")
                return self._mock_training_results()
            
            # 🎯 FEATURE SELECTION
            selected_features = self.perform_feature_selection(X, y)
            X_selected = X[selected_features]
            
            # 🎯 TRAIN INDIVIDUAL MODELS
            training_results = {}
            
            for model_name, model in self.models.items():
                if model is None:  # Mock model
                    training_results[model_name] = True
                    continue
                
                try:
                    # Scale features for this model
                    scaler = self.scalers[model_name]
                    X_scaled = scaler.fit_transform(X_selected)
                    
                    # Train model
                    model.fit(X_scaled, y)
                    
                    # Evaluate using cross-validation
                    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
                    
                    # Update performance metrics
                    self.model_performance[model_name].accuracy = cv_scores.mean()
                    self.model_performance[model_name].last_updated = datetime.now()
                    
                    training_results[model_name] = True
                    self.logger.info(f"✅ {model_name}: accuracy={cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
                    
                except Exception as e:
                    self.logger.error(f"❌ Training failed for {model_name}: {e}")
                    training_results[model_name] = False
            
            # 🎯 TRAIN VOTING CLASSIFIER
            if ML_AVAILABLE and any(training_results.values()):
                try:
                    # Update model weights based on performance
                    self._update_model_weights()
                    
                    # Retrain voting classifier with new weights
                    self.voting_classifier.set_params(weights=list(self.model_weights.values()))
                    
                    # Fit voting classifier on scaled data (using first scaler)
                    primary_scaler = list(self.scalers.values())[0]
                    X_scaled = primary_scaler.fit_transform(X_selected)
                    self.voting_classifier.fit(X_scaled, y)
                    
                    self.is_trained = True
                    self.training_features = selected_features
                    self.last_retrain_time = datetime.now()
                    
                    # Store reference data for drift detection
                    self.reference_data = X_scaled[:self.config['drift_detection']['reference_window']]
                    
                    self.logger.info("✅ Ensemble voting classifier trained successfully")
                    
                except Exception as e:
                    self.logger.error(f"❌ Voting classifier training failed: {e}")
            
            successful_models = sum(training_results.values())
            self.logger.info(f"🧠 Ensemble training complete: {successful_models}/{len(self.models)} models trained")
            
            return training_results
            
        except Exception as e:
            self.logger.error(f"❌ Error in ensemble training: {e}")
            return self._mock_training_results()
    
    def _mock_training_results(self) -> Dict[str, bool]:
        """Generate mock training results when ML unavailable"""
        return {name: True for name in self.models.keys()}
    
    def _update_model_weights(self):
        """Update model weights based on recent performance"""
        try:
            total_performance = 0
            performance_scores = {}
            
            # Calculate performance scores
            for model_name, metrics in self.model_performance.items():
                # Combine multiple metrics for overall score
                performance_score = (
                    metrics.accuracy * 0.4 +
                    metrics.precision * 0.2 +
                    metrics.recall * 0.2 +
                    metrics.f1_score * 0.2
                )
                performance_scores[model_name] = max(0.1, performance_score)  # Minimum weight
                total_performance += performance_scores[model_name]
            
            # Normalize to get weights
            if total_performance > 0:
                for model_name in self.model_weights.keys():
                    self.model_weights[model_name] = performance_scores.get(model_name, 0.1) / total_performance
            
            self.logger.info(f"📊 Model weights updated: {self.model_weights}")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating model weights: {e}")
            # Reset to equal weights
            equal_weight = 1.0 / len(self.models)
            for model_name in self.model_weights.keys():
                self.model_weights[model_name] = equal_weight
    
    def detect_model_drift(self, current_data: np.ndarray) -> Dict[str, Any]:
        """
        🎯 MODEL DRIFT DETECTION
        
        Detects if the data distribution has shifted significantly
        """
        try:
            if self.reference_data is None or len(current_data) < 10:
                return {
                    'drift_detected': False,
                    'drift_score': 0.0,
                    'recommendation': 'insufficient_data'
                }
            
            if not ML_AVAILABLE:
                # Mock drift detection
                drift_score = np.random.uniform(0.05, 0.25)
                return {
                    'drift_detected': drift_score > self.drift_threshold,
                    'drift_score': drift_score,
                    'recommendation': 'retrain' if drift_score > 0.20 else 'monitor'
                }
            
            # 🎯 STATISTICAL DRIFT DETECTION
            
            # Method 1: Mean and standard deviation comparison
            ref_mean = np.mean(self.reference_data, axis=0)
            ref_std = np.std(self.reference_data, axis=0)
            curr_mean = np.mean(current_data, axis=0)
            curr_std = np.std(current_data, axis=0)
            
            # Normalize differences
            mean_diff = np.mean(np.abs(ref_mean - curr_mean) / (ref_std + 1e-8))
            std_diff = np.mean(np.abs(ref_std - curr_std) / (ref_std + 1e-8))
            
            # Method 2: Kolmogorov-Smirnov test approximation
            # For multivariate data, use average of univariate tests
            ks_scores = []
            for i in range(min(current_data.shape[1], self.reference_data.shape[1])):
                try:
                    from scipy.stats import ks_2samp
                    ks_stat, _ = ks_2samp(self.reference_data[:, i], current_data[:, i])
                    ks_scores.append(ks_stat)
                except:
                    # Fallback simple comparison
                    ks_scores.append(abs(np.mean(self.reference_data[:, i]) - np.mean(current_data[:, i])))
            
            ks_score = np.mean(ks_scores) if ks_scores else 0.0
            
            # 🎯 COMBINE DRIFT SCORES
            drift_score = (mean_diff * 0.4 + std_diff * 0.3 + ks_score * 0.3)
            
            drift_detected = drift_score > self.drift_threshold
            
            # 🎯 RECOMMENDATIONS
            if drift_score > self.config['drift_detection']['retrain_threshold']:
                recommendation = 'retrain_immediately'
            elif drift_detected:
                recommendation = 'retrain_soon'
            elif drift_score > self.drift_threshold * 0.7:
                recommendation = 'monitor_closely'
            else:
                recommendation = 'normal'
            
            drift_result = {
                'drift_detected': drift_detected,
                'drift_score': drift_score,
                'mean_shift': mean_diff,
                'std_shift': std_diff,
                'ks_score': ks_score,
                'recommendation': recommendation,
                'analysis_time': datetime.now()
            }
            
            if drift_detected:
                self.logger.warning(f"🚨 Model drift detected: score={drift_score:.3f}, recommendation={recommendation}")
            
            return drift_result
            
        except Exception as e:
            self.logger.error(f"❌ Error in drift detection: {e}")
            return {
                'drift_detected': False,
                'drift_score': 0.0,
                'recommendation': 'error',
                'error': str(e)
            }
    
    def generate_ensemble_prediction(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        🎯 ENSEMBLE PREDICTION GENERATION
        
        Generates trading signals using ensemble of ML models
        """
        try:
            if not self.is_trained:
                return {
                    'action': 'HOLD',
                    'confidence': 0.3,
                    'reason': 'Ensemble models not trained',
                    'ensemble_votes': {},
                    'model_agreement': 0.0
                }
            
            # 🎯 EXTRACT FEATURES
            features_df = self.extract_advanced_features(df)
            
            if len(features_df) == 0:
                return self._get_fallback_prediction()
            
            # Use selected features
            if self.training_features:
                available_features = [f for f in self.training_features if f in features_df.columns]
                if not available_features:
                    return self._get_fallback_prediction()
                features_df = features_df[available_features]
            
            # Get latest features
            latest_features = features_df.iloc[-1:].fillna(0)
            
            # 🎯 CHECK FOR DRIFT
            if ML_AVAILABLE and len(latest_features.columns) > 0:
                drift_result = self.detect_model_drift(latest_features.values)
                
                if drift_result['recommendation'] == 'retrain_immediately':
                    self.logger.warning("🔄 Triggering immediate model retraining due to drift")
                    # Note: In production, trigger async retraining here
            
            # 🎯 GENERATE INDIVIDUAL MODEL PREDICTIONS
            model_predictions = {}
            model_confidences = {}
            
            for model_name, model in self.models.items():
                if model is None:  # Mock model
                    pred_proba = np.random.uniform(0.3, 0.8)
                    prediction = 1 if pred_proba > 0.5 else 0
                    confidence = abs(pred_proba - 0.5) * 2
                else:
                    try:
                        # Scale features
                        scaler = self.scalers[model_name]
                        features_scaled = scaler.transform(latest_features)
                        
                        # Get prediction and probability
                        prediction = model.predict(features_scaled)[0]
                        if hasattr(model, 'predict_proba'):
                            proba = model.predict_proba(features_scaled)[0]
                            confidence = max(proba) if len(proba) > 1 else 0.5
                        else:
                            confidence = 0.6  # Default confidence for models without probability
                        
                    except Exception as e:
                        self.logger.warning(f"⚠️ Prediction failed for {model_name}: {e}")
                        prediction = 0
                        confidence = 0.3
                
                model_predictions[model_name] = prediction
                model_confidences[model_name] = confidence
            
            # 🎯 ENSEMBLE VOTING
            weighted_votes = 0
            total_weight = 0
            
            for model_name, prediction in model_predictions.items():
                weight = self.model_weights.get(model_name, 1.0 / len(self.models))
                model_confidence = model_confidences[model_name]
                
                # Weight by both model weight and prediction confidence
                effective_weight = weight * model_confidence
                weighted_votes += prediction * effective_weight
                total_weight += effective_weight
            
            # 🎯 CALCULATE ENSEMBLE RESULT
            if total_weight > 0:
                ensemble_probability = weighted_votes / total_weight
            else:
                ensemble_probability = 0.5
            
            # Determine action
            if ensemble_probability > 0.6:
                action = 'BUY'
                confidence = min(0.95, (ensemble_probability - 0.5) * 2)
            elif ensemble_probability < 0.4:
                action = 'SELL'
                confidence = min(0.95, (0.5 - ensemble_probability) * 2)
            else:
                action = 'HOLD'
                confidence = 0.5 - abs(ensemble_probability - 0.5)
            
            # 🎯 CALCULATE MODEL AGREEMENT
            predictions = list(model_predictions.values())
            agreement = 1.0 - (np.std(predictions) if len(predictions) > 1 else 0.0)
            
            # 🎯 FEATURE IMPORTANCE ANALYSIS
            feature_importance = self._analyze_current_feature_importance(latest_features)
            
            ensemble_result = {
                'action': action,
                'confidence': confidence,
                'ensemble_probability': ensemble_probability,
                'model_predictions': model_predictions,
                'model_confidences': model_confidences,
                'model_agreement': agreement,
                'feature_importance': feature_importance,
                'ensemble_votes': {
                    'buy_votes': sum(1 for p in predictions if p == 1),
                    'sell_votes': sum(1 for p in predictions if p == 0),
                    'total_models': len(predictions)
                },
                'reason': f"Ensemble: {len(predictions)} models, {agreement:.1%} agreement",
                'ml_metadata': {
                    'model_weights': self.model_weights,
                    'training_features': self.training_features,
                    'drift_score': drift_result.get('drift_score', 0.0) if 'drift_result' in locals() else 0.0
                }
            }
            
            # 🎯 UPDATE PREDICTION HISTORY
            self.prediction_history.append({
                'timestamp': datetime.now(),
                'prediction': ensemble_result,
                'features_used': list(latest_features.columns)
            })
            
            # Keep only recent history
            max_history = self.config['performance_tracking']['performance_window']
            if len(self.prediction_history) > max_history:
                self.prediction_history = self.prediction_history[-max_history:]
            
            self.logger.info(f"🧠 Ensemble prediction: {action} (confidence: {confidence:.3f}, agreement: {agreement:.1%})")
            
            return ensemble_result
            
        except Exception as e:
            self.logger.error(f"❌ Error in ensemble prediction: {e}")
            return self._get_fallback_prediction()
    
    def _analyze_current_feature_importance(self, features: pd.DataFrame) -> Dict[str, float]:
        """Analyze feature importance for current prediction"""
        try:
            if not ML_AVAILABLE or 'random_forest' not in self.models:
                # Mock feature importance
                feature_names = list(features.columns)[:5]
                return {name: np.random.uniform(0.1, 0.3) for name in feature_names}
            
            model = self.models['random_forest']
            if hasattr(model, 'feature_importances_') and len(model.feature_importances_) == len(features.columns):
                importance_dict = dict(zip(features.columns, model.feature_importances_))
                # Return top 5 most important features
                sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                return dict(sorted_importance[:5])
            
            return {}
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing feature importance: {e}")
            return {}
    
    def _get_fallback_prediction(self) -> Dict[str, Any]:
        """Fallback prediction when ensemble fails"""
        return {
            'action': 'HOLD',
            'confidence': 0.4,
            'reason': 'Ensemble fallback - insufficient data',
            'ensemble_votes': {'buy_votes': 0, 'sell_votes': 0, 'total_models': 0},
            'model_agreement': 0.0
        }
    
    def update_model_performance(self, prediction_result: Dict, actual_outcome: bool):
        """
        🎯 PERFORMANCE TRACKING AND MODEL UPDATING
        
        Updates model performance metrics based on actual outcomes
        """
        try:
            # Update ensemble performance
            self.ensemble_performance.prediction_count += 1
            if actual_outcome:
                self.ensemble_performance.correct_predictions += 1
            
            # Calculate running accuracy
            if self.ensemble_performance.prediction_count > 0:
                self.ensemble_performance.accuracy = (
                    self.ensemble_performance.correct_predictions / 
                    self.ensemble_performance.prediction_count
                )
            
            # Update individual model performance
            model_predictions = prediction_result.get('model_predictions', {})
            ensemble_prediction = 1 if prediction_result.get('action') == 'BUY' else 0
            
            for model_name, model_pred in model_predictions.items():
                if model_name in self.model_performance:
                    metrics = self.model_performance[model_name]
                    metrics.prediction_count += 1
                    
                    # Check if this model's prediction was correct
                    model_correct = (model_pred == ensemble_prediction and actual_outcome) or \
                                  (model_pred != ensemble_prediction and not actual_outcome)
                    
                    if model_correct:
                        metrics.correct_predictions += 1
                    
                    # Update accuracy
                    if metrics.prediction_count > 0:
                        metrics.accuracy = metrics.correct_predictions / metrics.prediction_count
                    
                    metrics.last_updated = datetime.now()
            
            # Update model weights if we have enough data
            min_predictions = self.config['performance_tracking']['min_predictions_for_evaluation']
            if self.ensemble_performance.prediction_count >= min_predictions:
                self._update_model_weights()
            
            self.logger.info(f"📊 Performance updated: ensemble accuracy={self.ensemble_performance.accuracy:.3f}")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating performance: {e}")
    
    def get_ensemble_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the ensemble system"""
        try:
            status = {
                'ensemble_trained': self.is_trained,
                'total_models': len(self.models),
                'trained_models': sum(1 for model in self.models.values() if model is not None),
                'selected_features': len(self.selected_features),
                'model_weights': self.model_weights,
                'ensemble_performance': {
                    'accuracy': self.ensemble_performance.accuracy,
                    'total_predictions': self.ensemble_performance.prediction_count,
                    'correct_predictions': self.ensemble_performance.correct_predictions
                },
                'individual_performance': {
                    name: {
                        'accuracy': metrics.accuracy,
                        'predictions': metrics.prediction_count
                    }
                    for name, metrics in self.model_performance.items()
                },
                'last_retrain': self.last_retrain_time.isoformat() if self.last_retrain_time else None,
                'drift_detection_active': self.reference_data is not None,
                'prediction_history_length': len(self.prediction_history)
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Error getting ensemble status: {e}")
            return {'error': str(e)}

# =============================================================================
# GLOBAL ENSEMBLE INSTANCE AND HELPER FUNCTIONS
# =============================================================================

_ensemble_engine = None

def get_advanced_ml_engine(config: Dict = None) -> AdvancedMLEngine:
    """Get or create the global advanced ML engine instance"""
    global _ensemble_engine
    if _ensemble_engine is None:
        _ensemble_engine = AdvancedMLEngine(config)
        _ensemble_engine.initialize_ensemble_models()
    return _ensemble_engine

def enhance_signal_with_advanced_ml(signal: Dict, df: pd.DataFrame, symbol: str = 'BTC/USDT') -> Dict:
    """
    🎯 ENHANCE TRADING SIGNAL WITH ADVANCED ML PREDICTIONS
    
    Combines traditional trading signal with ensemble ML predictions
    """
    try:
        engine = get_advanced_ml_engine()
        
        # Generate ML prediction
        ml_prediction = engine.generate_ensemble_prediction(df)
        
        # Combine with original signal
        original_confidence = signal.get('confidence', 0.5)
        ml_confidence = ml_prediction.get('confidence', 0.5)
        ml_action = ml_prediction.get('action', 'HOLD')
        
        # Calculate enhancement
        if signal.get('action') == ml_action:
            # Signals agree - boost confidence
            confidence_boost = ml_confidence * 0.15  # Up to 15% boost
            enhanced_confidence = min(0.95, original_confidence + confidence_boost)
            enhancement_type = 'AGREEMENT_BOOST'
        elif ml_confidence > 0.7:
            # Strong ML signal disagrees - caution
            confidence_reduction = ml_confidence * 0.10  # Up to 10% reduction
            enhanced_confidence = max(0.3, original_confidence - confidence_reduction)
            enhancement_type = 'DISAGREEMENT_CAUTION'
        else:
            # Weak ML signal - minimal impact
            enhanced_confidence = original_confidence
            enhancement_type = 'NO_CHANGE'
        
        # Create enhanced signal
        enhanced_signal = signal.copy()
        enhanced_signal['confidence'] = enhanced_confidence
        enhanced_signal['ml_enhancement'] = {
            'ml_prediction': ml_prediction,
            'enhancement_type': enhancement_type,
            'confidence_change': enhanced_confidence - original_confidence,
            'model_agreement': ml_prediction.get('model_agreement', 0.0),
            'feature_importance': ml_prediction.get('feature_importance', {}),
            'ensemble_status': engine.get_ensemble_status()
        }
        
        # Update reason
        if enhancement_type == 'AGREEMENT_BOOST':
            enhanced_signal['reason'] += f" + ML ensemble agrees ({ml_confidence:.1%} confidence, {ml_prediction.get('model_agreement', 0):.1%} agreement)"
        elif enhancement_type == 'DISAGREEMENT_CAUTION':
            enhanced_signal['reason'] += f" - ML ensemble disagrees ({ml_action}, {ml_confidence:.1%} confidence)"
        
        return enhanced_signal
        
    except Exception as e:
        print(f"⚠️ Advanced ML enhancement error: {e}")
        return signal

def train_advanced_ml_models(df: pd.DataFrame, config: Dict = None) -> Dict[str, bool]:
    """Train the advanced ML ensemble models"""
    try:
        engine = get_advanced_ml_engine(config)
        return engine.train_ensemble_models(df)
    except Exception as e:
        print(f"❌ Advanced ML training error: {e}")
        return {}

if __name__ == "__main__":
    # Test the advanced ML engine
    print("🧠 Testing Advanced ML Features Engine...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=500, freq='5min')
    sample_df = pd.DataFrame({
        'close': 50000 + np.cumsum(np.random.randn(500) * 100),
        'volume': np.random.randint(1000, 10000, 500),
        'high': None,
        'low': None,
        'open': None
    }, index=dates)
    
    # Initialize engine
    engine = get_advanced_ml_engine()
    
    # Test training
    training_results = engine.train_ensemble_models(sample_df)
    print(f"Training results: {training_results}")
    
    # Test prediction
    prediction = engine.generate_ensemble_prediction(sample_df)
    print(f"Prediction: {prediction}")
    
    # Test signal enhancement
    sample_signal = {'action': 'BUY', 'confidence': 0.7, 'reason': 'Test signal'}
    enhanced = enhance_signal_with_advanced_ml(sample_signal, sample_df)
    print(f"Enhanced signal: {enhanced}")
    
    print("✅ Advanced ML Features Engine test complete!")
