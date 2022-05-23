Recipes
=================
In this section we have included a number of annotated and explained code examples
utilising the CSuite modules. 

Buy Order
----------
This is a simple recipe to create the code to send a Buy order for 1 Binance Token at the Best Bid. 
The :code:`client` and :code:`ledger` enable us to send orders and recive prices. We first access the Best Bid
(since we want to buy) by calling :code:`get_quote` and accessing the best bid '[1]' and from there the price '[0]'. 
Finally we can send a Limit Order with the parameters we want and use :code:`verified_submit()` such that the order passes relevant
checks before being routed. 

.. code-block::

    # Step 1 Connect the client by linking the JSON file
    client = CSuite.connect_client('file.json')

    # Step 2: Get token trade parameters via the ledger
    ledger = CSuite.build_ledger(client, ['BNBUSDT'])

    # Step 3: Get the latest quote and save the best bid for 'passive execution'
    price = float(CSuite.get_quote(client, 'BNBUSDT')[1][0])

    # Step 4: Send a Limit Order for 1 token of BNB with FOK time and no SL/TP.
    # Order parameters are verified through the downloaded ledger which checks for minQty, minNominal etc.
    order = CSuite.LimitOrder(client, price, 1, 0, 'BNBUSDT', 'FOK').verified_submit(ledger)


Tick-Match Buy
---------------
This is a simple recipe to setup a order algorithm using the OrderEngine object.

.. code-block::

    # Step 1: Connect Binance Client
    client = CSuite.connect_client('global.json')

    # Step 2: Build Ledger
    ledger = CSuite.build_ledger(client, ['BNBUSDT'])

    # Step 3: Setup Order Engine
    BNB_COIN = CSuite.OrderEngine(client, 'BNBUSDT', ledger)

    # Step 4: Start Algorithmic Execution
    BNB_COIN.tick_match(25, 3)


Expected Sweep Cost
--------------------
This is a simple calculator which enables users to view the expected sweep cost of 
hitting the book with a large block order at that time.

.. code-block:: 

    def sweep(pair, size):
    # Step 0: Convert Size input into BUY/SELL side parameter
    if size < 0:
        side = 'SELL'
    else:
        side = 'BUY'
    # Step 1: Connect with Binance Client for data
    client = CSuite.connect_client('file.json')
    # Step 2: Download Limit Order Book
    book = CSuite..view_book(pair, client)
    # Step 3: Calculate Expected Sweep Cost on a specified order of size with reference price being the Ask
    frame = CSuite.sweep_cost(book[0], abs(size), pair, side, ref='A')

    return frame