import pandas as pd
import CSuite.CSuite.BConnector as connector
import numpy as np
import scipy.stats as stats


class TimeSeries:
    data = None
    client = None
    col = 'close'
    symbol = None

    def __init__(self, client, data=None):
        self.client = client
        self.data = data

    # populates object 'data' field with OCHL retrieval from connector
    def download(self, symbol, interval):
        self.symbol = symbol
        self.data = connector.get_SpotKlines(self.client, symbol, interval)
        return self

    # enables user access to the data for validation
    def get_data(self):
        return self.data

    # changes the slice column used to turn OCHL into a timeseries
    def slice(self, col='close'):
        self.col = col
        return self

    # returns pandas frame of summary statistics for the timeseries
    def summarize(self, period=365):
        timeSeries = self.data[self.col]
        timeSeries = timeSeries[-period:].pct_change()
        downside = timeSeries[timeSeries.values < 0]
        sortino = ((timeSeries.mean()) * 365 - 0.01)/(downside.std()*np.sqrt(365))
        daily_draw_down = (timeSeries/timeSeries.rolling(center=False, min_periods=1, window=365).max())-1.0
        max_daily_draw_down = daily_draw_down.rolling(center=False, min_periods=1, window=365).min().min().round(4)
        calmar = round((timeSeries.mean()*365)/abs(max_daily_draw_down.min())*100, 4)

        returns = round(timeSeries[-365:].sum(), 4)
        stds = round(timeSeries[-365:].std()*np.sqrt(365), 4)
        sharpe = round(returns/stds, 4)

        skew = self.data[self.col].pct_change().skew()
        kurt = self.data[self.col].pct_change().kurtosis()

        frame = pd.DataFrame(columns = ['Return', 'Volatility', 'Sharpe', 'Sortino',
                                        'MaxDrawDown', 'Calmar', 'Skew', 'Kurtosis'])
        frame.loc[0] = [round(returns, 4)*100, round(stds, 4)*100, round(sharpe, 3), round(sortino, 3),
                        round(max_daily_draw_down, 3), round(calmar, 3), round(skew, 3), round(kurt, 3)]

        return frame

    # returns linear regression slope done through logarithmic normalisation
    def lin_reg(self, period=365):
        timeSeries = self.data[self.col]
        timeSeries = timeSeries[-period:].pct_change().dropna()
        returns = (timeSeries.cumsum()*100)+100
        log_ts = np.log(returns)
        x = np.arange(len(log_ts))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_ts)
        annualized_slope = ((np.power(np.exp(slope), 365) - 1) * 100) * (r_value ** 2)

        return round(annualized_slope, 3)

    # returns autocorrelation series for lags
    def autocorrelation(self, period=365, lags=50, diff=False):
        from statsmodels.tsa.stattools import acf
        if diff:
            return acf(self.data[self.col][-period:].diff().dropna(), nlags=lags)
        else:
            return acf(self.data[self.col][-period:], nlags=lags)

    # AD-Fuller test result dataframe
    def adfuller(self):
        from statsmodels.tsa.stattools import adfuller
        adf = adfuller(self.data['close'])
        df = pd.DataFrame(columns=['adf', 'p-value', 'lags', 'NObs', 'cv_1%', 'cv_5%', 'cv_10%', 'ic'])
        ks = list(adf[0:4]) + list(adf[4].values()) + [adf[5]]
        df.loc[0] = ks

        return df
