import pandas as pd
import CSuite.CSuite.BConnector as connector
import numpy as np


class Portfolio:
    symbols, weights = [], []
    data = pd.DataFrame()
    risk_free_rate = 0
    benchmark = ''

    def __init__(self, client, symbols, weights=None, interval='1d', download=True):
        if weights is None:
            weights = [1 / len(symbols)] * len(symbols)
        self.symbols, self.weights = symbols, weights
        if download:
            self.data = connector.batch_historic(client, symbols, interval, 'N')

    def get_timeseries(self, period=365):
        sub_frame = self.data[-period:].pct_change()
        cols = self.data.columns
        tmp = self.data[cols[0]]*self.weights[0]
        for i in range(1, len(self.symbols)):
            tmp = (sub_frame[cols[i]]*self.weights[i])
        return tmp

    def load_data(self, data):
        self.data = data
        return self

    def get_data(self):
        return self.data

    def summarize(self):

        returns = self.data.pct_change()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()
        frame = pd.DataFrame()

        returns = np.sum(mean_returns*self.weights) * 365
        std = np.sqrt(np.dot(np.array(self.weights).T, np.dot(cov_matrix, self.weights))) * np.sqrt(365)
        sharpe_ratio = round((returns-self.risk_free_rate)/std, 4)
        frame['Weights'] = [self.weights]
        frame['ExpectedReturns'] = [round(returns, 4)]
        frame['ExpectedVol'] = [round(std, 4)]
        frame['ExpectedSharpe'] = [sharpe_ratio]

        timeseries = self.get_timeseries(len(self.data)-1)
        downside = timeseries[timeseries.values < 0]
        sortino = ((timeseries.mean()) * 365 - 0.01)/(downside.std()*np.sqrt(365))
        daily_draw_down = (timeseries/timeseries.rolling(center=False, min_periods=1, window=365).max())-1.0
        max_daily_draw_down = daily_draw_down.rolling(center=False, min_periods=1, window=365).min().min().round(4)
        calmar = round((timeseries.mean()*365)/abs(max_daily_draw_down.min())*100, 4)
        frame['Sortino'] = [sortino.round(4)]
        frame['MaxDrawDown'] = [max_daily_draw_down]
        frame['Calmar'] = [calmar]

        returnp = round(timeseries[-365:].sum(), 4)
        stdp = round(timeseries[-365:].std()*np.sqrt(365), 4)
        sharpep = round(returnp/stdp, 4)
        frame['PerformedReturn'] = returnp
        frame['PerformedVol'] = stdp
        frame['PerformedSharpe'] = sharpep

        return frame


class MonteCarlo:

    np.random.seed(777)
    symbols = []
    client = None
    frame = pd.DataFrame()

    def __init__(self, client, symbols):
        self.symbols = symbols
        self.client = client

    def run(self, runs=5000):
        import_data = Portfolio(self.client, self.symbols, None, '1d', True).get_data()
        datums = []
        for i in range(1, runs):
            weights = np.random.random(len(self.symbols))
            weights /= np.sum(weights)
            datums.append(list(Portfolio(self.client, self.symbols, weights, '1d', False)
                                    .load_data(import_data).summarize().values[0]))
        frame = pd.DataFrame(columns=['Weights', 'ExpectedReturns', 'ExpectedVol', 'ExpectedSharpe',
                                      'Sortino', 'MaxDrawDown', 'Calmar', 'PerformedReturn', 'PerformedVol',
                                      'PerformedSharpe'], data=datums)
        self.frame = frame
        return self

    def eft(self):
        return self.frame.sort_values(by='ExpectedSharpe', ascending=False).head(5)
