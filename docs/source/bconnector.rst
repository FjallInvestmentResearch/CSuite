BConnector
===================================
The BConnector module acts as the API interface between custom CSuite functionality and the Binance Exchange.
Connectivity with Binance is achieved via the `binance-python library <https://python-binance.readthedocs.io/en/latest/index.html#>`_ developed by Sam McHardy; thank you Sam!

The API Client
--------------
The object which enables API calls is the :code:`client` which is derived from a connection via the binance-python lib.
The client can be used to connect with the exchange and send, recive data ad-hoc or in real-time and is necessary for most connected functionality such
as data retrival and order submission. A client can be easily created:

.. code-block::

    client = CSuite.connect_client('filename.json')

To initiate the client one must provide a JSON file with the two API keys for Binance, indexed as 'API KEY' and 'SECRET KEY'.
Once the client has been called successfully by providing up-to-date keys, the returned client object must be kept for later use.

Get Spot Timeseries
--------------------------
Downloading timeseries (OCHL) data for a specific crypto made extremely easy through the Kline function, which returns a Pandas DataFrame
with all the data: OCHL & Volume. The client is a required parameter, so is the symbol (Binance pair notation) and the interval which can be from
'1m' to '4d'. Please note that this function will return the latest 1000 data-points.

.. code-block::

    BTC = CSuite.get_SpotKlines(client, 'BTCUSDT', '1d')

Get Multiple Spot Timeseries
*****************************
Since users often find themselves needing to download multiple timeseries at the same time, we provide the custom :code:`get_batch_historic()` function.
This function allows the download of parrallel historical timeseries data for multiple crypto. Unlike the :code:`get_SpotKline()` function, this one requires an array of strings in the symbols parameter.
It also supports multiple modes through the mode parameter, the following is supported:

* Nominal - Closing Price ('N')
* Return - Daily Closing % Return ('R')
* Volatility - Rolling 5-day Standard Deviation ('V')


.. code-block::

    frame = CSuite.get_batch_historic(client, ['BTCUSDT', 'ADAUSDT'], '1d', 'N')

Get Quote & Limit Order Book
----------------------------

Viewing the Orderbook
**********************
Retrieving the live limit order book (LOB) is the first step in accessing the real time market on the exchange. Using this limit order
book functionality it is possible to have near-real time access to the access via equivalent DMA. The Binance API has a refresh rate of
200ms for the book.

We can simply call the :code:`view_book()` function to get a snapshot of the book. It returns a
ladder-like DataFrame with bid/ask volumes in num of tokens and Prices. The ticks are NOT uniform.

.. code::

    book = CSUite.view_book(client, symbol='BNBUSDT', limit=100)

Get Quote
**********
In certain use cases it may be useful to access only the best bid ask & volume at those ticks
in such cases we offer a parsed version of the book function via :code:`get_quote()` which directly interacts
with the Binance API for high speeds.

.. code::

    quote  = CSuite.get_quote(client, symbol='BTCUSDT')

Getting Symbol Trade Parameters
*********************************
We have also created a simplified way to parse the Exchange information necessary to execute automated trading
details such as the trading status, tickSize, and minimum notional are included.

.. code::
    info = get_symbol_info(client, 'BNBUSDT')

Get Futures Data
-----------------
Alongside Spot functionality, the library supports retrieval and operation in the Binance Futures Market. It is possible to access futures Timeseries data through
the provided functions. 
The :code:`get_FutureKlines()` function works exactly like the :code:`get_SpotKline()` described above.

.. code-block::

    BNB_PERP = CSuite.get_FutureKlines(client, 'BNBUSDT', '1d')

Get Futures-Spot Spread
************************
We have bundled the functionality of comparing the Spot and Futures by 
downloading and parsing both :code:`get_FutureKlines()` & :code:`get_SpotKline()`. This is possible via the following:

.. code-block::

    spread = get_FuturesSpread(client, 'BTCUSDT', '1m')

Get Futures Open Interest
**************************
The Open Interest statistic is available through Binance API and can be retived simply.

.. code-block::

    open_interest = get_FuturesOI(client, 'BTCUSDT', '30m')

Get Futures Long-Short
***********************

.. code-block::

    long_short = get_FuturesLS(client, 'BTCUSDT, period)

Get Futures Funding Rate
*************************

.. code-block::

    funding_rate = get_FuturesFundingRate(client, 'BTCUSDT', period)


Options Data
-----------------

Get Option Skew
*****************

.. code-block::

    skew = get_options_skew(client, maturity, strikes)`

Get Multiple Issue Skew
************************

.. code-block::

    data = get_omm_skew(client, [''], [''])

Options Vol Smirk
*******************

.. code-block::

    iv = IV_skew(data, price)
