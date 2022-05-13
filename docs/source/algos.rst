CTrader
=================
The CTrader component enables users to submit and manage orders on the exchange. This module interfaces with the 
Limit Order Book functionality provided by :code:`view_book` & :code:`get_quote()`. Through this library users should
be able to quickly develop production ready algorithms. 

Setup & The Ledger
-------------------
In this library we have packaged a :code:`ledger` object alongside the :code:`client` such that building and calling complex, tick-accurate execution
algorithms is a simple process. Setting up these two objects is necessary when creating the enviornment to run the modules.
In order to build the ledger one needs to pass a list of symbols in String format however it is not necessary to use the ledger when using orders it just makes the process easier. 

.. code::

    client = CSuite.connect_client('setup.json')

    ledger = CSUite.build_ledger(client, ['ADAUSDT', 'BNBUSDT'])

Orders & Order Entry
---------------------

The Order Engine
*****************
In certain cases it may be necessary that the order generation and submission is contained by a recording and managment object, in this case, that is the Order Engine.
As an object, it contains the :code:`client`, symbol and, :code:`ledger`` (see above) and can be used to expedite and manage order submission and execusion processes for users necessitating a more streamlined interface.

Setting up the Engine
:code:`engine = OrderEngine(client, 'BTCUSDT', ledger)`

Building an Order
:code:`order = engine.order('MKT', 1)`

Submitting the Order
:code:`order.submit()`

.. warning:: Iceberg orders are currently not supported

Limit Order
************
A limit order is a type of order to purchase or sell a security at a specified price or better. 
By using a buy limit order, the investor is guaranteed to pay that price or less. While the price is guaranteed, 
the filling of the order is not, and limit orders will not be executed unless the security price meets the 
order qualifications. If the asset does not reach the specified price, the order is not filled.

Limit Orders requires 6 parameters, the :code:`client` for data access and 4 order parameters. In limit orders a Limit Price (Price) is necessary
and so is a symbol (str) and the quatity, which is also used to specify trade direction, e.g. +10 (BUY) and -10 (SELL). 
The :code:`timeInForce` variable specifies the order enforcment and defualts to Good-Till-Cancel ('GTC'), it can be set to:

* **Good-Till-Cancel** ('GTC'): An order to buy or sell a security that lasts until the order is completed or canceled.
* **Fill-Or-Kill** ('FOK'): An order to buy or sell a security that must be executed immediately in its entirety; otherwise, the entire order will be cancelled.
* **Immediate-Or-Cancel** ('IOC'): An order to buy or sell a security that must be executed immediately. Any portion of an IOC order that cannot be filled immediately will be cancelled.

Limit Order support a stop through the :code:`stop`  parameter which has a defualt value of 0. The stop is set as a nominal (price) value which is automatically
converted into a TP or SL. For example passing a price of 100 and a stop of 120 would imply a Take Profit (TP), conversly a stop of 80 would imply a Stop Loss (SL)


+------------+------------+-----------+-----------+
| **Name**   | **Type**   |**Example**|**Default**|
+------------+------------+-----------+-----------+
| Price      | Float      | 0.5002    |  None     |
+------------+------------+-----------+-----------+
| Size (Qty) | Float      | 15 or -50 |  None     |
+------------+------------+-----------+-----------+
| Symbol     | String     | 'BTCUSDT' |  None     |
+------------+------------+-----------+-----------+
| stop       | Float      | 0,  1.25  |    0      |
+------------+------------+-----------+-----------+
| timeInForce| String     |'GTC' 'FOK'|   'GTC'   |
+------------+------------+-----------+-----------+

One can generate a simply Limit Order as such. For example to build an order for 1 BNB token at 0 with
no SL/TP and a 'GTC' time parameter.
.. code::
    
    order = CSuite.LimitOrder(client, 300.0, 1, 'BNBUSDT', 0, 'GTC')`

Submit
^^^^^^
To submit a built order to the Binance Exchange the submit method of the Limit Order can be used. As such: :code:`order.submit()`

Test
^^^^^
To validate a built order by submitting an identical test order the :code:`test()` method may be used. This is useful if order parameters must be verified fast
as the call and response takes a mere 200ms. This is possible as such: :code:`order.test()`.
Test routes the order through the Exchange filters but not to the matchine engine. If the order is valid a '{}' is returned.

Cancel
^^^^^^
To cancel a submitted order (one that has recived a valid :code:`orderId` variable) the cancel method can be used: :code:`order.cancel()`.

