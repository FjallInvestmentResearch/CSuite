import pandas as pd
import connector


def get_trade_history(client, symbol):
    trades = client.get_my_trades(symbol='{}'.format(symbol))
    cols = ['time', 'symbol', 'id', 'price', 'qty', 'quoteQty', 'commission', 'commissionAsset', 'isBuyer', 'isMaker']
    tags = ['Time', 'Symbol', 'ID', 'Price', 'Qty', 'Cost', 'Commission', 'CAsset', 'Side', 'isMaker']
    # Time, Symbol, ID, Price, Qty, Cost, Commission (USD), Side
    order_hist = []
    for order in trades:
        datum = []
        for item in cols:
            datum.append(order[item])
        order_hist.append(datum)

    data = pd.DataFrame(order_hist, columns=tags)
    data.Time = pd.to_datetime(data.Time, unit="ms")
    data.ID = data.ID
    data.Price = pd.to_numeric(data.Price)
    data.Qty = pd.to_numeric(data.Qty)
    data.Cost = pd.to_numeric(data.Cost)
    data.Commission = pd.to_numeric(data.Commission)

    commission, side = [], []
    for i in range(0,len(data.index)):
        if data.CAsset.iloc[i] == 'USDT':
            if data.isMaker.iloc[i] is True:
                commission.append(data.Commission.iloc[i])
            else:
                commission.append(-data.Commission.iloc[i])
        else:
            if data.isMaker.iloc[i] is True:
                commission.append(data.Commission.iloc[i] * data.Price.iloc[i])
            else:
                commission.append(-(data.Commission.iloc[i] * data.Price.iloc[i]))
    for j in range(0,len(data.index)):

        if data.Side.iloc[j]:
            side.append('BUY')
        else:
            side.append('SELL')

    data['Commission'] = commission
    data['Side'] = side

    data = data.drop(labels=['CAsset', 'isMaker'], axis=1)

    return data


def adjust_fx_trades(client, symbol):
    data_array = []
    currencies = ['USDT', 'EUR']
    # check available currency order history
    for currency in currencies:
        try:
            data_array.append(get_trade_history(client, '{}{}'.format(symbol, currency)))
        except:
            data_array.append(pd.DataFrame(columns=['Time', 'Symbol', 'ID', 'Price', 'Qty', 'Cost', 'Commission', 'Side']))
    # get FOREX rate to pass into conversion
    forex_rate = connector.get_SpotKlines(client, '{}USDT'.format(currencies[1]), '1d')
    spec_array, com = [], []
    # convert FX rate
    for i in range(0, len(data_array[1])):
        spec_array.append(data_array[1].iloc[i].Price * forex_rate[forex_rate.index == data_array[1].Time.iloc[i].strftime('%Y-%m-%d')].close.iloc[0])
        com.append(data_array[1].iloc[i].Commission * forex_rate[forex_rate.index == data_array[1].Time.iloc[i].strftime('%Y-%m-%d')].close.iloc[0])

    data_array[1]['Price'] = spec_array
    data_array[1]['Commission'] = com
    data_array[1]['Cost'] = data_array[1]['Price'] * data_array[1]['Qty']
    data = data_array[0]
    data = data.append(data_array[1])
    data['adjCost'] = data['Cost'] + data['Commission']

    return data


def get_asset_status(client, symbol):

    orders = adjust_fx_trades(client, symbol)
    data = pd.DataFrame()

    BUY = orders[orders.Side == 'BUY']
    SELL = orders[orders.Side == 'SELL']

    # order symbol
    data['Symbol'] = [symbol]
    # Active Order Quantity
    data['Qty'] = BUY['Qty'].sum() - SELL['Qty'].sum()
    # Active WAP
    data['WAP'] = round(sum(BUY.Price * (BUY.Qty/BUY.Qty.sum())), 8)
    # Cost of active LS
    data['CostBasis'] = round((data['WAP'] * data['Qty']), 8)
    # total trading cost in USD
    data['Commission'] = orders.Commission.sum()

    # Live Quote
    if symbol != 'USDT':
        data['MarketPrice'] = round(float(client.get_avg_price(symbol='{}USDT'.format(symbol))['price']), 8)
    else:
        data['MarketPrice'] = 1.0

    # Active L/S Spot P/L
    data['Unrealized'] = (data['MarketPrice'] * data['Qty']) - data['CostBasis']

    # Realized L/S P/L
    if len(SELL['Qty']) > 0:
        data['Realized'] = sum(SELL['Qty'] * SELL['Price']) - sum((BUY['Qty']-data['Qty']) * BUY['Price'])
    else:
        data['Realized'] = 0

    data['Total_PL'] = data['Unrealized'] + data['Realized']
    data['Inactive_Long'] = BUY.Qty.sum() - data['Qty'].iloc[0]

    return data


def get_account_snapshot(client, type):
    snap = client.get_account_snapshot(type=type, limit=1)
    snap = snap['snapshotVos']
    snap = snap[0]['data']['balances']

    cols, names, qty = ['asset', 'free'], [], []
    for asset in snap:
        names.append(asset[cols[0]])
        qty.append(asset[cols[1]])
    data = pd.DataFrame()
    data['Asset'] = names
    data['Qty'] = pd.to_numeric(qty)

    return data


def get_spot_balances(client, snap):
    frame = pd.DataFrame()
    data = []
    for asset in snap.index:
        if asset != 'USDT':
            data.append(get_asset_status(client, asset))
    frame = frame.append(data)


    frame['PL%'] = round(frame['Total_PL']/(frame['CostBasis'])*100, 2)

    tmp_snap = get_account_snapshot(client, 'SPOT')

    account_value = frame.CostBasis.sum() + tmp_snap[tmp_snap.Asset == 'USDT'].Qty.iloc[0]
    #frame = frame[frame.TPL != 0]

    return [frame, account_value]


def wallet_composition(client, snap):
    price_q = []
    for asset in snap.index:
        price_q.append(client.get_avg_price(symbol='{}USDT'.format(asset))['price'])
    snap['Price'] = price_q
    snap.Qty = pd.to_numeric(snap.Qty)
    snap.Price = pd.to_numeric(snap.Price)
    snap['Value'] = snap.Qty * snap.Price

    return snap