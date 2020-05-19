import math
import backtrader as bt

class RSIpattern(bt.Strategy):
    """
    Strategy based on RSI dip below 30 and 20EMA / 50EMA crossover
    """
    def __init__(self):
        self.ema_20 = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=20, plotname='20 period EMA'
        )
        self.ema_50 = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=50, plotname='50 period EMA'
        )
        self.ema_crossover = bt.indicators.CrossOver(self.ema_20, self.ema_50)
        self.rsi = bt.indicators.RSI_Safe(self.data.close, period=5) # 3 period relative strength index
        
        # initialize previous 2 days rsi
        self.prev_rsi1 = 0
        self.prev_rsi2 = 0
        # store previous 2 days low
        self.prev_candle1_low = self.data.low[0]
        self.prev_candle2_low = self.data.low[-1]

    def next(self):

        # Open long position
        if self.position.size == 0:
            if self.rsi < 30 and self.rsi < self.prev_rsi1 and self.rsi < self.prev_rsi2: 
            # if self.ema_crossover > 0 and self.rsi < self.prev_rsi1 and self.rsi < self.prev_rsi2 and self.rsi < 30: 
                size = int(self.broker.getcash() / self.data) # going all in 
                print("Buy {} shares at {}".format(size, self.data.close[0]))
                self.buy(size=size) 

        # Close positions
        elif self.position.size > 0:
            if self.ema_crossover < 0:
                print("Selling all shares at {}".format(self.data.close[0]))
                self.close()
        
        # update previous lows + rsi
        self.prev_candle2_low = self.prev_candle1_low
        self.prev_candle1_low = self.data.low[-1]
        self.prev_rsi2 = self.prev_rsi1
        self.prev_rsi1 = self.rsi[0]