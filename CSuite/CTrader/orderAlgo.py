import CSuite.CSuite.CTrader as ct
import numpy as np


# Tick-Match Execution Algorithm
def tick_match(client, ticker, size, tickSize, distance=5, retry=10, refresh=2):
    # array to hold Ids and Book info
    ids = []

    for k in range(0, retry):
        # Get Live Quote
        book = ct.orderBook.get_quote(client, ticker)
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
        book = ct.orderBook.get_quote(client, ticker)
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


# TEST
def mini_lot(client, symbol, size, tickSize, minQty, minNotional=10, retry=10):
    record = []
    for k in range(0, retry):
        book = ct.connector.get_quote(client, symbol)
        if size > 0:
            strike = book[1][0]
        else:
            strike = book[0][0]
        strike = round(float(strike), int(abs(np.log10(tickSize))))
        qty = round(minNotional/strike, int(abs(np.log(minQty))))
        while qty * strike < minNotional*1.002:
            qty = qty + minQty

        strike = float(str(strike)[:int(abs(np.log10(tickSize)))+3])
        qty = float(str(qty)[:int(abs(np.log10(minQty)))+3])
        qty = qty * size

        print('Strike: '+str(strike)+' // Qty: '+str(qty)+' // Value: '+str(qty*strike))

        order = ct.LimitOrder(client, strike, qty, symbol, 0, 'IOC').submit()
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
