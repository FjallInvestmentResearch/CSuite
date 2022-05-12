Recipes
=================

Buy Order
----------
This is a simple recipe to create the code to send a Buy order.

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
