import backtrader as bt


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
