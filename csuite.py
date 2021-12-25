import pandas as pd
import json
from binance.client import Client
from datetime import datetime


# MISC SETUP & CONNECTION
def connect_client(file_name):
    # connect client function connects the binance client and allows for API fetching. It requires one input, a file_name,
    # which should direct to a formatted JSON file. It returns the Binance client.
    GLOBAL = open(file_name)
    GLOBAL = json.load(GLOBAL)
    client = Client(GLOBAL['API KEY'], GLOBAL['SECRET KEY'])
    return client


# SPOT DATA
def get_SpotKlines(client, symbol, interval):
    # download data from the Binance API
    # keys are stored in a JSON file and Timeseries ticker and scope is manual (for now)
    klines = client.get_klines(symbol=symbol, interval=interval, limit=1000)
    df = pd.DataFrame(klines)
    df.columns = [
        "timestamp", "open", "high", "low", "close", "volume", "closetime", "quote_av",
        "trades", "tb_base_ab", "tv_quote_av", "ignore"]

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]]
    for label in df.columns:
        df[label] = df[label].astype(float)
    # above lines parse the dataframe from download to ML format for our system
    return df


def batch_historic(client, symbols, interval, mode):
    frame = pd.DataFrame()
    for symbol in symbols:
        if mode == 'N':
            frame[symbol.replace('USDT', '')] = get_SpotKlines(client, symbol, interval)['close']
        elif mode == 'R':
            frame[symbol.replace('USDT', '')] = get_SpotKlines(client, symbol, interval)['close'].pct_change()
        elif mode == 'V':
            frame[symbol.replace('USDT', '')] = get_SpotKlines(client, symbol, interval)['close'].pct_change().rolling(7).std()
        else:
            print('ERROR: Invalid Mode Passed')
            break

    return frame


# FUTURES DATA
def get_FuturesKlines(client, symbol, interval):
    # download data from the Binance API
    # keys are stored in a JSON file and Timeseries ticker and scope is manual (for now)
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=1000)
    df = pd.DataFrame(klines)
    df.columns = [
        "timestamp", "open", "high", "low", "close", "volume", "closetime", "quote_av",
        "trades", "tb_base_ab", "tv_quote_av", "ignore"]

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]]
    for label in df.columns:
        df[label] = df[label].astype(float)
    # above lines parse the dataframe from download to ML format for our system
    return df


def get_FuturesSpread(client, symbol, interval):
    # function returns the futures to spot spread in % terms over the last 100 intervals
    # returns dataframe
    future = get_FuturesKlines(client, symbol, interval)
    spot = get_SpotKlines(client, symbol, interval)
    frame = pd.DataFrame()
    for label in future.columns:
        tmp_array = ((future[label] - spot[label])/spot[label])*100
        tmp_array = tmp_array.fillna(0)
        frame[label] = tmp_array

    frame = frame.drop('volume', axis=1)
    return frame


def get_FuturesOI(client, symbol, interval):
    # Returns timeseries frame with the futures open interest in specified interval
    frame = pd.DataFrame()
    tmp_a, tmp_b = [], []
    OI_dict = client.futures_open_interest_hist(symbol=symbol, period=interval, limit=500)
    for point in OI_dict:
        tmp_a.append(datetime.fromtimestamp(int(str(point['timestamp'])[:-3])).strftime("%d-%m-%Y"))
        tmp_b.append(point['sumOpenInterest'])
    frame['timestamp'] = tmp_a
    frame['OpenInterest'] = tmp_b
    frame['OpenInterest'] = pd.to_numeric(frame['OpenInterest'])
    frame = frame.set_index('timestamp')

    return frame


def get_LiveSpread(client, symbol):
    mp = float(client.futures_mark_price(symbol=symbol)['markPrice'])
    return ((mp - float(client.get_avg_price(symbol=symbol)['price']))/mp)*100

def get_FuturesLS(client, symbol, period):
    frame = pd.DataFrame()
    lsp = client.futures_top_longshort_position_ratio(symbol=symbol,period=period)
    la, sa, lsr, ts = [], [], [], []
    for entry in lsp:
        la.append(entry['longAccount'])
        lsr.append(entry['longShortRatio'])
        sa.append(entry['shortAccount'])
        ts.append(datetime.fromtimestamp(int(str(entry['timestamp'])[:-3])).strftime("%d-%m-%Y"))
    frame['timestamp'] = ts
    frame['longAccount'] = la
    frame['shortAccount'] = sa
    frame['longShortRatio'] = lsr
    frame = frame.set_index('timestamp')
    frame['longAccount'] = pd.to_numeric(frame['longAccount'])
    frame['shortAccount'] = pd.to_numeric(frame['shortAccount'])
    frame['longShortRatio'] = pd.to_numeric(frame['longShortRatio'])

    return frame


def get_FuturesFundingRate(client, ticker, period):
    data = client.futures_funding_rate(symbol=ticker, period=period)
    tmstp, fr = [], []
    frame = pd.DataFrame()
    for point in data:
        tmstp.append(datetime.fromtimestamp(int(str(point['fundingTime'])[:-3])).strftime("%d-%m-%Y"))
        fr.append(float(point['fundingRate']))
    frame['timestamp'] = tmstp
    frame['FundingRate'] = fr
    frame = frame.set_index('timestamp')
    frame['FundingRate'] = frame['FundingRate'] * 100

    return frame


# OPTIONS DATA
def get_options_skew(client, maturity, strikes):
    # This function returns the skew for BTC Vanilla options in easily readable CSV format
    cols = ['strike', 'direction', 'bidIV', 'askIV', 'delta', 'gamma', 'theta', 'vega']
    frame = pd.DataFrame(columns=cols)
    counter = 0
    for direction in ['C', 'P']:
        for strike in strikes:
            datapoint = client.options_mark_price(symbol="BTC-{}-{}-{}".format(maturity, strike, direction))
            tmp_frame = pd.DataFrame(datapoint['data'][0], index=[0])
            frame.loc[counter] = [strike, direction, tmp_frame['bidIV'].values[0], tmp_frame['askIV'].values[0], tmp_frame['delta'].values[0], tmp_frame['gamma'].values[0], tmp_frame['theta'].values[0], tmp_frame['vega'].values[0]]
            counter = counter + 1

    for label in cols:
        if label == 'direction':
            pass
        else:
            frame[label] = pd.to_numeric(frame[label], downcast="float")

    return frame


def get_omm_skew(client, maturities, strikes):
    data_array = []
    count = 0
    for expiry in maturities:
        data_array.append(get_options_skew(client, expiry, strikes[count]))
        count = count + 1
    return data_array

def IV_skew(data, price):
    IV_array = []
    for i in range(0,3):
        op_data = data[i]
        calls, puts  = op_data[op_data['direction'] == 'C'], op_data[op_data['direction'] == 'P']
        call_IV, put_IV = calls[calls.strike > price]['askIV'], puts[puts.strike <= price]['askIV']
        vol_skew = pd.DataFrame(columns=['IV'])
        count = 0
        for value in put_IV.values:
            vol_skew.loc[count] = value
            count = count + 1
        for value in call_IV.values:
            vol_skew.loc[count] = value
            count = count + 1
        vol_skew = vol_skew.set_index(op_data[op_data['direction']=='C'].strike)
        IV_array.append(vol_skew)
        return IV_array
