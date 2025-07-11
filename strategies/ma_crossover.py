import pandas as pd
import numpy as np
import time
from typing import Dict, List, Optional, Tuple

def fetch_ohlcv(exchange, symbol='BTC/USDT', timeframe='1m', limit=100):
    """Fetch recent candlestick data"""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

class MovingAverageCrossover:
    """
    Moving Average Crossover Strategy
    
    This strategy generates buy/sell signals based on the crossover of two moving averages:
    - Short MA crosses above Long MA = Buy signal
    - Short MA crosses below Long MA = Sell signal
    """

    def __init__(self, short_window: int = 10, long_window: int = 20):
        """
        Initialize the MA Crossover strategy
        
        Args:
            short_window: Period for short-term moving average
            long_window: Period for long-term moving average
        """
        self.short_window = short_window
        self.long_window = long_window
        self.name = f"MA_Crossover_{short_window}_{long_window}"

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate moving averages and generate signals
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicators and signals 
        """        # Calculate moving averages
        df[f'MA_{self.short_window}'] = df['close'].rolling(window=self.short_window).mean()
        df[f'MA_{self.long_window}'] = df['close'].rolling(window=self.long_window).mean()

        # Initialize position column
        df['position'] = 0

        # Precise crossover detection (true crossovers only)
        for i in range(1, len(df)):
            fast_prev = df[f'MA_{self.short_window}'].iloc[i-1]
            slow_prev = df[f'MA_{self.long_window}'].iloc[i-1]
            fast_curr = df[f'MA_{self.short_window}'].iloc[i]
            slow_curr = df[f'MA_{self.long_window}'].iloc[i]

            # Buy signal: fast crosses above slow
            if fast_prev <= slow_prev and fast_curr > slow_curr:
                df.iloc[i, df.columns.get_loc('position')] = 1
            # Sell signal: fast crosses below slow
            elif fast_prev >= slow_prev and fast_curr < slow_curr:
                df.iloc[i, df.columns.get_loc('position')] = -1

        return df

    def get_signal(self, df: pd.DataFrame) -> Dict:
        """
        Get the latest trading signal
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with signal information
        """
        if len(df) < self.long_window:
            return {
                'action': 'HOLD',
                'signal': 0,
                'confidence': 0,
                'reason': f'Insufficient data (need {self.long_window} periods)'
            }

        df_with_signals = self.calculate_indicators(df)
        latest = df_with_signals.iloc[-1]

        action = 'HOLD'
        confidence = 0
        reason = 'No crossover detected'

        if latest['position'] == 1:
            action = 'BUY'
            confidence = self._calculate_confidence(df_with_signals)
            reason = f"Short MA ({latest[f'MA_{self.short_window}']:.4f}) crossed above Long MA ({latest[f'MA_{self.long_window}']:.4f})"
        elif latest['position'] == -1:
            action = 'SELL'
            confidence = self._calculate_confidence(df_with_signals)
            reason = f"Short MA ({latest[f'MA_{self.short_window}']:.4f}) crossed below Long MA ({latest[f'MA_{self.long_window}']:.4f})"

        return {
            'action': action,
            'signal': latest['position'],
            'confidence': confidence,
            'reason': reason,
            'price': latest['close'],
            'short_ma': latest[f'MA_{self.short_window}'],
            'long_ma': latest[f'MA_{self.long_window}']
        }

    def _calculate_confidence(self, df: pd.DataFrame) -> float:
        """
        Calculate confidence score for the signal (0-1)
        Based on the spread between MAs and recent price trend
        """
        latest = df.iloc[-1]

        # Calculate MA spread as percentage
        ma_spread = abs(latest[f'MA_{self.short_window}'] - latest[f'MA_{self.long_window}']) / latest['close']

        # Calculate recent price momentum
        recent_data = df.tail(5)
        price_momentum = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]

        # Confidence increases with larger MA spread and aligned momentum
        confidence = min(1.0, ma_spread * 100 + abs(price_momentum) * 0.5)

        return round(confidence, 3)

    def backtest(self, df: pd.DataFrame, initial_balance: float = 10000) -> Dict:
        """
        Simple backtest of the strategy
        
        Args:
            df: DataFrame with OHLCV data
            initial_balance: Starting balance for backtest
            
        Returns:
            Dictionary with backtest results
        """
        df_bt = self.calculate_indicators(df.copy())

        balance = initial_balance
        position = 0
        trades = []

        for i, row in df_bt.iterrows():
            if row['position'] == 1 and position <= 0:  # Buy
                position = balance / row['close']
                balance = 0
                trades.append({
                    'date': i,
                    'action': 'BUY',
                    'price': row['close'],
                    'position': position
                })
            elif row['position'] == -1 and position > 0:  # Sell
                balance = position * row['close']
                position = 0
                trades.append({
                    'date': i,
                    'action': 'SELL',
                    'price': row['close'],
                    'balance': balance
                })

        # Calculate final balance
        final_balance = balance + (position * df_bt['close'].iloc[-1])
        total_return = (final_balance - initial_balance) / initial_balance * 100

        return {
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'total_return': round(total_return, 2),
            'total_trades': len(trades),
            'trades': trades
        }

    def get_parameters(self) -> Dict:
        """Get strategy parameters"""
        return {
            'name': self.name,
            'short_window': self.short_window,
            'long_window': self.long_window,
            'type': 'Trend Following'
        }

# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    import datetime

    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    np.random.seed(42)
    prices = 50000 + np.cumsum(np.random.randn(100) * 100)

    sample_data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(100, 1000, 100)
    })

    # Test the strategy
    strategy = MovingAverageCrossover(short_window=5, long_window=15)

    # Get latest signal
    signal = strategy.get_signal(sample_data)
    print(f"Strategy: {strategy.name}")
    print(f"Latest Signal: {signal}")

    # Run backtest
    backtest_results = strategy.backtest(sample_data)
    print(f"\nBacktest Results: {backtest_results}")
