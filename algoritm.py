from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from binance.client import Client
import pandas as pd
import pygad
import numpy as np
import talib
from dotenv import load_dotenv
import os

def fetch_binance_data(client, symbol, interval, start_date, end_date=None):
    # Fetch historical klines from Binance
    klines = client.get_historical_klines(symbol, interval, start_date, end_date)

    # Convert to pandas DataFrame
    df = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Convert prices to floats
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col])

    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

    # Set timestamp as index
    df.set_index('timestamp', inplace=True)

    return df

# Load environment variables from .env file
load_dotenv()

class TradeStrategy(Strategy):
    def init(self):
        self.macd_line, self.signal_line, _ = self.I(talib.MACD, self.data.Close, self.macd_short_period, self.macd_long_period, self.macd_signal_period)
        self.sma1 = self.I(talib.SMA, self.data.Close, self.sma1_period)
        self.sma2 = self.I(talib.SMA, self.data.Close, self.sma1_period + self.sma2_period)
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
        self.upper, self.middle, self.lower = self.I(talib.BBANDS, self.data.Close, self.bb_period)

    def next(self):
        if ((crossover(self.macd_line, self.signal_line) and self.sma1[-1] > self.sma2[-1]) or 
            (crossover(self.sma1, self.sma2) and self.macd_line[-1] > self.signal_line[-1])) and \
            (self.rsi[-1] > self.rsi_oversold or self.data.Close[-1] < self.lower[-1]):
            self.buy(tp=self.data.Close[-1]*1.05, sl=self.data.Close[-1]*0.99)
        elif ((crossover(self.signal_line, self.macd_line) and self.sma1[-1] < self.sma2[-1]) or 
              (crossover(self.sma2, self.sma1) and self.macd_line[-1] < self.signal_line[-1])) and \
              (self.rsi[-1] < self.rsi_overbought or self.data.Close[-1] > self.upper[-1]):
            self.sell(tp=self.data.Close[-1]*0.95, sl=self.data.Close[-1]*1.01)

# Fitness function
def fitness_func(ga_instance, solution, solution_idx):
    macd_short_period, macd_long_period, macd_signal_period, sma1_period, sma2_period, rsi_period, rsi_oversold, rsi_overbought, bb_period = map(int, solution)
    
    TradeStrategy.macd_short_period = macd_short_period
    TradeStrategy.macd_long_period = macd_long_period
    TradeStrategy.macd_signal_period = macd_signal_period
    TradeStrategy.sma1_period = sma1_period
    TradeStrategy.sma2_period = sma2_period
    TradeStrategy.rsi_period = rsi_period
    TradeStrategy.rsi_oversold = rsi_oversold
    TradeStrategy.rsi_overbought = rsi_overbought
    TradeStrategy.bb_period = bb_period

    score = 1
    for df in ga_instance.dfList:
        bt = Backtest(df, TradeStrategy, cash=100000, commission=.0005, margin=.2)
        stats = bt.run()
        score *= stats['Win Rate [%]'] - 45
    return score


# Initialize Binance API client
binance_api_key = os.getenv('BINANCE_API_KEY')
binance_api_secret = os.getenv('BINANCE_API_SECRET')

client = Client(binance_api_key, binance_api_secret)

df = fetch_binance_data(client, 'BTCUSDT', Client.KLINE_INTERVAL_1HOUR, "1 years ago UTC")

# GA Parameters
num_generations = 60
num_parents_mating = 4
sol_per_pop = 15
num_genes = 9
mutation_num_genes = 4

# GA instance
ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_func=fitness_func,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       gene_space=[range(12, 26), range(26, 30), range(9, 21), range(10, 30), range(10, 100), range(14, 28), range(20, 80), range(70, 90), range(5, 50)],
                       mutation_num_genes=mutation_num_genes)


# [fetch_binance_data(client, 'BTCUSDT', Client.KLINE_INTERVAL_1HOUR, "1 months ago UTC")]+
ga_instance.dfList = [fetch_binance_data(client, 'BTCUSDT', Client.KLINE_INTERVAL_1HOUR, str(i+2) + " months ago UTC", str(i+1) + " months ago UTC") for i in range(7)]
# Run the GA
ga_instance.run()

# Print the details of the best solution
solution, solution_fitness, _ = ga_instance.best_solution()
macd_short_period, macd_long_period, macd_signal_period, sma1_period, sma2_period, rsi_period, rsi_oversold, rsi_overbought, bb_period = map(int, solution)

print(f"Best solution: MACD Short period={macd_short_period}, MACD Long period={macd_long_period}, MACD Signal period={macd_signal_period}, SMA1 period={sma1_period}, SMA2 period={sma2_period}, RSI period={rsi_period}, RSI Oversold={rsi_oversold}, RSI Overbought={rsi_overbought}, BB period={bb_period}")
print(f"Best solution fitness: {solution_fitness}")

# Set the best periods for MACD, SMA, RSI, and Bollinger Bands
TradeStrategy.macd_short_period = macd_short_period
TradeStrategy.macd_long_period = macd_long_period
TradeStrategy.macd_signal_period = macd_signal_period
TradeStrategy.sma1_period = sma1_period
TradeStrategy.sma2_period = sma2_period
TradeStrategy.rsi_period = rsi_period
TradeStrategy.rsi_oversold = rsi_oversold
TradeStrategy.rsi_overbought = rsi_overbought
TradeStrategy.bb_period = bb_period

df = fetch_binance_data(client, 'BTCUSDT', Client.KLINE_INTERVAL_1HOUR, "1 years ago UTC")

# Run backtest with the best solution
bt = Backtest(df, TradeStrategy, cash=100000, commission=.002, trade_on_close=True, exclusive_orders=True)
result = bt.run()
print(result)


# api fetch
df = fetch_binance_data(client, 'BTCUSDT', Client.KLINE_INTERVAL_1HOUR, "1 month ago UTC")

# Run backtest with the best solution
bt = Backtest(df, TradeStrategy, cash=100000, commission=.002, trade_on_close=True, exclusive_orders=True, margin=.2)
result = bt.run()
print(result)
bt.plot()
