import pandas as pd
import CSuite.CSuite.BConnector.connector as connector
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import CSuite.CSuite.utils as Cutil


class TimeSeries:
    data = None
    client = None
    col = 'close'
    symbol = ''
    interval = ''

    def __init__(self, client, data=None):
        self.client = client
        self.data = data

    # passes data onto the timeSeries using the get_SpotKlines() function
    def download(self, symbol, interval):
        self.symbol = symbol
        self.interval = interval
        self.data = connector.get_SpotKlines(self.client, symbol, interval)
        return self

    # changes the col object used as the primary Timeseries from the OCHL frame
    def slice(self, col='close'):
        self.col = col
        return self

    # returns a summary statistic pandas data frame
    def summarize(self, period=365, pct=False):

        if pct:
            timeSeries = self.data[self.col]
            timeSeries = timeSeries.dropna()
        else:
            timeSeries = self.data[self.col]
            timeSeries = timeSeries.pct_change().dropna()

        downside = timeSeries[timeSeries.values < 0]
        sortino = ((timeSeries.mean()) * 365 - 0.01) / (downside.std() * np.sqrt(365))
        daily_draw_down = (timeSeries / timeSeries.rolling(center=False, min_periods=1, window=365).max()) - 1.0
        max_daily_draw_down = daily_draw_down.rolling(center=False, min_periods=1, window=365).min().min()
        calmar = round((timeSeries.mean() * 365) / abs(max_daily_draw_down.min()) * 100, 4)

        returnP = round(timeSeries[-period:].sum(), 4)
        stdP = round(timeSeries[-period:].std() * np.sqrt(365), 4)
        sharpeP = round(returnP / stdP, 4)

        skew = timeSeries.skew()
        kurt = timeSeries.kurtosis()

        frame = pd.DataFrame(columns=['Return', 'Volatility', 'Sharpe', 'Sortino',
                                      'MaxDrawDown', 'Calmar', 'Skew', 'Kurtosis'])
        frame.loc[0] = [round(returnP, 4) * 100, round(stdP, 4) * 100, round(sharpeP, 3), round(sortino, 3),
                        round(max_daily_draw_down, 3), round(calmar, 3), round(skew, 3), round(kurt, 3)]

        return frame

    # returns the annualised returns estimation using Linear Regression of Logarithmic Returns
    def lin_reg(self, period=365):
        timeSeries = self.data[self.col]
        timeSeries = timeSeries[-period:].pct_change().dropna()
        returns = (timeSeries.cumsum() * 100) + 100
        log_ts = np.log(returns)
        x = np.arange(len(log_ts))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_ts)
        annualized_slope = ((np.power(np.exp(slope), 365) - 1) * 100) * (r_value ** 2)

        return round(annualized_slope, 3)

    # returns a Pandas DataFrame with the average performed return by Month
    def seasonality(self):

        monthly = self.data.resample('BM')
        monthly = (monthly.last().close - monthly.first().open) / monthly.first().open

        monthly = monthly * 100
        frame = pd.DataFrame(data=list(zip(monthly.index, monthly.values)), columns=['timestamp', 'returns'])
        frame = frame.dropna()
        frame['positive'] = frame['returns'] > 0
        table = frame
        table['Month'] = [table.timestamp[i].month for i in range(0, len(table))]

        seasonality = []
        for i in range(1, 13):
            seasonality.append(table[table['Month'] == i].returns.mean())
        frame = pd.DataFrame()
        frame['seasonality'] = seasonality
        frame['positive'] = frame['seasonality'] > 0
        frame['months'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        return frame

    # returns plot of autocorrelation for specified lags
    def autocorrelation(self, period=365, lags=50, diff=False):
        from statsmodels.tsa.stattools import acf
        if diff:
            return acf(self.data[self.col][-period:].diff().dropna(), nlags=lags)
        else:
            return acf(self.data[self.col][-period:], nlags=lags)

    # returns a Pandas DataFrame with the results of the AD-Fuller test
    def adfuller(self, maxlag=5, mode='N', regression='c'):
        from statsmodels.tsa.stattools import adfuller
        if mode == 'N':
            adf = adfuller(self.data['close'], maxlag=maxlag, regression=regression)
        elif mode == 'L':
            adf = adfuller(np.log(self.data['close']), maxlag=maxlag, regression=regression)
        else:
            return False
        df = pd.DataFrame(columns=['adf', 'p-value', 'lags', 'NObs', 'cv_1%', 'cv_5%', 'cv_10%', 'ic'])
        ks = list(adf[0:4]) + list(adf[4].values()) + [adf[5]]
        df.loc[0] = ks

        return df


class Plotter:
    timeSeries = TimeSeries
    path = ''

    def __init__(self, timeSeries, path=''):
        self.timeSeries = timeSeries

    # Returns a basic timeseries plot with either Price, Return or Volatility
    def plot(self, period=365, mode='N', col='close', save=False):
        plt.clf()
        fig, ax = plt.subplots()
        if mode == 'N':
            ax.set_title('Price of {}'.format(self.timeSeries.symbol))
            ax.set_ylabel('Price ($ per unit)')
            ax.set_xlabel('Time (Days)')
            ax.plot(self.timeSeries.data[col][-period:])

        elif mode == 'R':
            ax.set_title('Cumulative Return of {}'.format(self.timeSeries.symbol))
            ax.set_ylabel('Return (%)')
            ax.set_xlabel('Time (Days)')
            ax.plot(self.timeSeries.data[col][-period:].pct_change().cumsum() * 100)
            ax.axhline(0, color='black', linewidth=1, linestyle='--')

        elif mode == 'V':
            ax.set_title('7-Day Rolling Volatility for {}'.format(self.timeSeries.symbol))
            ax.set_ylabel('7-Day Rolling Std (%)')
            ax.set_xlabel('Time (Days)')
            ax.plot(self.timeSeries.data[col][-period:].pct_change().cumsum().rolling(7).std() * 100)
            ax.axhline(0, color='black', linewidth=1, linestyle='-')

        plt.show()
        if save:
            plt.savefig('{}timeseries_{}.jpg'.format(self.path, self.timeSeries.symbol), dpi=800)

    # Returns a Quartile-Quantile Plot for either returns or volatility distributions
    def plot_qq(self, period=365, mode='R', save=False):
        plt.clf()
        fig = plt.figure()
        ax = fig.add_subplot()
        if mode == 'R':
            stats.probplot(self.timeSeries.data[self.timeSeries.col].pct_change()[-period:], dist='norm', plot=ax)
        elif mode == 'V':
            stats.probplot(self.timeSeries.data[self.timeSeries.col].pct_change()[-period:].rolling(7).std() * 100,
                           dist="norm", plot=ax)
        ax.set_title('Quantile-Quartile Plot for {} Return Distribution'.format(self.timeSeries.symbol))
        ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
        ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
        plt.show()
        if save:
            plt.savefig('{}QQPlot_{}.jpg'.format(self.path, self.timeSeries.symbol), dpi=800)

    # Returns the seasonality bar plot
    def plot_seasonality(self, save=False):
        frame = self.timeSeries.seasonality()
        plt.clf()
        fig, ax = plt.subplots()
        ax.axhline(0, color='black', linewidth=1)
        ax.bar(x=frame['months'], height=frame['seasonality'], color=frame.positive.map({True: 'g', False: 'r'}),
               edgecolor='black')
        ax.set_title('Seasonality Plot for {}'.format(self.timeSeries.symbol))
        ax.set_xlabel('Months')
        ax.set_ylabel('Average Monthly Return (%)')

        for i in range(0, 12):
            h = 0.5
            if frame['positive'][i]:
                h = -0.5
            text = ax.text(frame['months'][i], h,
                           str(round(frame['seasonality'][i], 1)) + '%', ha="center", va="center", color="black",
                           fontsize=8)

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        if save:
            plt.savefig('{}seasonality_{}.jpg'.format(self.path, self.timeSeries.symbol), dpi=800)

    # Plots autocorrelation or differencing for specified lags
    def plot_acf(self, period=365, lags=50, diff=False, save=False):
        plt.clf()
        fig, ax = plt.subplots()
        acf = self.timeSeries.autocorrelation(period=period, diff=diff, lags=lags)
        ax.stem(acf, use_line_collection=True, linefmt='C0-', basefmt='C7-', markerfmt='C1*')
        if diff:
            ax.set_title('Autocorrelation Differencing for 50 lags')
        else:
            ax.set_title('Autocorrelation Chart for 50 lags')
        ax.set_ylabel('Correlation Coefficient')
        ax.set_xlabel('Lags (n)')
        plt.tight_layout()
        if save:
            plt.savefig('{}acf_{}.jpg'.format(self.path, self.timeSeries.symbol), dpi=800)

    # Plots against a benchmark
    def benchmark(self, benchmark='BTCUSDT', period=365, delta=False, save=False):
        plt.clf()
        benchmark = TimeSeries(self.timeSeries.client).download(benchmark, self.timeSeries.interval)
        frame = pd.DataFrame()
        frame['data'] = self.timeSeries.data[self.timeSeries.col][-period:].pct_change().dropna().cumsum() * 100
        frame['bench'] = benchmark.data[self.timeSeries.col][-period:].pct_change().dropna().cumsum() * 100
        frame['delta'] = frame['data'] - frame['bench']
        fig, ax = plt.subplots()
        if delta is False:
            ax.plot(frame['data'], color='r', label=self.timeSeries.symbol)
            ax.plot(frame['bench'], color='b', label=benchmark.symbol)
        else:
            ax.plot(frame['delta'], color='r', label='Comparative Performance')
        ax.axhline(0, linewidth=1, linestyle='-', color='black')
        ax.set_title('Benchmarking Plot')
        ax.set_xlabel('Time (Days)')
        ax.set_ylabel('Return (%)')
        plt.legend()
        if save:
            plt.savefig('{}bench_{}.jpg'.format(self.path, self.timeSeries.symbol), dpi=800)


class Spread(TimeSeries):

    def __init__(self, data):
        super().__init__(None, data)
        self.slice('spread')

    def johansen(self, maxLags):
        from statsmodels.tsa.vector_ar.vecm import coint_johansen

        # uses https://nbviewer.jupyter.org/github/mapsa/seminario-doc-2014/blob/master/cointegration-
        # example.ipynb to create functions to return the number of cointegrating vectors based
        # on the Trace version if the Johansen Cointegration Test
        def johansen_trace(y, p):
            N, l = y.shape
            joh_trace = coint_johansen(y, 0, p)
            r = 0
            for i in range(l):
                if joh_trace.lr1[i] > joh_trace.cvt[i, 1]:     # 0: 90%  1:95% 2: 99%
                    r = i + 1
            joh_trace.r = r

            return joh_trace

        # loops through 1 to 10 lags of trading days trading days
        columns_gen = list(self.data.columns)
        columns_gen.remove('spread')
        for i in range(1, maxLags):
            # tests for cointegration at i lags
            joh_trace = johansen_trace(self.data[columns_gen], i)
            # prints the results
            print('Using the Trace Test, there are', joh_trace.r, '''cointegrating vectors at %s lags between the specified pair''' % i)
            # prints a space for readability
            print()

    def VCEM_forecast(self, periods, lags, coints, backtest=False, confi=0.05, determ='ci'):
        # import vector error correction model from statsmodels
        from statsmodels.tsa.vector_ar.vecm import VECM
        # if backtest then it excludes historic data for the forecast period such that the VCEM
        # quality can be verified.
        columns_gen = list(self.data.columns)
        columns_gen.remove('spread')

        if backtest:
            ex_data = self.data[:-periods]
        else:
            ex_data = self.data
        # setup & fit the data
        vcem = VECM(endog=ex_data[columns_gen], k_ar_diff=lags, coint_rank=coints, deterministic=determ)
        vcem = vcem.fit()
        forecast = vcem.predict(periods, confi)
        # create array of DataFrames with estimations
        datums = []
        for k in range(0, len(columns_gen)):
            cols = ['Mid', 'Low', 'High']
            frame = pd.DataFrame(columns=cols)
            for i in range(0, 3):
                tmp = pd.DataFrame(forecast[i])
                frame[cols[i]] = tmp[k] * 100
            datums.append(frame)
        # create array of the implied spread estimations
        implied_spread = datums[0] - datums[1]

        return implied_spread


class Pair:
    symbols = []
    client = None
    data = None
    interval = ''
    spread = None

    def __init__(self, client, symbols, interval, download=True):
        self.client = client
        self.symbols = symbols
        self.interval = interval
        if download:
            self.download(client, symbols, interval)

    def load_data(self, data, interval):
        self.data = data
        self.interval = interval
        return self

    def download(self, client, symbols, interval):
        self.data = connector.batch_historic(client, symbols, interval, 'N')
        return self

    def get_spread(self):
        tmp = self.data.pct_change()
        tmp['spread'] = tmp[tmp.columns[0]] - tmp[tmp.columns[1]]
        spr = Spread(tmp.dropna())
        return spr

    def VCEM_backtest(self, lags, coint, periods=2, start=100, determ='ci'):
        import warnings
        warnings.simplefilter(action='ignore')
        data = self.data

        results = pd.DataFrame(columns=['Low', 'Mid', 'High'])
        for i in range(start, len(data), periods):
            Cutil.progress(i, len(data), status='')
            tmp_pair = Pair(self.client, self.symbols, '', False)
            tmp_pair = tmp_pair.load_data(data[:i], '')
            tmp_spread = tmp_pair.get_spread()

            results = results.append(tmp_spread.VCEM_forecast(periods, lags, coint, False, 0.05, determ))

        results.index = data[start:].index
        results['spread'] = self.get_spread().data['spread']

        return results
