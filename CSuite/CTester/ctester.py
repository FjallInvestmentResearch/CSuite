import backtrader as bt


# Built in indicators that add functionality beyond the basics of backtrader

# Money Flow Indicator
# Retrieved through BackTrader recopies
# https://www.backtrader.com/recipes/indicators/mfi/mfi/
# https://school.stockcharts.com/doku.php?id=technical_indicators:money_flow_index_mfi
class MFI(bt.Indicator):
    lines = ('mfi',)
    params = dict(period=14)

    alias = ('MoneyFlowIndicator',)

    def __init__(self):
        tprice = (self.data.close + self.data.low + self.data.high) / 3.0
        mfraw = tprice * self.data.volume

        flowpos = bt.ind.SumN(mfraw * (tprice > tprice(-1)), period=self.p.period)
        flowneg = bt.ind.SumN(mfraw * (tprice < tprice(-1)), period=self.p.period)

        mfiratio = bt.ind.DivByZero(flowpos, flowneg, zero=100.0)
        self.l.mfi = 100.0 - 100.0 / (1.0 + mfiratio)


# Stochastic RSI
class StochRSI(bt.Indicator):
    lines = ('stochrsi',)
    params = dict(
        period=14,  # to apply to RSI
        pperiod=None,  # if passed apply to HighestN/LowestN, else "period"
    )

    def __init__(self):
        rsi = bt.ind.RSI(self.data, period=self.p.period)

        pperiod = self.p.pperiod or self.p.period
        maxrsi = bt.ind.Highest(rsi, period=pperiod)
        minrsi = bt.ind.Lowest(rsi, period=pperiod)

        self.l.stochrsi = (rsi - minrsi) / (maxrsi - minrsi)


# Chaikin Money Flow
# Reference: https://backtest-rookies.com/2018/06/29/backtrader-chaikin-money-flow-indicator/
class ChaikinMoneyFlow(bt.Indicator):
    lines = ('money_flow',)
    params = (('len', 20),)
    plotlines = dict(money_flow=dict(_name='CMF', color='green', alpha=0.50))

    def __init__(self):
        # Let the indicator get enough data
        self.addminperiod(self.p.len)
        # Plot horizontal Line
        self.plotinfo.plotyhlines = [0]
        # Aliases to avoid long lines
        c = self.data.close
        h = self.data.high
        l = self.data.low
        v = self.data.volume
        self.data.ad = bt.If(bt.Or(bt.And(c == h, c == l), h == l), 0, ((2 * c - l - h) / (h - l)) * v)
        self.lines.money_flow = bt.indicators.SumN(self.data.ad, period=self.p.len) / bt.indicators.SumN(
            self.data.volume, period=self.p.len)


# Volume Oscillator
# Reference: https://www.tradingview.com/chart/n3x6FXov/?symbol=BITSTAMP%3ABTCUSD&solution=43000591350
class VolumeOscillator(bt.Indicator):
    lines = ('volume_oscillator',)
    params = dict(
        fast=14,  # to apply to RSI
        slow=28,  # if passed apply to HighestN/LowestN, else "period"
    )

    def __init__(self):
        self.fastVO = bt.indicators.SMA(self.data.volume, period=self.p.fast)
        self.slowVO = bt.indicators.SMA(self.data.volume, period=self.p.slow)
        self.l.volume_oscillator = 100 * (self.fastVO - self.slowVO) / self.slowVO


# Klinger Volume Oscillator
# Reference: https://backtest-rookies.com/2018/05/18/backtrader-klinger-volume-oscillator/
class KlingerOsc(bt.Indicator):
    lines = ('sig', 'kvo')
    params = dict(
        kvoFast=34,
        kvoSlow=55,
        sigPeriod=13,
    )

    def __init__(self):
        self.plotinfo.plotyhlines = [0]
        self.addminperiod(55)
        self.data.hlc3 = (self.data.high + self.data.low + self.data.close) / 3
        self.data.sv = bt.If((self.data.hlc3(0) - self.data.hlc3(-1)) / self.data.hlc3(-1) >= 0, self.data.volume,
                             -self.data.volume)
        self.lines.kvo = bt.indicators.EMA(self.data.sv, period=self.p.kvoFast) - bt.indicators.EMA(self.data.sv,
                                                                                                    period=self.p.kvoSlow)
        self.lines.sig = bt.indicators.EMA(self.lines.kvo, period=self.p.sigPeriod)


