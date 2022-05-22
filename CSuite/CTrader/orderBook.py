import pandas as pd
import matplotlib.pyplot as plt
import CSuite.CSuite.BConnector as bc

# Orderbook Functions


# Builds the trading parameter ledger for an array of symbols.
def build_ledger(client, symbols):
    frame = pd.DataFrame(columns=['symbol', 'status', 'icebergAllowed', 'ocoAllowed', 'allowTrailingStop', 'tickSize', 'up',
                                  'down', 'minQty', 'maxQty', 'stepSize', 'minNotional', 'icebergParts', 'maxNumOrders'])
    for ticker in symbols:
        length = len(frame)
        frame.loc[length] = (bc.get_symbol_info(client, ticker))

    frame = frame.astype({"icebergAllowed": bool, "ocoAllowed": bool, "allowTrailingStop": bool, "tickSize": float,
                          "up": float, "down": float, "minQty": float, "maxQty": float, "stepSize": float,
                          "minNotional": float, "icebergParts": int, "maxNumOrders": int})
    frame = frame.set_index('symbol')

    return frame


# Plots the resting limit book orders currently active for a specified depth. Returns plt plot/image with bars of volume
def plot_book(book, symbol, limit=100, plot=True, save=False, path=''):

    book, timestamp = book[0], book[1]
    best_ask, best_bid = book.iloc[int(limit/2)-1], book.iloc[int(limit/2)]
    midpoint = ((best_bid['bid_vol']*best_ask['quote'] + best_ask['ask_vol']*best_bid['quote'])/
                (best_ask['ask_vol']+best_bid['bid_vol']))
    # ref_move = [round(((quote-midpoint)/midpoint)*100, 3) for quote in book['quote']]

    if plot:
        plt.bar(book['quote'], book['ask_vol'], color='red', label='Ask')
        plt.bar(book['quote'], book['bid_vol'], color='green', label='Bid')
        plt.axvline(midpoint, color='black', linewidth=1, linestyle='--', label='Mid')
        plt.ylabel('Volume (# Units in LOB)')
        plt.xlabel('Quote ($)')
        plt.title('Limit Order Book in {}'.format(symbol))
        plt.legend()
        plt.show()
        if save:
            plt.savefig('{}book{}.jpg'.format(path, symbol), dpi=800)

    return book


# Function which provides the Swipe cost of walking the orderbook for a specified lot size (size). Requires book object
def sweep_cost(book, size, pair='NA', side='BUY', ref='A'):

    asks = book['ask_vol'][0:int(len(book)/2)]
    best_ask, best_bid = book.iloc[int(len(book)/2)-1], book.iloc[int(len(book)/2)]
    midpoint = ((best_bid['bid_vol']*best_ask['quote'] + best_ask['ask_vol']*best_bid['quote'])
                / (best_ask['ask_vol']+best_bid['bid_vol']))

    fill = 0

    if side == 'BUY':
        for i in range(len(asks)-1, 0, -1):
            fill = fill + book['ask_vol'][i]
            if fill >= size:
                price = (book['quote'][i+1])
                break

    elif side == 'SELL':
        for i in range(len(asks), len(book)):
            fill = fill + book['bid_vol'][i]
            if fill >= size:
                price = (book['quote'][i-1])
                break

    else:
        price = 0

    if ref == 'A':
        ref_price = best_ask['quote']
    elif ref == 'B':
        ref_price = best_bid['quote']
    elif ref == 'M':
        ref_price = midpoint
    else:
        ref_price = best_ask['quote']

    change = (abs((price-ref_price)/ref_price).round(6))
    rows = ['Pair', 'Size', 'Ref. Price', 'Expected Price', 'Cost (%)']
    datums = [pair, size, ref_price, price, change*100]
    fr = pd.DataFrame()
    fr['Index'] = rows
    fr['Data'] = datums

    return fr


# Plots the Expected Swipe Cost (ESC) of sell & buy orders for orders up to size max. Returns plt plot.
def plot_esc(book, symbol, max=100, inc=1, plot=True, save=False, path=''):
    results = []
    for i in range(-max, max, inc):
        if i < 0:
            side = 'SELL'
            results.append(sweep_cost(book, abs(i), symbol, side, ref='B').iloc[4]['Data'])
        elif i > 0:
            side = 'BUY'
            results.append(sweep_cost(book, abs(i), symbol, side, ref='A').iloc[4]['Data'])

    if plot:
        plt.plot([i for i in range(0, max)], results[0:max][::-1], color='r', label='Selling')
        plt.plot([i for i in range(0, max)], results[max-1:max*2], color='g', label='Buying')
        plt.legend()
        plt.ylim(0, 0.35)
        plt.xlabel('Lot Size (Units)')
        plt.ylabel('Expected Sweep Cost (%)')
        plt.title('Expected Sweep Cost by Lot Size')
        plt.tight_layout()
        if save:
            plt.savefig('{}ESC_{}.jpg'.format(path, symbol), dpi=800)
        plt.show()


# Continuously monitors the book using view_book() function and records vitals
def monitor_book(symbol, client, limit):
    spread, mid_point, timestamp = [], [], []
    ask_mean, bid_mean = [], []
    book_balance, bba = [], []
    run, count = True, 0
    # Data fetching loop
    while run is True:
        # retrieve book
        book = C.view_book(symbol, client)
        frame = book[0]
        # retrieve timestamp
        timestamp.append(book[1])
        # Book analysis
        best_ask, best_bid = frame.iloc[101], frame.iloc[100]
        # Spread
        spread.append(best_bid['quote'] - best_ask['quote'])
        # Mid-point
        mid_point.append((best_bid['bid_vol']*best_ask['quote'] + best_ask['ask_vol']*best_bid['quote'])/
                         (best_ask['ask_vol']+best_bid['bid_vol']))
        # Book Balance
        book_balance.append(sum(frame['bid_vol']*frame['quote'])/sum(frame['ask_vol']*frame['quote']))
        # Weighted Mean by Side
        bid_mean.append(sum(frame.quote * frame.bid_vol)/sum(frame.bid_vol))
        ask_mean.append(sum(frame.quote * frame.ask_vol)/sum(frame.ask_vol))
        bba.append(best_bid)

        count = count + 1

        if count > limit:
            run = False

    df = pd.DataFrame(data=list(zip(timestamp, mid_point, spread, book_balance, bid_mean, ask_mean, bba)),
                      columns=['timestamp', 'mid_point', 'spread', 'book_balance', 'bid_mean', 'ask_mean', 'best_bid'],
                      index=range(0, limit+1))

    return df