Verify
^^^^^^

Market Order
************
A market order is an instruction by an investor to a broker to buy or sell stock shares, bonds, or other assets at the best available price in the current financial market.
It is the default choice for buying and selling for most investors most of the time.That means that a market order will be completed nearly instantaneously at a price very 
close to the latest posted price that the investor can see.

Market Orders requires 4 parameters, the :code:`client` for data access and 3 order parameters. In limit orders passing a price is not necessary
and however a so is a symbol (str) and quatity must be set, with the latter being used to specify trade direction, e.g. +10 (BUY) and -10 (SELL). 
No :code:`timeInForce` parameter is necessary as all Market Orders are flagged for immedate execution. 

Market Order supports a stop through the :code:`stop`  parameter which has a defualt value of 0. The stop is set as a nominal (price) value which is automatically
converted into a TP or SL. For example passing a price of 100 and a stop of 120 would imply a Take Profit (TP), conversly a stop of 80 would imply a Stop Loss (SL)

+------------+------------+-----------+-----------+
| **Name**   | **Type**   |**Example**|**Default**|
+------------+------------+-----------+-----------+
| Size (Qty) | Float      | 15 or -50 |  None     |
+------------+------------+-----------+-----------+
| Symbol     | String     | 'BTCUSDT' |  None     |
+------------+------------+-----------+-----------+
| stop       | Float      | 0,  1.25  |    0      |
+------------+------------+-----------+-----------+

One can generate a simple Market Order as such. For example to build an order for 1 BNB token with
no SL/TP.
.. code::
    
    order = CSuite.MarketOrder(client, 1, 'BNBUSDT', 0')`


Post-Only Order
****************


Order Book Functions
---------------------

Build Ledger
*************
:code:`ledger = build_ledger(client, ['BTCUSDT', 'ADAUSDT', 'BNBUSDT'])`

Plot Limit Order Book
**********************

Expected Sweep Cost 
*********************

Plot Expected Sweep Cost
*************************

Order Execution Algorithms
---------------------------
Utilising the extensive wrapping of functionality we can provide packaged execution algorithms which can 
be worked with or without the :code:`OrderEngine`

Tick Match
***********
Tick Match (or Peg Match) is a propriatery high-speed, high-fill peg algorithm that requires no counterparty 
(i.e. executes in the market). Tick Match enables the trader to peg an order at a specific tick distance from the BBO. 
The algorithm executes by posting Limit Orders at a set distance from the BBO, say 2 or 3 ticks. Continous monitoring of 
each order is the defualt and the time until the order is force cancelled is set via the :code:`refresh` parameter. Each refresh cycle is
approx. 600ms. 

Parameters

+------------+------------+-----------+-----------+------------------------+
| **Name**   | **Type**   |**Example**|**Default**|  **Decription**        |
+------------+------------+-----------+-----------+------------------------+
| client     | Client     | Object    |  None     | API client             |
+------------+------------+-----------+-----------+------------------------+
| symbol     | String     | 'BTCUSDT' |  None     | Binance symbol str     |
+------------+------------+-----------+-----------+------------------------+
| size (qty) | Float      | 0,  1.25  |    0      | Order qty (neg = sell) |
+------------+------------+-----------+-----------+------------------------+
| tickSize   | Float      | 0.0001    |    0      | min tradable tick      |
+------------+------------+-----------+-----------+------------------------+
| distance   | int        | 1, 12     |    5      | tick distance from BBO |
+------------+------------+-----------+-----------+------------------------+
| retry      | int        | 5,  25    |    10     |num of order submissions|
+------------+------------+-----------+-----------+------------------------+
| refresh    | int        | 1, 3      |    1      |num of monitor cycles   |
+------------+------------+-----------+-----------+------------------------+

Returns


Direct Access
^^^^^^^^^^^^^^^

.. code-block:: 

    execution = CSUite.tick_match(client, symbol='BNBUSDT', size=1, tickSize=0.001, distance=3, retry=10, refresh=2)

Example code for running the algo to buy 1 'BNB' token by sending 10 consecutive orders each at 3 ticks from the BBO. Furthermore, each order is monitored
twice (specified via refresh) before forced cancelled if not filled. 

via OrderEngine Wrapper
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: 

    engine = OrderEngine(client, 'BTCUSDT', ledger)
    execution = engine.tick_match(size=0.02, distance=3, retry=10, refresh=1)

Mid-Point Match
***************

Mini-Lot
********