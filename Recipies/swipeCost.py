import CTrader


def swipe(pair, size):
    if size < 0:
        side = 'SELL'
    else:
        side = 'BUY'
    client = CTrader.ctrader.connector.connect_client('file.json')
    book = CTrader.LOB.view_book(pair, client)
    frame = CTrader.LOB.swipe_cost(book[0], abs(size), pair, side, ref='A')

    return frame


swipe('BTCUSDT', -25)
