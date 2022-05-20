import numpy as np
import pandas as pd
import CSuite.CSuite.CTrader as ct
import CSuite.CSuite.BConnector as bc
from binance.exceptions import BinanceAPIException


# Tick-Match Execution Algorithm
def tick_match(client, ticker, size, tickSize, distance=5, retry=10, refresh=2):
    # array to hold Ids and Book info
    ids = []

    for k in range(0, retry):
        # Get Live Quote
        book = bc.get_quote(client, ticker)
        # Calculate order strike
        if size > 0:
            price = float(book[1][0]) - (distance*tickSize)
        elif size < 0:
            price = float(book[0][0]) + (distance*tickSize)
        price = round(price, 5)

        # Submit Order
        order = ct.orderEntry.LimitOrder(client, price, abs(size), ticker, 0, 'GTC').submit()

        # If order is active
        if order.orderId != '':
            orderId = order.orderId
            # Report Submission
            print('Order Num {}'.format(str(k+1))+' -Status: '+order['status'] + ' Id: '+str(orderId)+' Price: '+str(price))
            ids.append([orderId, book])
            # Check executedQty N times (200ms each)
            for i in range(0, refresh):
                qty = float(client.get_order(symbol=ticker, orderId=orderId)['executedQty'])

            # If not filled yet then cancel
            if qty < 1:
                cancel = order.cancel()
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


# Mid-Point Match Execution Algorithm
def midpoint_match(client, ticker, size, tickSize, retry=10):
    record = []
    for i in range(0, retry):
        # get the Limit Order Book and thus Best-Bid & Best-Ask
        book = bc.get_quote(client, ticker)
        # Strike as Best-Bid + Spread/2
        best_bid, best_ask = float(book[1][0]), float(book[0][0])
        midpoint = round(best_bid + ((best_ask-best_bid)/2), 4)
        if best_ask - best_bid == tickSize:
            if size < 0:
                midpoint = midpoint + tickSize
            else:
                midpoint = midpoint - tickSize
        # Submit IOC Limit Order at the Strike without verification for added speed
        order = ct.LimitOrder(client, str(midpoint), size, ticker, 0, 'IOC').submit()
        # Monitor output
        print('Strike: '+str(midpoint)+' - Best Bid: ' + str(book[0][0]) + ' Best Ask: '+str(book[1][0]))
        # If order active then save orderId and Book used for record
        if order.orderId != '':
            orderId = order.orderId
            record.append([orderId, book])
            # Stop sending orders if any is filled
            if order.status == 'FILLED':
                print('Order Filled!')
                return record
        else:
            print(order)
            print('Order not Routed!')
            return False
        return record


# Mini-Lot enables execution of minimum possible size lots using current BBO
def mini_lot(client, symbol, size, tickSize, minQty, minNotional=10, retry=10):
    record = []
    # Sequential submission
    for k in range(0, retry):
        book = bc.get_quote(client, symbol)
        # choose between best bid or best ask based on direction
        if size > 0:
            strike = book[1][0]
        else:
            strike = book[0][0]
        # calculate strike and qty freely
        strike = round(float(strike), int(abs(np.log10(tickSize))))
        qty = round(minNotional/strike, int(abs(np.log(minQty))))
        # in some cases the qty calculation might be off by a bit,
        # thus we sequentially add 1 tick until we exceed minNotional + 0.5%
        while qty * strike < minNotional*1.0005:
            qty = qty + minQty

        # use string conversion to pass the exact right value of strike & qty if it rounds high
        strike = float(str(strike)[:int(abs(np.log10(tickSize)))+3])
        qty = float(str(qty)[:int(abs(np.log10(minQty)))+3])
        qty = qty * size
        # print statement
        print('Strike: '+str(strike)+' // Qty: '+str(qty)+' // Value: '+str(qty*strike))
        # build & submit order
        order = ct.LimitOrder(client, strike, qty, symbol, 0, 'IOC').submit()
        # check order, record and if filled then stop
        if order != {} and order.orderId != '':
            orderId = order.orderId
            record.append([orderId, book])
            # Stop sending orders if any is filled
            if order.status == 'FILLED':
                print('Order Filled!')
                return record
        else:
            print(order)
            print('Order not Routed!')
            return False
        return record


# Break-Even order mirroring algorithm
def breakeven(client, symbol, orderId, offset, tickSize, stepSize):
    order = client.get_order(symbol=symbol, orderId=orderId)
    if order['status'] == 'FILLED':
        if order['side'] == 'BUY':
            n, m = -1, 1
        elif order['side'] == 'SELL':
            n, m = 1, -1
        price, qty = float(order['price']), float(order['origQty'])
        cost_basis = price * qty
        total_fee = cost_basis - float(order['cummulativeQuoteQty'])
        token_fee = total_fee/float(order['cummulativeQuoteQty'])

        strike = round(price + (m*1.57*token_fee), int(abs(np.log10(tickSize))))
        sub_qty = round(n*float(order['cummulativeQuoteQty'])/price, int(abs(np.log10(stepSize))))

        t_strike = strike+(m*float(tickSize)*offset)
        t_strike = float(str(t_strike)[:int(abs(np.log10(tickSize)))+3])

        order = ct.orderEntry.LimitOrder(client, t_strike, sub_qty, symbol, 0, 'GTC')

        return order


# Buy Portfolio algo that builds an order collection which when submitted buys the specified long-only portfolio
def buy_portfolio(client, portfolio, balance, tickSize, stepSize):

    comp = pd.DataFrame(data=[portfolio.weights, tickSize, stepSize], columns=portfolio.symbols)
    orders = []
    for token in comp.columns:
        quote = float(bc.get_quote(client, token)[1][0])
        nomSize = float(balance*comp[token][0])
        size = round(nomSize/quote, int(abs(np.log10(comp[token][2]))))
        quote = round(quote, int(abs(np.log10(comp[token][1]))))
        print('Buy: {} units of {} at ${} a position size of {}%'
              .format(size, token, quote, round((nomSize/balance)*100), 2))
        order = ct.LimitOrder(client, quote, size, token, 0, 'GTC')
        try:
            order.test()
            orders.append(order)
        except BinanceAPIException:
            return False
    return orders
