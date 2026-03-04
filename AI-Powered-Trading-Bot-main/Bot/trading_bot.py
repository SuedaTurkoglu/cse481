import asyncio
import time
import os
from dotenv import load_dotenv
import pandas as pd

from Patterns.Observer.subject import Subject
from Patterns.Strategies.RSI import RSIStrategy
from Patterns.Strategies.MACD import MACDStrategy
from Patterns.Strategies.ADX import ADXStrategy
from Patterns.Strategies.Default import DefaultStrategy
from Indicator.calculator import IndicatorCalculator
from Data_Initializer.initializer import DataLoader

# Load environment variables
load_dotenv()

class TradingBot(Subject):
    """
    Trading Bot - Strategy Pattern'in Context sınıfı
    Subject Pattern - Observer'ları bilgilendirir
    """

    def __init__(self, coin_symbol: str):
        """
        Initialize the trading bot.
        
        Args:
            coin_symbol (str): Cryptocurrency symbol (e.g., 'BTCUSDT')
        """
        self.coin_symbol = coin_symbol
        self.strategy = None
        self.observers = []
        self.df = None
        self._state_changed = False
        self.total_trades = 0      # Toplam tamamlanmış işlem sayısı (BUY ve SELL eşleşmesi)
        self.winning_trades = 0    # Kârlı kapanan işlem sayısı
        self.is_winning_trade = False # Mevcut işlemin kârlı olup olmadığını tutar
        
        # API credentials
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        
        # Helper objects
        self.indicator_calculator = IndicatorCalculator()
        self.data_loader = DataLoader()
        
        print(f"🤖 TradingBot initialized for {coin_symbol}")

    # Observer Pattern Methods
    def register_observer(self, observer):
        """Register an observer"""
        self.observers.append(observer)
        print(f"✅ Observer registered: {observer.__class__.__name__}")

    def remove_observer(self, observer):
        """Remove an observer"""
        self.observers.remove(observer)
        print(f"❌ Observer removed: {observer.__class__.__name__}")

    def set_change(self):
        """Mark whether subject state changed before notifying observers"""
        self._state_changed = True

    def notify_observers(self, message: str):
        """Notify observers only when a state change is flagged"""
        if not self._state_changed:
            return

        for observer in self.observers:
            observer.update(message)

        self._state_changed = False

    # Strategy Pattern Methods
    def set_strategy(self, strategy):
        """Set trading strategy (Strategy Pattern)"""
        self.strategy = strategy

    def trade(self, row, df):
        """Execute trade using current strategy"""
        return self.strategy.execute_strategy(row, df)

    # Data Methods
    def get_latest_data(self):
        """Fetch latest real-time data via WebSocket"""
        df = asyncio.run(self.data_loader.download_crypto_data(self.coin_symbol))
        self.df = df
        return df

    def get_interval_data(self):
        """Fetch historical data for indicators"""
        df = self.data_loader.download_crypto_data_interval(
            self.api_key, 
            self.api_secret, 
            self.coin_symbol
        )
        return df

    def get_interval_data_backtest(self, interval: str, check_date: str):
        """Fetch historical data for backtesting"""
        df = self.data_loader.download_crypto_data_interval_backtest(
            self.api_key,
            self.api_secret,
            self.coin_symbol,
            interval,
            check_date
        )
        return df

    # Strategy Evaluation
    def evaluate_strategies(self, row, stop_loss: float, historical_data):
        """Dynamically evaluate and select best strategy"""
        volatility = historical_data['Close'].std()
        
        rsi_weight = 0.4 * (1 + volatility)
        macd_weight = 0.3 * (1 - volatility)
        adx_weight = 0.3 * volatility

        rsi_score = row['rsi'] - historical_data['rsi'].mean()
        macd_score = row['macd'] - historical_data['macd'].mean()
        adx_score = row['adx'] - historical_data['adx'].mean()

        weighted_scores = [
            rsi_score * rsi_weight,
            macd_score * macd_weight,
            adx_score * adx_weight
        ]

        max_score_idx = weighted_scores.index(max(weighted_scores))
        
        if max(weighted_scores) > 0:
            if max_score_idx == 0:
                return RSIStrategy(stop_loss)
            elif max_score_idx == 1:
                return MACDStrategy(stop_loss)
            else:
                return ADXStrategy(stop_loss)
        else:
            return DefaultStrategy(stop_loss)

    def change_strategy(self, row, stop_loss: float, df):
        """Change strategy dynamically"""
        best_strategy = self.evaluate_strategies(row, stop_loss, df)
        self.set_strategy(best_strategy)

    # Trading Simulation
    def simulate_trading(self, initial_balance: float, stop_loss: float, interval: int, position_size_pct: float = 0.5):
        """Live trading simulation"""
        balance = initial_balance
        position = 0
        entry_price = 0
        trades = []

        start_time = time.time()
        print(f"\n🚀 Starting LIVE trading simulation for {self.coin_symbol}")
        print(f"   Initial Balance: ${balance:.2f}")
        print(f"   Stop Loss: {stop_loss*100}%")
        print(f"   Interval: {interval}s")
        print(f"   Position Size: {position_size_pct*100}%")
        print("="*70)

        while True:
            elapsed_time = time.time() - start_time

            self.get_latest_data()
            print(f"\n📥 Data acquired at {time.strftime('%H:%M:%S')}")

            row = self.df.iloc[-1]
            df = self.get_interval_data()
            df.loc[len(df)] = row
            df = self.indicator_calculator.calculate_indicators(df)

            row = df.iloc[-1]
            #self.change_strategy(row, stop_loss, df) #commented for case 1 & 2

            action = self.strategy.execute_strategy(
                row=row, 
                df=df_with_indicators, 
                position=position,         # Botun anlık pozisyon bilgisi
                entry_price=entry_price    # Botun giriş fiyatı bilgisi
            )
            
            if action == "Buy" and position == 0:
                entry_price = row['Close']
                investment_amount = balance * position_size_pct
                if investment_amount <= 0:
                    print(f"⏸️  Holding (Insufficient balance for {position_size_pct*100}% position), Strategy: {self.strategy.__class__.__name__}")
                    continue
                position = investment_amount / entry_price
                balance -= investment_amount
                trades.append(("BUY", entry_price, balance))
                message = f"Bought {self.coin_symbol}, Price: {entry_price}, Cash: ${balance:.2f}, Position: {position}, Strategy: {self.strategy.__class__.__name__}"
                print(f"✅ {message}")
                self.set_change()
                self.notify_observers(message)
                
            elif action == "Sell" and position > 0:
                sell_price = row['Close']
                sale_value = position * sell_price
                balance += sale_value
                position = 0
                trades.append(("SELL", sell_price, balance))
                message = f"Sold {self.coin_symbol}, Price: {sell_price}, New Balance: ${balance:.2f}, Strategy: {self.strategy.__class__.__name__}"
                print(f"💰 {message}")
                self.set_change()
                self.notify_observers(message)
                
            elif action == "Hold":
                print(f"⏸️  Holding, Strategy: {self.strategy.__class__.__name__}")

            if elapsed_time > interval:
                break
            
        if position > 0:
            last_price = df.iloc[-1]['Close'] # En son çekilen verinin son satırı
            sale_value = position * last_price
            balance += sale_value
            print(f"ℹ️ Simulation sonu: Kalan pozisyon {position} adet {self.coin_symbol} ${last_price} fiyattan satıldı.")
            self.set_change()
            self.notify_observers(f"Simulation sonu: Kalan pozisyon satıldı. Bakiye: ${balance:.2f}")
            
        self.set_change()
        self.notify_observers("Simulation complete")
        print(f"\n{'='*70}")
        print(f"📊 Simulation Complete!")
        print(f"   Final Balance: ${balance:.2f}")
        print(f"   Profit/Loss: ${balance - initial_balance:.2f}")
        print(f"{'='*70}\n")
        
        return balance

    def backtest_trading(self, initial_balance: float, stop_loss: float, 
                         df_with_indicators: pd.DataFrame, position_size_pct: float = 0.5):
        """Backtest trading on historical data"""
        balance = initial_balance
        position = 0
        entry_price = 0
        trades = []

        print(f"\n🔙 Starting BACKTEST for {self.coin_symbol}")
        print(f"   Initial Balance: ${balance:.2f}")
        print(f"   Position Size: {position_size_pct*100}%")

        #historical_df = self.get_interval_data_backtest(interval, check_date)
        #df_with_indicators = self.indicator_calculator.calculate_indicators(historical_df)
        
        print(f"📊 Processing {len(df_with_indicators)} candles...")

        for index, row in df_with_indicators.iterrows():
            #self.change_strategy(row, stop_loss, df_with_indicators) #commented for case 1 & 2

            action, trigger_rule = self.strategy.execute_strategy(
                row=row, 
                df=df_with_indicators, 
                position=position,         # Botun anlık pozisyon bilgisi
                entry_price=entry_price    # Botun giriş fiyatı bilgisi
            )

            try:
                trade_date = row['Timestamp'] 
            except AttributeError:
                trade_date = str(index)   
                
            # Loglanacak gösterge seçimi
            indicator_summary = (
                f"RSI={row['rsi']:.2f}, "
                f"BB_Lower={row['BB_lower']:.2f}, "
                f"KAMA={row['KAMA']:.2f}, "
                f"ST_DIR={row['ST_DIR']:.0f}"
            )      
            
            if action == "Buy" and position == 0:
                entry_price = row['Close']
                investment_amount = balance * position_size_pct
                if investment_amount <= 0:
                    continue
                position = investment_amount / entry_price
                balance -= investment_amount
                trades.append(("BUY", entry_price, balance))
                self.is_winning_trade = False
                message = (
                    f"Bought {self.coin_symbol}, Date: {trade_date}, Price: {entry_price:.2f}, "
                    f"Cash: ${balance:.2f}, Position: {position:.5f}, "
                    f"Strategy: {self.strategy.__class__.__name__}, "
                    f"Trigger: {trigger_rule}, Indicators: {indicator_summary}"
                )
                self.set_change()
                self.notify_observers(message)
                
            elif action == "Sell" and position > 0:
                sell_price = row['Close']
                # Kâr/Zarar kontrolü
                if sell_price > entry_price:
                    self.is_winning_trade = True
                sale_value = position * sell_price
                
                # PnL hesaplama (log detayına eklemek için)
                pnl = sale_value - (position * entry_price)
                pnl_pct = (sell_price / entry_price - 1) * 100
                self.total_trades += 1
                if self.is_winning_trade:
                    self.winning_trades += 1
                balance += sale_value
                position = 0
                trades.append(("SELL", sell_price, balance))
                message = (
                    f"Sold {self.coin_symbol}, Date: {trade_date}, Price: {sell_price:.2f}, "
                    f"New Balance: ${balance:.2f}, PnL: ${pnl:.2f} ({pnl_pct:.2f}%), "
                    f"Strategy: {self.strategy.__class__.__name__}, "
                    f"Trigger: {trigger_rule}, Indicators: {indicator_summary}"
                )
                self.set_change()
                self.notify_observers(message)
        
        if position > 0:
            last_price = df_with_indicators.iloc[-1]['Close']
            sale_value = position * last_price
            balance += sale_value
            print(f"ℹ️ Backtest sonu: Kalan pozisyon {position} adet {self.coin_symbol} ${last_price} fiyattan satıldı.")
            self.set_change()
            self.notify_observers(f"Backtest sonu: Kalan pozisyon satıldı. Bakiye: ${balance:.2f}")

        self.set_change()
        self.notify_observers("Simulation complete")
        
        print(f"\n📊 Backtest Complete!")
        print(f"   Final Balance: ${balance:.2f}")
        print(f"   Profit/Loss: ${balance - initial_balance:.2f} ({((balance/initial_balance - 1)*100):.2f}%)\n")
        print(f"{'='*70}\n")
        
        return balance

    def get_trade_statistics(self):
        """Hesaplanan ticaret istatistiklerini döndürür."""
        win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        
        return {
            "completed_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "win_rate": win_rate
        }