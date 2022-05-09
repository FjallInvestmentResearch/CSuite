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

+------------+------------+-----------+
| Name       | Type       | Example   |
+------------+------------+-----------+
| Price      | Float      | 0.5002    |
+------------+------------+-----------+
| Size (Qty) | Float      | 15 or -50 |
+------------+------------+-----------+
| Symbol     | String     | 'BTCUSDT' |
+------------+------------+-----------+
| timeInForce| String     |'GTC' 'FOK'|
+------------+------------+-----------+

**Building an Order:** :code:`order = CSuite.LimitOrder(client, 300.0, 1, 'BNBUSDT', 'GTC')`

Submit
^^^^^^
To submit a built order to the Binance Exchange the submit method of the Limit Order can be used. As so: :code:`order.submit()`

Test
^^^^^
To test a built order by submitting an identical test order this :code:`test` method may be used. This is useful if order parameters must be verified fast
as the call and response takes a mere 200ms. This is possible as such: :code:`order.test()`.

Cancel
^^^^^^
To cancel a submitted order (one that has recived a valid :code:`orderId` variable) the cancel method can be used: :code:`order.cancel()`.

Market Order
************

Post Order
***********

Order Book Functions
---------------------

Order Execution Algorithms
---------------------------