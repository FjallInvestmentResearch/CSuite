CTrader
=================
Order Execution is a critical component of the CSuite offering

Setup & The Ledger
-------------------

Orders & Order Entry
---------------------

The Order Engine
*****************
In certain cases it may be necessary that the order generation and submission is contained by a recording and managment object, in this case, that is the Order Engine.
As an object, it contains the :code:`client`, symbol and, ledger (see above) and can be used to expedite and manage order submission and execusion processes for users necessitating a more streamlined interface.

Setting up the Engine
:code:`engine = OrderEngine(client, 'BTCUSDT', ledger)`

Building an Order
:code:`order = engine.order('MKT', 1)`

Submitting the Order
:code:`order.submit()`

Limit Order
************
A limit order is a type of order to purchase or sell a security at a specified price or better. 
By using a buy limit order, the investor is guaranteed to pay that price or less. While the price is guaranteed, 
the filling of the order is not, and limit orders will not be executed unless the security price meets the 
order qualifications. If the asset does not reach the specified price, the order is not filled.

Limit Orders requires 5 parameters, the :code:`client` for data access and 4 order parameters. In limit orders a Limit Price (Price) is necessary
and so is a symbol (str) and the quatity, which is also used to specify trade direction, e.g. +10 (BUY) and -10 (SELL). 
The :code:`timeInForce` variable specifies the order enforcment and defualts to Good-Till-Cancel ('GTC'), it can be set to:

* **Good-Till-Cancel** ('GTC'): An order to buy or sell a security that lasts until the order is completed or canceled.
* **Fill-Or-Kill** ('FOK'): An order to buy or sell a security that must be executed immediately in its entirety; otherwise, the entire order will be cancelled.
* **Immediate-Or-Cancel** ('IOC'): An order to buy or sell a security that must be executed immediately. Any portion of an IOC order that cannot be filled immediately will be cancelled.
 
+------------+------------+-----------+
| **Name**   | **Type**   |**Example**|
+------------+------------+-----------+
| Price      | Float      | 0.5002    |
+------------+------------+-----------+
| Size (Qty) | Float      | 15 or -50 |
+------------+------------+-----------+
| Symbol     | String     | 'BTCUSDT' |
+------------+------------+-----------+
| timeInForce| String     |'GTC' 'FOK'|
+------------+------------+-----------+


:code:`order = CSuite.LimitOrder(client, 300.0, 1, 'BNBUSDT', 'GTC')`

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

Tick Match
***********

Mid-Point Match
***************

Mini-Lot
********