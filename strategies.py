import backtrader as bt
import indicators

# Proprietary Backtrader Strategies for use with CTester


# Three-X-Trend: Trend Following. Uses RSI and SMA to buy into a trend
class ThreeXTrend(bt.Strategy):
    params = (
        ('rsi_period', None),
        ('sma_period', None),
        ('order_size', None),
        ('rsi_bandwidth', None)
    )

    def __init__(self):
        self.RSI = bt.indicators.RSI(self.data.close, period=self.params.rsi_period, safediv=True)
        self.SMA = bt.indicators.SMA(self.data.close, period=self.params.sma_period)

    def next(self):
        # BUY LOGIC
        if self.RSI > 50 + self.params.rsi_bandwidth and self.data.close > self.SMA:
            self.buy(size=(self.params.order_size/self.data.close), trailpercent=5, exectype=bt.Order.StopLimit)

        # SELL LOGIC
        elif self.RSI < 50 - self.params.rsi_bandwidth and self.data.close < self.SMA:
            self.close()


# Triple Confluence Indicator: Trend Following. Uses RSI, SMA, MFI and SRSI to find and close a trend following trade.
class TripleCCP(bt.Strategy):
    params = (
        ('rsi_period', None),
        ('sma_period', None),
        ('order_size', None),
        ('rsi_bandwidth', None)
    )

    def __init__(self):
        self.RSI = bt.indicators.RSI(self.data.close, period=self.params.rsi_period, safediv=True)
        self.SMA = bt.indicators.SMA(self.data.close, period=self.params.sma_period)
        self.MFI = indicators.MFI(period=self.params.rsi_period)
        self.SRSI = indicators.StochRSI(period=self.params.rsi_period)

    def next(self):
        # BUY LOGIC
        if self.RSI > 50 + self.params.rsi_bandwidth and self.data.close > self.SMA:
            self.buy(size=(self.params.order_size/self.data.close), trailpercent=5, exectype=bt.Order.StopLimit)

        # SELL LOGIC
        elif self.RSI > 70 and self.MFI > 70 and self.SRSI > 0.70:
            self.close()
        elif self.RSI < 50 - self.params.rsi_bandwidth or self.data.close < self.SMA:
            self.close()


# Moving Average Crossover Strategy: Trend Following.
class CrossoverStrategy(bt.Strategy):
    # parameters (change to import via text file)
    params = dict(fast_period=15, slow_period=5, signal_period=10)

    # Logging Function
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # initialize startegy by defining indicators using Backtrader built-in functions
        self.dataclose = self.datas[0].close
        self.fast_ma = bt.indicators.EMA(self.data.close, period=self.p.fast_period)
        self.slow_ma = bt.indicators.EMA(self.data.close, period=self.p.slow_period)
        self.macd_line = self.fast_ma - self.slow_ma
        self.signal_line = bt.indicators.EMA(self.macd_line, period=self.p.signal_period)
        self.macd_crossover = bt.indicators.CrossOver(self.macd_line, self.signal_line)

    def next(self):
        # Continous startegy, changing with MACD crossover
        if self.macd_crossover > 0:
            self.close()  # close short position
            self.buy()  # enter long position
            self.log('BUY, %.2f' % self.dataclose[0])
        elif self.macd_crossover < 0:
            self.close()  # close long position
            self.sell()  # enter short position
            self.log('SELL, %.2f' % self.dataclose[0])


class DCAStartegy(bt.Strategy):
    params = (
        ('rsi_period', 7),
        ('rsi_signal', 30),
        ('order_size', 100)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.RSI = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

    def next(self):
        if self.RSI < self.params.rsi_signal:
            self.buy(size=(self.params.order_size/self.data.close))