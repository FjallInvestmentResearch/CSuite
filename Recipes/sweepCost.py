import CSuite


def sweep(pair, size):
    # Step 0: Convert Size input into BUY/SELL side parameter
    if size < 0:
        side = 'SELL'
    else:
        side = 'BUY'
    # Step 1: Connect with Binance Client for data
    client = CSuite.CSuite.BConnector.connector.connect_client('file.json')
    # Step 2: Download Limit Order Book
    book = CSuite.CSuite.CTrader.orderBook.view_book(pair, client)
    # Step 3: Calculate Expected Sweep Cost on a specified order of size with reference price being the Ask
    frame = CSuite.CSuite.CTrader.orderBook.sweep_cost(book[0], abs(size), pair, side, ref='A')

    return frame


# Calculate on selling (-) 25  units of BTC-USDT
sweep('BTCUSDT', -25)
