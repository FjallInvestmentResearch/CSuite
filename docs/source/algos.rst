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
Limit Orders provide guaranteed price at execution, at the Limit Price or better, however the execution is not immediate.

:code:`order = CSuite.LimitOrder(client, 300.0, 1, 'BNBUSDT', 'GTC')`

Market Order
************

Post Order
***********

Order Book Functions
---------------------

Order Execution Algorithms
---------------------------