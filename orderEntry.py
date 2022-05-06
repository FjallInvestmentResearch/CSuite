# ORDER MANAGEMENT SYSTEM
# Order object
from binance.enums import *
from CTrader import orderbook


class LimitOrder:
    price, size= 0, 0
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

    def verify_trade(self, ledger):

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
        if self.verify_trade(ledger):
            self.submit()
            return True
        else:
            return False

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

    def verify_trade(self, ledger):

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
        if self.verify_trade(ledger):
            self.submit()
            return True
        else:
            return False

    def submit(self):
        if self.stop == 0:
            self.stop = None

        return self.client.create_test_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), stopPrice=self.stop)


class PostOrder:
    price, size= 0, 0
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

    def verify_trade(self, ledger):

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
        if self.verify_trade(ledger):
            self.submit()
            return True
        else:
            return False

    def submit(self):
        return self.client.create_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), price=str(self.price), timeInForce=None)


# Tick-Match Execution Algorithm
def tick_match(client, ticker, size, tickSize, distance=5, retry=10, refresh=2):
    # array to hold Ids and Book info
    ids = []

    for k in range(0, retry):
        # Get Live Quote
        book = orderbook.get_quote(client, ticker)
        # Calculate order strike
        if size > 0:
            price = float(book[1][0]) - (distance*tickSize)
        elif size < 0:
            price = float(book[0][0]) + (distance*tickSize)
        price = round(price, 5)

        # Submit Order
        order = LimitOrder(client, price, abs(size), ticker, 0, 'GTC').submit()

        # If order is active
        if type(order) != bool:
            orderId = order['orderId']
            # Report Submission
            print('Order Num {}'.format(str(k+1))+' -Status: '+order['status'] + ' Id: '+str(orderId)+' Price: '+str(price))
            ids.append([orderId, book])
            # Check executedQty N times (200ms each)
            for i in range(0, refresh):
                qty = float(client.get_order(symbol=ticker, orderId=orderId)['executedQty'])

            # If not filled yet then cancel
            if qty < 1:
                cancel = client.cancel_order(symbol=ticker, orderId=orderId)
                if cancel['status'] == 'CANCELED':
                    print('Order Num {}: Cancelled!'.format(k+1))
            else:
                # Confirm Execution
                print('Order Executed!')
                return ids
        else:
            # If fails activation then show as invalid
            print('Invalid Order. Not Routed!')
            return False

    print('Execution Done!')
    return ids