# Schaff Trend Cycle
class SchaffTrendCycle(bt.Indicator):

    lines = ('schaff','macd','f1','f2','pf')

    params = (
        ('fast', 23),
        ('slow', 50),
        ('cycle', 10),
        ('factor', 0.5)
    )

    plotinfo = dict(
        plot=True,
        plotname='Schaff Trend Cycle',
        subplot=True,
        plotlinelabels=True)

    plotlines = dict(macd=dict(_plotskip=True, ),
                     f1=dict(_plotskip=True, ),
                     f2=dict(_plotskip=True, ),
                     pf=dict(_plotskip=True, ),
                     )

    def __init__(self):
        # Plot horizontal Line
        self.plotinfo.plotyhlines = [25,75]


        self.addminperiod(self.p.slow)
        self.l.macd = bt.indicators.MACD(self.data,period_me1=self.p.fast,period_me2=self.p.slow)

    def prenext(self):

        self.l.f1[0] = self.data.close[0]
        self.l.pf[0] = self.data.open[0]
        self.l.f2[0] = self.data.high[0]
        self.l.schaff[0] = self.data.low[0]

    def next(self):

        v1 = min(self.l.macd.get(size=self.p.cycle))
        v2 = max(self.l.macd.get(size=self.p.cycle))-v1

        self.l.f1[0] = 100*(self.l.macd[0]-v1)/v2 if v2 > 0 else self.l.f1[-1]
        self.l.pf[0] = self.l.pf[-1] + (self.p.factor*(self.l.f1[0]-self.l.pf[-1]))

        v3 = min(self.l.pf.get(size=self.p.cycle))
        v4 = max(self.l.pf.get(size=self.p.cycle))-v3

        self.l.f2[0] = 100*(self.l.pf[0]-v3)/v4 if v4 > 0 else self.l.f2[-1]
        self.l.schaff[0] = self.l.schaff[-1] + (self.p.factor*(self.l.f2[0]-self.l.schaff[-1]))


# VWAP Indicator
class VolumeWeightedAveragePrice(bt.Indicator):
    plotinfo = dict(subplot=False)

    params = (('period', 30), ('mult', 0.025) )

    alias = ('VWAP', 'VolumeWeightedAveragePrice',)
    lines = ('VWAP','low', 'high')
    plotlines = dict(VWAP=dict(alpha=0.50, linestyle='-.', linewidth=2.0), low=dict(alpha=0.50, linestyle='-.', linewidth=2.0), high=dict(alpha=0.50, linestyle='-.', linewidth=2.0))



    def __init__(self):
        # Before super to ensure mixins (right-hand side in subclassing)
        # can see the assignment operation and operate on the line
        cumvol = bt.ind.SumN(self.data.volume, period = self.p.period)
        typprice = ((self.data.close + self.data.high + self.data.low)/3) * self.data.volume
        cumtypprice = bt.ind.SumN(typprice, period=self.p.period)
        self.lines[0] = cumtypprice / cumvol
        vol = bt.indicators.SumN((self.data.close - (cumtypprice / cumvol))**2, period=self.p.period)
        vol = ((1/self.p.period)*vol)**0.5

        self.lines[1] = self.lines[0] - (vol*(1+self.p.mult))
        self.lines[2] = self.lines[0] + (vol*(1+self.p.mult))

        super(VolumeWeightedAveragePrice, self).__init__()


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
            self.buy(size=(self.params.order_size / self.data.close), trailpercent=5, exectype=bt.Order.StopLimit)

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
        self.MFI = MFI(period=self.params.rsi_period)
        self.SRSI = StochRSI(period=self.params.rsi_period)

    def next(self):
        # BUY LOGIC
        if self.RSI > 50 + self.params.rsi_bandwidth and self.data.close > self.SMA:
            self.buy(size=(self.params.order_size / self.data.close), trailpercent=5, exectype=bt.Order.StopLimit)

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


# Dollar Cost Averaging Strategy.
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
            self.buy(size=(self.params.order_size / self.data.close))
