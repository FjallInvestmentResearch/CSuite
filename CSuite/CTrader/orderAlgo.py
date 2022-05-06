import CSuite.CSuite.CTrader as ct


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