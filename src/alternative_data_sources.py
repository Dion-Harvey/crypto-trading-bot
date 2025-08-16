# =============================================================================
# PHASE 3 WEEK 4 - ALTERNATIVE DATA SOURCES
# =============================================================================
#
# Copyright (c) 2025 Dion Harvey. All rights reserved.
# Alternative Data Sources for Enhanced Trading Intelligence
#
# FEATURES:
# - GitHub Activity Analysis (Developer ecosystem health)
# - Social Media Sentiment Aggregation (Twitter, Reddit, Telegram)
# - Network Effects Analysis (Hash rate, active addresses, transaction volume)
# - Developer Ecosystem Health Metrics
# - Market Psychology and Fear/Greed Indicators
# - Cross-Platform Signal Correlation
#
# =============================================================================

import requests
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
import hashlib
import random

@dataclass
class AlternativeDataPoint:
    """Individual alternative data point"""
    source: str
    metric: str
    value: float
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class NetworkMetrics:
    """Network-level cryptocurrency metrics"""
    hash_rate: float
    active_addresses: int
    transaction_volume: float
    network_value: float
    network_health_score: float
    timestamp: datetime

class GitHubActivityAnalyzer:
    """
    🧑‍💻 GITHUB ACTIVITY ANALYSIS
    
    Analyzes developer ecosystem health through GitHub activity
    """
    
    def __init__(self):
        self.logger = logging.getLogger('GitHubAnalyzer')
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
        
        # Crypto project repositories to monitor
        self.crypto_repos = {
            'bitcoin': ['bitcoin/bitcoin'],
            'ethereum': ['ethereum/go-ethereum', 'ethereum/ethereum-org-website'],
            'cardano': ['input-output-hk/cardano-node'],
            'polkadot': ['paritytech/polkadot'],
            'chainlink': ['smartcontractkit/chainlink'],
            'solana': ['solana-labs/solana'],
            'avalanche': ['ava-labs/avalanchego'],
            'polygon': ['maticnetwork/polygon-edge'],
            'cosmos': ['cosmos/cosmos-sdk'],
            'general': ['DeFiPulse/DeFiPulse-API', 'yearn/yearn-vaults']
        }
    
    def analyze_developer_activity(self, symbol: str = 'BTC') -> Dict[str, Any]:
        """
        Analyze GitHub developer activity for cryptocurrency projects
        """
        try:
            cache_key = f"github_{symbol}_{int(time.time() / self.cache_duration)}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Map symbol to repository category
            repo_category = self._map_symbol_to_repos(symbol)
            repos = self.crypto_repos.get(repo_category, self.crypto_repos['general'])
            
            activity_metrics = {
                'total_commits': 0,
                'active_contributors': 0,
                'open_issues': 0,
                'closed_issues': 0,
                'pull_requests': 0,
                'code_frequency': 0,
                'community_engagement': 0,
                'development_momentum': 0.0
            }
            
            # Simulate GitHub API calls (replace with real API in production)
            for repo in repos:
                repo_activity = self._simulate_repo_activity(repo)
                
                activity_metrics['total_commits'] += repo_activity['commits']
                activity_metrics['active_contributors'] += repo_activity['contributors']
                activity_metrics['open_issues'] += repo_activity['open_issues']
                activity_metrics['closed_issues'] += repo_activity['closed_issues']
                activity_metrics['pull_requests'] += repo_activity['pull_requests']
                activity_metrics['code_frequency'] += repo_activity['code_frequency']
                activity_metrics['community_engagement'] += repo_activity['engagement']
            
            # Calculate development momentum score
            development_momentum = self._calculate_development_momentum(activity_metrics)
            activity_metrics['development_momentum'] = development_momentum
            
            # Calculate ecosystem health score
            ecosystem_health = self._calculate_ecosystem_health(activity_metrics)
            
            result = {
                'symbol': symbol,
                'activity_metrics': activity_metrics,
                'ecosystem_health_score': ecosystem_health,
                'developer_sentiment': self._classify_developer_sentiment(ecosystem_health),
                'repositories_analyzed': repos,
                'analysis_timestamp': datetime.now(),
                'confidence_score': 0.8,  # High confidence for GitHub data
                'recommendations': self._generate_development_recommendations(ecosystem_health)
            }
            
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            self.logger.error(f"❌ GitHub analysis error: {e}")
            return self._get_fallback_github_data(symbol)
    
    def _map_symbol_to_repos(self, symbol: str) -> str:
        """Map trading symbol to GitHub repository category"""
        mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'SOL': 'solana',
            'AVAX': 'avalanche',
            'MATIC': 'polygon',
            'ATOM': 'cosmos'
        }
        return mapping.get(symbol.replace('/USDT', '').replace('USDT', ''), 'general')
    
    def _simulate_repo_activity(self, repo: str) -> Dict[str, int]:
        """Simulate GitHub repository activity (replace with real API calls)"""
        # Create deterministic but realistic values based on repo name
        seed = int(hashlib.md5(repo.encode()).hexdigest()[:8], 16)
        np.random.seed(seed % 10000)
        
        base_activity = {
            'bitcoin/bitcoin': {'commits': 150, 'contributors': 45, 'multiplier': 1.5},
            'ethereum/go-ethereum': {'commits': 200, 'contributors': 60, 'multiplier': 1.3},
            'solana-labs/solana': {'commits': 300, 'contributors': 80, 'multiplier': 1.8}
        }
        
        default_base = {'commits': 100, 'contributors': 30, 'multiplier': 1.0}
        base = base_activity.get(repo, default_base)
        
        # Add some realistic variation
        variation = np.random.uniform(0.7, 1.3)
        
        return {
            'commits': int(base['commits'] * variation),
            'contributors': int(base['contributors'] * variation),
            'open_issues': np.random.randint(50, 200),
            'closed_issues': np.random.randint(100, 300),
            'pull_requests': np.random.randint(20, 80),
            'code_frequency': np.random.randint(1000, 5000),
            'engagement': np.random.randint(100, 500)
        }
    
    def _calculate_development_momentum(self, metrics: Dict[str, int]) -> float:
        """Calculate development momentum score (0-1)"""
        try:
            # Normalize metrics
            commit_score = min(1.0, metrics['total_commits'] / 500)
            contributor_score = min(1.0, metrics['active_contributors'] / 100)
            issue_resolution_rate = metrics['closed_issues'] / max(1, metrics['open_issues'] + metrics['closed_issues'])
            pr_activity = min(1.0, metrics['pull_requests'] / 200)
            
            momentum = (
                commit_score * 0.3 +
                contributor_score * 0.25 +
                issue_resolution_rate * 0.25 +
                pr_activity * 0.2
            )
            
            return min(1.0, momentum)
            
        except Exception as e:
            return 0.5
    
    def _calculate_ecosystem_health(self, metrics: Dict[str, int]) -> float:
        """Calculate overall ecosystem health score (0-1)"""
        try:
            momentum = metrics['development_momentum']
            community_factor = min(1.0, metrics['community_engagement'] / 1000)
            code_quality = min(1.0, metrics['code_frequency'] / 10000)
            
            health_score = (momentum * 0.5 + community_factor * 0.3 + code_quality * 0.2)
            return min(1.0, health_score)
            
        except Exception as e:
            return 0.5
    
    def _classify_developer_sentiment(self, health_score: float) -> str:
        """Classify developer sentiment based on ecosystem health"""
        if health_score > 0.8:
            return 'VERY_BULLISH'
        elif health_score > 0.6:
            return 'BULLISH'
        elif health_score > 0.4:
            return 'NEUTRAL'
        elif health_score > 0.2:
            return 'BEARISH'
        else:
            return 'VERY_BEARISH'
    
    def _generate_development_recommendations(self, health_score: float) -> List[str]:
        """Generate trading recommendations based on development activity"""
        recommendations = []
        
        if health_score > 0.8:
            recommendations.extend([
                "Strong developer ecosystem suggests long-term bullish outlook",
                "High development activity indicates network growth potential",
                "Consider increasing position size based on fundamental strength"
            ])
        elif health_score > 0.6:
            recommendations.extend([
                "Solid development activity supports current price levels",
                "Moderate ecosystem health suggests stable growth potential"
            ])
        elif health_score < 0.4:
            recommendations.extend([
                "Declining developer activity may indicate ecosystem concerns",
                "Consider reducing exposure until development momentum improves",
                "Monitor for any fundamental issues affecting the project"
            ])
        
        return recommendations
    
    def _get_fallback_github_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback data when GitHub analysis fails"""
        return {
            'symbol': symbol,
            'activity_metrics': {
                'total_commits': 100,
                'active_contributors': 30,
                'development_momentum': 0.5
            },
            'ecosystem_health_score': 0.5,
            'developer_sentiment': 'NEUTRAL',
            'analysis_timestamp': datetime.now(),
            'confidence_score': 0.3,
            'recommendations': ["GitHub analysis unavailable - using fallback data"]
        }

class NetworkEffectsAnalyzer:
    """
    🌐 NETWORK EFFECTS ANALYSIS
    
    Analyzes blockchain network health and adoption metrics
    """
    
    def __init__(self):
        self.logger = logging.getLogger('NetworkEffectsAnalyzer')
        self.cache = {}
        self.cache_duration = 1800  # 30 minutes cache
    
    def analyze_network_effects(self, symbol: str = 'BTC') -> Dict[str, Any]:
        """
        Analyze network effects and adoption metrics
        """
        try:
            cache_key = f"network_{symbol}_{int(time.time() / self.cache_duration)}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Get network metrics
            network_metrics = self._get_network_metrics(symbol)
            
            # Calculate network effects scores
            network_value_score = self._calculate_network_value_score(network_metrics)
            adoption_score = self._calculate_adoption_score(network_metrics)
            security_score = self._calculate_security_score(network_metrics)
            
            # Calculate overall network health
            overall_health = (network_value_score * 0.4 + adoption_score * 0.4 + security_score * 0.2)
            
            # Generate network insights
            insights = self._generate_network_insights(network_metrics, overall_health)
            
            result = {
                'symbol': symbol,
                'network_metrics': network_metrics,
                'network_value_score': network_value_score,
                'adoption_score': adoption_score,
                'security_score': security_score,
                'overall_network_health': overall_health,
                'network_growth_trend': self._calculate_growth_trend(network_metrics),
                'insights': insights,
                'analysis_timestamp': datetime.now(),
                'confidence_score': 0.75
            }
            
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Network effects analysis error: {e}")
            return self._get_fallback_network_data(symbol)
    
    def _get_network_metrics(self, symbol: str) -> Dict[str, float]:
        """Get blockchain network metrics (simulated - replace with real API)"""
        # Simulate realistic network metrics
        base_metrics = {
            'BTC': {
                'hash_rate': 600_000_000,  # TH/s
                'active_addresses': 1_000_000,
                'transaction_volume': 50_000,
                'network_value': 1_200_000_000_000,  # Market cap
                'transaction_fees': 25.0
            },
            'ETH': {
                'hash_rate': 900_000,  # GH/s (different unit)
                'active_addresses': 800_000,
                'transaction_volume': 1_200_000,
                'network_value': 400_000_000_000,
                'transaction_fees': 15.0
            }
        }
        
        symbol_clean = symbol.replace('/USDT', '').replace('USDT', '')
        base = base_metrics.get(symbol_clean, base_metrics['BTC'])
        
        # Add realistic variation
        variation = np.random.uniform(0.9, 1.1)
        
        return {
            'hash_rate': base['hash_rate'] * variation,
            'active_addresses': int(base['active_addresses'] * variation),
            'transaction_volume': int(base['transaction_volume'] * variation),
            'network_value': base['network_value'] * variation,
            'transaction_fees': base['transaction_fees'] * variation,
            'block_time': 10.0 + np.random.uniform(-2, 2),  # minutes
            'mempool_size': np.random.randint(5000, 50000),
            'node_count': np.random.randint(10000, 50000)
        }
    
    def _calculate_network_value_score(self, metrics: Dict[str, float]) -> float:
        """Calculate network value score based on Metcalfe's Law"""
        try:
            # Metcalfe's Law: Network value proportional to square of active users
            active_addresses = metrics['active_addresses']
            transaction_volume = metrics['transaction_volume']
            
            # Normalize scores
            address_score = min(1.0, np.sqrt(active_addresses) / 3000)  # Normalize to 0-1
            volume_score = min(1.0, transaction_volume / 2_000_000)
            
            network_value_score = (address_score * 0.6 + volume_score * 0.4)
            return min(1.0, network_value_score)
            
        except Exception as e:
            return 0.5
    
    def _calculate_adoption_score(self, metrics: Dict[str, float]) -> float:
        """Calculate adoption score based on usage metrics"""
        try:
            active_addresses = metrics['active_addresses']
            transaction_volume = metrics['transaction_volume']
            node_count = metrics['node_count']
            
            # Normalize adoption metrics
            address_adoption = min(1.0, active_addresses / 2_000_000)
            volume_adoption = min(1.0, transaction_volume / 1_500_000)
            decentralization = min(1.0, node_count / 30_000)
            
            adoption_score = (
                address_adoption * 0.4 +
                volume_adoption * 0.4 +
                decentralization * 0.2
            )
            
            return min(1.0, adoption_score)
            
        except Exception as e:
            return 0.5
    
    def _calculate_security_score(self, metrics: Dict[str, float]) -> float:
        """Calculate network security score"""
        try:
            hash_rate = metrics['hash_rate']
            node_count = metrics['node_count']
            block_time = metrics['block_time']
            
            # Normalize security metrics
            hash_rate_score = min(1.0, hash_rate / 1_000_000_000)  # Normalize to network size
            decentralization_score = min(1.0, node_count / 40_000)
            consistency_score = max(0.0, 1.0 - abs(block_time - 10) / 10)  # Ideal block time
            
            security_score = (
                hash_rate_score * 0.5 +
                decentralization_score * 0.3 +
                consistency_score * 0.2
            )
            
            return min(1.0, security_score)
            
        except Exception as e:
            return 0.5
    
    def _calculate_growth_trend(self, metrics: Dict[str, float]) -> str:
        """Calculate network growth trend"""
        # Simulate growth trend analysis
        growth_indicators = [
            metrics['active_addresses'] > 800_000,
            metrics['transaction_volume'] > 40_000,
            metrics['hash_rate'] > 500_000_000,
            metrics['node_count'] > 15_000
        ]
        
        positive_indicators = sum(growth_indicators)
        
        if positive_indicators >= 3:
            return 'STRONG_GROWTH'
        elif positive_indicators >= 2:
            return 'MODERATE_GROWTH'
        elif positive_indicators >= 1:
            return 'SLOW_GROWTH'
        else:
            return 'STAGNANT'
    
    def _generate_network_insights(self, metrics: Dict[str, float], health_score: float) -> List[str]:
        """Generate insights based on network analysis"""
        insights = []
        
        if health_score > 0.8:
            insights.append("Network fundamentals are extremely strong")
            insights.append("High adoption and security suggest bullish long-term outlook")
        elif health_score > 0.6:
            insights.append("Network shows solid fundamentals")
            insights.append("Steady adoption supports current valuation")
        elif health_score < 0.4:
            insights.append("Network fundamentals show weakness")
            insights.append("Consider monitoring for further deterioration")
        
        # Transaction volume insights
        if metrics['transaction_volume'] > 100_000:
            insights.append("High transaction volume indicates active usage")
        elif metrics['transaction_volume'] < 20_000:
            insights.append("Low transaction volume may indicate reduced activity")
        
        # Security insights
        if metrics['hash_rate'] > 700_000_000:
            insights.append("Network security is exceptionally high")
        elif metrics['hash_rate'] < 200_000_000:
            insights.append("Network security may need monitoring")
        
        return insights
    
    def _get_fallback_network_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback data when network analysis fails"""
        return {
            'symbol': symbol,
            'network_metrics': {'active_addresses': 500000, 'transaction_volume': 30000},
            'overall_network_health': 0.5,
            'network_growth_trend': 'MODERATE_GROWTH',
            'insights': ["Network analysis unavailable - using fallback data"],
            'analysis_timestamp': datetime.now(),
            'confidence_score': 0.3
        }

class AlternativeDataAggregator:
    """
    📊 ALTERNATIVE DATA AGGREGATOR
    
    Combines all alternative data sources into comprehensive intelligence
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or self._get_default_config()
        self.logger = self._setup_logger()
        
        # Initialize analyzers
        self.github_analyzer = GitHubActivityAnalyzer()
        self.network_analyzer = NetworkEffectsAnalyzer()
        
        # Data cache
        self.aggregated_cache = {}
        self.cache_duration = 1800  # 30 minutes
        
        self.logger.info("📊 Alternative Data Aggregator initialized - Phase 3 Week 4")
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'data_weights': {
                'github_activity': 0.25,
                'network_effects': 0.35,
                'sentiment_correlation': 0.20,
                'market_psychology': 0.20
            },
            'confidence_thresholds': {
                'high': 0.75,
                'medium': 0.5,
                'low': 0.3
            },
            'signal_fusion': {
                'consensus_threshold': 0.6,
                'disagreement_penalty': 0.15
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger"""
        logger = logging.getLogger('AlternativeDataAggregator')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def get_comprehensive_alternative_data(self, symbol: str = 'BTC/USDT') -> Dict[str, Any]:
        """
        🎯 GET COMPREHENSIVE ALTERNATIVE DATA ANALYSIS
        
        Combines all alternative data sources for complete market intelligence
        """
        try:
            cache_key = f"alt_data_{symbol}_{int(time.time() / self.cache_duration)}"
            if cache_key in self.aggregated_cache:
                return self.aggregated_cache[cache_key]
            
            symbol_clean = symbol.replace('/USDT', '').replace('USDT', '')
            
            # 🧑‍💻 GITHUB DEVELOPER ACTIVITY
            github_data = self.github_analyzer.analyze_developer_activity(symbol_clean)
            
            # 🌐 NETWORK EFFECTS ANALYSIS
            network_data = self.network_analyzer.analyze_network_effects(symbol_clean)
            
            # 📊 SOCIAL SENTIMENT (Enhanced from existing sentiment analysis)
            social_sentiment = self._analyze_social_sentiment_correlation(symbol_clean)
            
            # 🧠 MARKET PSYCHOLOGY INDICATORS
            market_psychology = self._analyze_market_psychology(symbol_clean)
            
            # 🎯 AGGREGATE ALL DATA SOURCES
            aggregated_analysis = self._aggregate_alternative_data({
                'github': github_data,
                'network': network_data,
                'social': social_sentiment,
                'psychology': market_psychology
            })
            
            # 🎯 GENERATE COMPREHENSIVE INSIGHTS
            comprehensive_insights = self._generate_comprehensive_insights(aggregated_analysis)
            
            result = {
                'symbol': symbol,
                'analysis_timestamp': datetime.now(),
                'data_sources': {
                    'github_activity': github_data,
                    'network_effects': network_data,
                    'social_sentiment': social_sentiment,
                    'market_psychology': market_psychology
                },
                'aggregated_scores': aggregated_analysis,
                'comprehensive_insights': comprehensive_insights,
                'trading_recommendations': self._generate_trading_recommendations(aggregated_analysis),
                'confidence_level': self._calculate_overall_confidence(aggregated_analysis),
                'alternative_data_summary': self._create_summary_metrics(aggregated_analysis)
            }
            
            self.aggregated_cache[cache_key] = result
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Comprehensive alternative data error: {e}")
            return self._get_fallback_comprehensive_data(symbol)
    
    def _analyze_social_sentiment_correlation(self, symbol: str) -> Dict[str, Any]:
        """Analyze social sentiment correlation across platforms"""
        try:
            # Simulate multi-platform sentiment analysis
            platforms = ['twitter', 'reddit', 'telegram', 'discord']
            
            sentiment_scores = {}
            for platform in platforms:
                # Simulate platform-specific sentiment
                base_sentiment = 0.5 + np.random.uniform(-0.3, 0.3)
                volume = np.random.randint(1000, 10000)
                
                sentiment_scores[platform] = {
                    'sentiment_score': base_sentiment,
                    'volume': volume,
                    'confidence': np.random.uniform(0.6, 0.9)
                }
            
            # Calculate weighted sentiment
            total_weight = 0
            weighted_sentiment = 0
            
            for platform, data in sentiment_scores.items():
                weight = np.sqrt(data['volume']) * data['confidence']
                weighted_sentiment += data['sentiment_score'] * weight
                total_weight += weight
            
            overall_sentiment = weighted_sentiment / total_weight if total_weight > 0 else 0.5
            
            return {
                'symbol': symbol,
                'platform_sentiments': sentiment_scores,
                'overall_sentiment': overall_sentiment,
                'sentiment_classification': self._classify_sentiment(overall_sentiment),
                'cross_platform_correlation': np.random.uniform(0.6, 0.9),
                'sentiment_momentum': np.random.uniform(-0.2, 0.2),
                'analysis_timestamp': datetime.now(),
                'confidence_score': 0.7
            }
            
        except Exception as e:
            self.logger.error(f"❌ Social sentiment analysis error: {e}")
            return {'overall_sentiment': 0.5, 'confidence_score': 0.3}
    
    def _analyze_market_psychology(self, symbol: str) -> Dict[str, Any]:
        """Analyze market psychology indicators"""
        try:
            # Simulate market psychology metrics
            fear_greed_index = np.random.uniform(0, 100)
            volatility_sentiment = np.random.uniform(0.3, 0.8)
            momentum_psychology = np.random.uniform(-0.5, 0.5)
            
            # FOMO/FUD indicators
            fomo_indicator = np.random.uniform(0, 1)
            fud_indicator = np.random.uniform(0, 1)
            
            # Institutional vs retail sentiment
            institutional_sentiment = np.random.uniform(0.3, 0.8)
            retail_sentiment = np.random.uniform(0.2, 0.9)
            
            # Calculate composite psychology score
            psychology_score = (
                (fear_greed_index / 100) * 0.3 +
                volatility_sentiment * 0.2 +
                (momentum_psychology + 0.5) * 0.2 +  # Normalize to 0-1
                institutional_sentiment * 0.15 +
                retail_sentiment * 0.15
            )
            
            return {
                'symbol': symbol,
                'fear_greed_index': fear_greed_index,
                'volatility_sentiment': volatility_sentiment,
                'momentum_psychology': momentum_psychology,
                'fomo_indicator': fomo_indicator,
                'fud_indicator': fud_indicator,
                'institutional_sentiment': institutional_sentiment,
                'retail_sentiment': retail_sentiment,
                'composite_psychology_score': psychology_score,
                'market_mood': self._classify_market_mood(psychology_score),
                'analysis_timestamp': datetime.now(),
                'confidence_score': 0.65
            }
            
        except Exception as e:
            self.logger.error(f"❌ Market psychology analysis error: {e}")
            return {'composite_psychology_score': 0.5, 'confidence_score': 0.3}
    
    def _classify_sentiment(self, sentiment_score: float) -> str:
        """Classify sentiment score"""
        if sentiment_score > 0.7:
            return 'VERY_BULLISH'
        elif sentiment_score > 0.55:
            return 'BULLISH'
        elif sentiment_score > 0.45:
            return 'NEUTRAL'
        elif sentiment_score > 0.3:
            return 'BEARISH'
        else:
            return 'VERY_BEARISH'
    
    def _classify_market_mood(self, psychology_score: float) -> str:
        """Classify market mood"""
        if psychology_score > 0.8:
            return 'EXTREME_GREED'
        elif psychology_score > 0.6:
            return 'GREED'
        elif psychology_score > 0.4:
            return 'NEUTRAL'
        elif psychology_score > 0.2:
            return 'FEAR'
        else:
            return 'EXTREME_FEAR'
    
    def _aggregate_alternative_data(self, data_sources: Dict[str, Dict]) -> Dict[str, float]:
        """Aggregate all alternative data sources into composite scores"""
        try:
            weights = self.config['data_weights']
            
            # Extract key scores from each source
            github_score = data_sources['github'].get('ecosystem_health_score', 0.5)
            network_score = data_sources['network'].get('overall_network_health', 0.5)
            social_score = data_sources['social'].get('overall_sentiment', 0.5)
            psychology_score = data_sources['psychology'].get('composite_psychology_score', 0.5)
            
            # Calculate weighted composite score
            composite_score = (
                github_score * weights['github_activity'] +
                network_score * weights['network_effects'] +
                social_score * weights['sentiment_correlation'] +
                psychology_score * weights['market_psychology']
            )
            
            # Calculate individual dimension scores
            fundamental_strength = (github_score * 0.6 + network_score * 0.4)
            sentiment_strength = (social_score * 0.6 + psychology_score * 0.4)
            
            # Calculate consensus/divergence
            scores = [github_score, network_score, social_score, psychology_score]
            consensus_level = 1.0 - np.std(scores)  # Higher std = lower consensus
            
            return {
                'composite_score': composite_score,
                'fundamental_strength': fundamental_strength,
                'sentiment_strength': sentiment_strength,
                'consensus_level': consensus_level,
                'github_score': github_score,
                'network_score': network_score,
                'social_score': social_score,
                'psychology_score': psychology_score
            }
            
        except Exception as e:
            self.logger.error(f"❌ Data aggregation error: {e}")
            return {
                'composite_score': 0.5,
                'fundamental_strength': 0.5,
                'sentiment_strength': 0.5,
                'consensus_level': 0.5
            }
    
    def _generate_comprehensive_insights(self, aggregated_data: Dict[str, float]) -> List[str]:
        """Generate comprehensive insights from aggregated data"""
        insights = []
        
        composite = aggregated_data['composite_score']
        fundamental = aggregated_data['fundamental_strength']
        sentiment = aggregated_data['sentiment_strength']
        consensus = aggregated_data['consensus_level']
        
        # Overall assessment
        if composite > 0.75:
            insights.append("🚀 Alternative data shows very strong bullish signals across multiple dimensions")
        elif composite > 0.6:
            insights.append("📈 Alternative data indicates positive momentum with good fundamentals")
        elif composite < 0.4:
            insights.append("📉 Alternative data suggests caution with mixed signals")
        else:
            insights.append("⚠️ Alternative data shows concerning trends across multiple metrics")
        
        # Fundamental vs sentiment analysis
        if fundamental > sentiment + 0.2:
            insights.append("💎 Strong fundamentals (dev activity + network health) outweigh sentiment concerns")
        elif sentiment > fundamental + 0.2:
            insights.append("🎭 Market sentiment driving performance more than fundamental factors")
        else:
            insights.append("⚖️ Fundamentals and sentiment are well-aligned")
        
        # Consensus analysis
        if consensus > 0.8:
            insights.append("🎯 High consensus across all alternative data sources")
        elif consensus < 0.5:
            insights.append("🔀 Mixed signals across alternative data sources - proceed with caution")
        
        # Specific recommendations
        if aggregated_data['github_score'] > 0.8:
            insights.append("🧑‍💻 Developer ecosystem is extremely healthy - strong long-term outlook")
        
        if aggregated_data['network_score'] > 0.8:
            insights.append("🌐 Network effects are strong - adoption and security metrics excellent")
        
        return insights
    
    def _generate_trading_recommendations(self, aggregated_data: Dict[str, float]) -> List[str]:
        """Generate specific trading recommendations"""
        recommendations = []
        
        composite = aggregated_data['composite_score']
        consensus = aggregated_data['consensus_level']
        
        if composite > 0.8 and consensus > 0.7:
            recommendations.extend([
                "Strong BUY signal from alternative data",
                "Consider increasing position size",
                "High confidence for long-term holdings"
            ])
        elif composite > 0.65 and consensus > 0.6:
            recommendations.extend([
                "Moderate BUY signal",
                "Good risk/reward for new positions",
                "Monitor for continued strength"
            ])
        elif composite < 0.35 or consensus < 0.4:
            recommendations.extend([
                "Consider reducing exposure",
                "Wait for clearer alternative data signals",
                "High uncertainty across data sources"
            ])
        else:
            recommendations.append("Hold current positions - mixed alternative data signals")
        
        return recommendations
    
    def _calculate_overall_confidence(self, aggregated_data: Dict[str, float]) -> str:
        """Calculate overall confidence level"""
        consensus = aggregated_data['consensus_level']
        
        if consensus > self.config['confidence_thresholds']['high']:
            return 'HIGH'
        elif consensus > self.config['confidence_thresholds']['medium']:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _create_summary_metrics(self, aggregated_data: Dict[str, float]) -> Dict[str, Any]:
        """Create summary metrics for display"""
        return {
            'overall_signal': 'BULLISH' if aggregated_data['composite_score'] > 0.6 else 'BEARISH' if aggregated_data['composite_score'] < 0.4 else 'NEUTRAL',
            'signal_strength': aggregated_data['composite_score'],
            'consensus_rating': 'HIGH' if aggregated_data['consensus_level'] > 0.7 else 'MEDIUM' if aggregated_data['consensus_level'] > 0.5 else 'LOW',
            'fundamental_rating': 'STRONG' if aggregated_data['fundamental_strength'] > 0.7 else 'MODERATE' if aggregated_data['fundamental_strength'] > 0.5 else 'WEAK',
            'sentiment_rating': 'BULLISH' if aggregated_data['sentiment_strength'] > 0.6 else 'BEARISH' if aggregated_data['sentiment_strength'] < 0.4 else 'NEUTRAL'
        }
    
    def _get_fallback_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback data when comprehensive analysis fails"""
        return {
            'symbol': symbol,
            'analysis_timestamp': datetime.now(),
            'aggregated_scores': {
                'composite_score': 0.5,
                'consensus_level': 0.5
            },
            'comprehensive_insights': ["Alternative data analysis unavailable"],
            'trading_recommendations': ["Monitor manually due to data unavailability"],
            'confidence_level': 'LOW'
        }

# =============================================================================
# GLOBAL INSTANCES AND HELPER FUNCTIONS
# =============================================================================

_alternative_data_aggregator = None

def get_alternative_data_aggregator(config: Dict = None) -> AlternativeDataAggregator:
    """Get or create the global alternative data aggregator instance"""
    global _alternative_data_aggregator
    if _alternative_data_aggregator is None:
        _alternative_data_aggregator = AlternativeDataAggregator(config)
    return _alternative_data_aggregator

def enhance_signal_with_alternative_data(signal: Dict, symbol: str = 'BTC/USDT') -> Dict:
    """
    🎯 ENHANCE TRADING SIGNAL WITH ALTERNATIVE DATA
    
    Combines traditional trading signal with alternative data intelligence
    """
    try:
        aggregator = get_alternative_data_aggregator()
        
        # Get comprehensive alternative data
        alt_data = aggregator.get_comprehensive_alternative_data(symbol)
        
        # Extract key metrics
        composite_score = alt_data['aggregated_scores']['composite_score']
        confidence_level = alt_data['confidence_level']
        consensus_level = alt_data['aggregated_scores']['consensus_level']
        
        # Calculate enhancement
        original_confidence = signal.get('confidence', 0.5)
        
        if confidence_level == 'HIGH' and consensus_level > 0.7:
            # High confidence alternative data
            if composite_score > 0.7 and signal.get('action') == 'BUY':
                # Alternative data supports BUY
                confidence_boost = min(0.2, (composite_score - 0.5) * 0.4)
                enhanced_confidence = min(0.95, original_confidence + confidence_boost)
                enhancement_type = 'STRONG_SUPPORT'
            elif composite_score < 0.3 and signal.get('action') == 'SELL':
                # Alternative data supports SELL
                confidence_boost = min(0.2, (0.5 - composite_score) * 0.4)
                enhanced_confidence = min(0.95, original_confidence + confidence_boost)
                enhancement_type = 'STRONG_SUPPORT'
            elif abs(composite_score - 0.5) > 0.2:
                # Alternative data disagrees
                confidence_reduction = min(0.15, abs(composite_score - 0.5) * 0.3)
                enhanced_confidence = max(0.3, original_confidence - confidence_reduction)
                enhancement_type = 'DATA_CONFLICT'
            else:
                enhanced_confidence = original_confidence
                enhancement_type = 'NEUTRAL'
        else:
            # Low confidence or consensus - minimal impact
            enhanced_confidence = original_confidence
            enhancement_type = 'LOW_CONFIDENCE'
        
        # Create enhanced signal
        enhanced_signal = signal.copy()
        enhanced_signal['confidence'] = enhanced_confidence
        enhanced_signal['alternative_data_enhancement'] = {
            'alternative_data': alt_data,
            'enhancement_type': enhancement_type,
            'confidence_change': enhanced_confidence - original_confidence,
            'composite_score': composite_score,
            'consensus_level': consensus_level,
            'summary': alt_data['alternative_data_summary']
        }
        
        # Update reason
        if enhancement_type == 'STRONG_SUPPORT':
            enhanced_signal['reason'] += f" + Alternative data strongly supports ({composite_score:.1%} composite score)"
        elif enhancement_type == 'DATA_CONFLICT':
            enhanced_signal['reason'] += f" - Alternative data shows conflicting signals ({composite_score:.1%} vs trade direction)"
        
        return enhanced_signal
        
    except Exception as e:
        print(f"⚠️ Alternative data enhancement error: {e}")
        return signal

def get_alternative_data_insights(symbol: str = 'BTC/USDT') -> Dict[str, Any]:
    """Get alternative data insights for display"""
    try:
        aggregator = get_alternative_data_aggregator()
        return aggregator.get_comprehensive_alternative_data(symbol)
    except Exception as e:
        print(f"❌ Alternative data insights error: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    # Test the alternative data system
    print("📊 Testing Alternative Data Sources Engine...")
    
    # Initialize aggregator
    aggregator = get_alternative_data_aggregator()
    
    # Test comprehensive analysis
    alt_data = aggregator.get_comprehensive_alternative_data('BTC/USDT')
    print(f"Alternative data analysis: {alt_data['alternative_data_summary']}")
    
    # Test signal enhancement
    sample_signal = {'action': 'BUY', 'confidence': 0.7, 'reason': 'Test signal'}
    enhanced = enhance_signal_with_alternative_data(sample_signal, 'BTC/USDT')
    print(f"Enhanced signal: {enhanced}")
    
    print("✅ Alternative Data Sources Engine test complete!")
