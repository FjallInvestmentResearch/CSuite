from CTrader import connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def portfolio_simulation(client, tickers, num_portfolios=15000, risk_free_rate=0.01614):

    def portfolio_annualised_performance(weights, mean_returns, cov_matrix, risk_free_rate, sortino, calmar):
        returns = np.sum(mean_returns*weights) * 252
        std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        beta = 0
        treynor_ratio = (returns-risk_free_rate)/beta
        short_interest_ratio = 0
        sortino_ratio = np.sum(sortino*weights)
        calmar = np.sum(calmar*weights)
        weights_out = list(weights)
        sharpe_ratio = (returns-risk_free_rate)/std

        return [weights_out, returns, std, sharpe_ratio, beta, treynor_ratio, sortino_ratio, short_interest_ratio, calmar]

    frame = pd.DataFrame(columns=['timestamp', 'ticker', 'close'])
    np.random.seed(777)

    for stock in tickers:
        series = connector.get_SpotKlines(client, stock, '1d')
        series = series.drop(['open', 'high', 'low', 'volume'], axis=1)
        tmp_ticker = [stock for i in range(len(series['close']))]
        series.insert(0, 'timestamp', series.index)
        series.insert(1, 'ticker', tmp_ticker)
        frame = frame.append(series, ignore_index=True)

    # runs the efficient frontier theory portfolio allocation
    df = frame.set_index('timestamp')
    table = df.pivot(columns='ticker')
    table.columns = [col[1] for col in table.columns]

    # get special tables & set simulation size & risk free rate
    returns = table.pct_change()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    num_equities = len(tickers)

    # generate downside volatility metrics
    sortino = []
    calmar = []
    for i in range(0, num_equities):

        downside_returns = returns.loc[returns[tickers[i]] < 0]
        sortino.append(((returns[tickers[i]].mean()*252)-risk_free_rate)/(downside_returns.std()*np.sqrt(252)))
        daily_draw_down = (returns[tickers[i]]/returns[tickers[i]].rolling(center=False, min_periods=1, window=252).max())-1.0
        max_daily_draw_down = daily_draw_down.rolling(center=False, min_periods=1, window=252).min()
        calmar.append((returns[tickers[i]].mean()*252)/abs(max_daily_draw_down.min()))

    portfolio_data = pd.DataFrame(columns=['Weights', 'Return', 'Volatility', 'Sharpe', 'Beta', 'Treynor',
                                           'Sortino', 'SIR', 'Calmar'])

    weights_record = []
    # get weights and return
    for i in range(num_portfolios):
        weights = np.random.random(num_equities)
        weights /= np.sum(weights)
        weights_record.append(weights)

        portfolio_data.loc[i] = portfolio_annualised_performance(weights, mean_returns, cov_matrix, risk_free_rate, sortino, calmar)

    return portfolio_data


def calc_portfolio_eft(portfolio_data, limit=5, plot=True, save=True, path=''):
    frame = portfolio_data.sort_values(by='Sharpe', ascending=False)
    new_frame = frame.head(limit)
    new_frame = new_frame.reset_index(inplace=False)

    if plot:

        plt.figure(figsize=(10, 7))
        plt.scatter(frame['Volatility'], frame['Return'], c=frame['Sharpe'], cmap='YlGnBu', marker='o', s=10, alpha=0.3)

        plt.scatter(new_frame.iloc[0]['Volatility'], new_frame.iloc[0]['Return'], marker='*', color='r', s=500)
        plt.scatter(new_frame.iloc[1]['Volatility'], new_frame.iloc[1]['Return'], marker='*', color='g', s=500)
        plt.scatter(new_frame.iloc[2]['Volatility'], new_frame.iloc[2]['Return'], marker='*', color='b', s=500)
        plt.scatter(new_frame.iloc[3]['Volatility'], new_frame.iloc[3]['Return'], marker='*', color='y', s=500)
        plt.scatter(new_frame.iloc[4]['Volatility'], new_frame.iloc[4]['Return'], marker='*', color='c', s=500)

        plt.colorbar()
        plt.title('Simulated Portfolio Optimization based on Efficient Frontier')
        plt.xlabel('Expected Annualised Volatility (%)')
        plt.ylabel('Expected Annualised Returns (%)')
        plt.show()
        if save:
            plt.savefig('{}EFT.png'.format(path), dpi=800)

    return new_frame
