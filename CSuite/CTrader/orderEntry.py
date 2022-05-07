# ORDER MANAGEMENT SYSTEM
# Order object
from binance.enums import *
import CSuite.CSuite.CTrader as C


class LimitOrder:
    price, size = 0, 0
    symbol = ''
    stop, timeInForce = 0.0, 'GTC'
    params, client = None, None

    # API parameters
    side = None
    type = None

    def __init__(self, client, price, size, symbol, stop, timeInForce):

        if size > 0:
            self.side = SIDE_BUY
        else:
            self.side = SIDE_SELL

        self.stop = stop
        if stop == 0:
            self.type = ORDER_TYPE_LIMIT
        elif stop > price:
            self.type = ORDER_TYPE_TAKE_PROFIT_LIMIT
        elif stop < price:
            self.type = ORDER_TYPE_STOP_LOSS_LIMIT


        if timeInForce == 'GTC':
            self.timeInForce = TIME_IN_FORCE_GTC
        elif timeInForce == 'FOK':
            self.timeInForce = TIME_IN_FORCE_FOK
        elif timeInForce == 'IOC':
            self.timeInForce = TIME_IN_FORCE_IOC

        self.price, self.size, self.symbol = float(price), size, symbol
        self.client = client

    def verify(self, ledger):

        def verify_price():
            ref_price = float(self.client.get_avg_price(symbol=self.symbol)['price'])
            #print(type(self.price))
            if (self.price < ref_price*self.params['up']) and (self.price > ref_price*self.params['down']):
                return True
            else:
                return False

        def verify_notional():
            if self.price * abs(self.size) > self.params['minNotional']:
                return True
            else:
                return False

        def verify_qty():
            if (abs(self.size) > self.params['minQty']) and (abs(self.size) < self.params['maxQty']):
                return True
            else:
                return False

        self.params = ledger.loc[self.symbol]

        if verify_price():
            if verify_notional():
                if verify_qty():
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def verified_submit(self, ledger):
        if self.verify(ledger):
            self.submit()
            return True
        else:
            return False

    def test(self):
        if self.stop == 0:
            self.stop = None
        return self.client.create_test_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), price=str(self.price), timeInForce=self.timeInForce, stopPrice=self.stop)

    def submit(self):
        if self.stop == 0:
            self.stop = None
        return self.client.create_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), price=str(self.price), timeInForce=self.timeInForce, stopPrice=self.stop)


class MarketOrder:
    size = 0
    symbol = ''
    stop = 0.0
    params, client = None, None

    # API parameters
    side = None
    type = None

    def __init__(self, client, size, symbol, stop=0):

        self.client = client
        self.size, self.symbol = size, symbol
        self.price = float(self.client.get_avg_price(symbol=self.symbol)['price'])

        if size > 0:
            self.side = SIDE_BUY
        else:
            self.side = SIDE_SELL

        self.stop = stop
        if stop == 0:
            self.type = ORDER_TYPE_MARKET
        elif stop > self.price:
            self.type = ORDER_TYPE_TAKE_PROFIT
        elif stop < self.price:
            self.type = ORDER_TYPE_STOP_LOSS

    def verify(self, ledger):

        def verify_notional():
            if self.price * abs(self.size) > self.params['minNotional']:
                return True
            else:
                return False

        def verify_qty():
            if (abs(self.size) > self.params['minQty']) and (abs(self.size) < self.params['maxQty']):
                return True
            else:
                return False

        self.params = ledger.loc[self.symbol]

        if verify_notional():
            if verify_qty():
                return True
            else:
                return False
        else:
            return False

    def verified_submit(self, ledger):
        if self.verify(ledger):
            self.submit()
            return True
        else:
            return False

    def test(self):
        if self.stop == 0:
            self.stop = None

        return self.client.create_test_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), stopPrice=self.stop)

    def submit(self):
        if self.stop == 0:
            self.stop = None

        return self.client.create_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), stopPrice=self.stop)


class PostOrder:
    price, size = 0, 0
    symbol = ''
    timeInForce = 'GTC'
    params, client = None, None

    # API parameters
    side = None
    type = None

    def __init__(self, client, price, size, symbol, timeInForce):

        if size > 0:
            self.side = SIDE_BUY
        else:
            self.side = SIDE_SELL

        self.type = ORDER_TYPE_LIMIT_MAKER


        if timeInForce == 'GTC':
            self.timeInForce = TIME_IN_FORCE_GTC
        elif timeInForce == 'FOK':
            self.timeInForce = TIME_IN_FORCE_FOK
        elif timeInForce == 'IOC':
            self.timeInForce = TIME_IN_FORCE_IOC

        self.price, self.size, self.symbol = float(price), size, symbol
        self.client = client

    def verify(self, ledger):

        def verify_price():
            ref_price = float(self.client.get_avg_price(symbol=self.symbol)['price'])
            #print(type(self.price))
            if (self.price < ref_price*self.params['up']) and (self.price > ref_price*self.params['down']):
                return True
            else:
                return False

        def verify_notional():
            if self.price * abs(self.size) > self.params['minNotional']:
                return True
            else:
                return False

        def verify_qty():
            if (abs(self.size) > self.params['minQty']) and (abs(self.size) < self.params['maxQty']):
                return True
            else:
                return False

        self.params = ledger.loc[self.symbol]

        if verify_price():
            if verify_notional():
                if verify_qty():
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def verified_submit(self, ledger):
        if self.verify(ledger):
            self.submit()
            return True
        else:
            return False

    def test(self):
        return self.client.create_test_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), price=str(self.price), timeInForce=None)

    def submit(self):
        return self.client.create_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), price=str(self.price), timeInForce=None)


class OrderEngine:
    client, ticker = None, ''
    ledger = None

    def __init__(self, client, ticker, ledger):
        self.client = client
        self.ticker = ticker
        self.ledger = ledger
        return

    def order(self, type, size, price=0, stop=0, timeInForce='GTC'):

        if type == 'LMT' and price != 0:
            tmp_order = LimitOrder(self.client, price, size, self.ticker, stop, timeInForce)
        elif type == 'MKT':
            tmp_order = MarketOrder(self.client, size, self.ticker, stop)
        else:
            return False

        def send():
            return tmp_order.submit()

        def test():
            return tmp_order.test()

        return tmp_order

    def tick_match(self, size, distance=5, retry=10, refresh=2):
        return C.tick_match(self.client, self.ticker, float(size),
                            float(self.ledger.loc[self.ticker]['tickSize']), distance, retry, refresh)

    def midpoint_match(self, size, retry=10):
        return C.midpoint_match(self.client, self.ticker, float(size),
                                float(self.ledger.loc[self.ticker]['tickSize']), retry=retry)

