import pandas as pd


def view_book(symbol, client):
    # call order book JSON read
    order_snap = client.get_order_book(symbol=symbol, limit=100)

    # Parse JSON structure
    bid_prices, bid_vol = [], []
    ask_prices, ask_vol = [], []
    for k in range(0, 100):
        bid_prices.append(float(order_snap['bids'][k][0]))
        bid_vol.append(float(order_snap['bids'][k][1]))
        ask_prices.append(float(order_snap['asks'][k][0]))
        ask_vol.append(float(order_snap['asks'][k][1]))

    # format ladder
    bid_vol = ([0.0 for i in range(0, 100)] + bid_vol)
    price = ask_prices[::-1] + bid_prices
    ask_vol = (ask_vol + [0.0 for i in range(0, 100)])
    # create & return pandas DF object
    frame = pd.DataFrame(data=list(zip(bid_vol, price, ask_vol)), columns=['bid_vol', 'quote', 'ask_vol'], index=range(0, 200))

    return frame, order_snap['lastUpdateId']


def monitor_book(symbol, client, limit):
    spread, mid_point, timestamp = [], [], []
    ask_mean, bid_mean = [], []
    book_balance, bba = [], []
    run, count = True, 0
    # Data fetching loop
    while run is True:
        # retrieve book
        book = view_book(symbol, client)
        frame = book[0]
        # retrieve timestamp
        timestamp.append(book[1])
        # Book analysis
        best_ask, best_bid = frame.iloc[101], frame.iloc[100]
        # Spread
        spread.append(best_bid['quote'] - best_ask['quote'])
        # Mid-point
        mid_point.append((best_bid['bid_vol']*best_ask['quote'] + best_ask['ask_vol']*best_bid['quote'])/(best_ask['ask_vol']+best_bid['bid_vol']))
        # Book Balance
        book_balance.append(sum(frame['bid_vol']*frame['quote'])/sum(frame['ask_vol']*frame['quote']))
        # Weighted Mean by Side
        bid_mean.append(sum(frame.quote * frame.bid_vol)/sum(frame.bid_vol))
        ask_mean.append(sum(frame.quote * frame.ask_vol)/sum(frame.ask_vol))
        bba.append(best_bid)

        count = count + 1

        if count > limit:
            run = False

    df = pd.DataFrame(data=list(zip(timestamp, mid_point, spread, book_balance, bid_mean, ask_mean, bba)), columns=['timestamp', 'mid_point', 'spread', 'book_balance', 'bid_mean', 'ask_mean', 'best_bid'], index=range(0,limit+1))

    return df
