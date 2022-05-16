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

**Setup File Example**

.. code:: JSON

    {
    "API_KEY" : "YOUR_API_KEY_HERE",
    "SECRET_KEY" : "SECRET_KEY_HERE"
    }
    


Get Spot Timeseries
--------------------------
.. code-block::

    timeSeries = CSuite.get_SpotKlines(client, symbol, interval)

Downloading timeseries (OCHL) data for a specific crypto made extremely easy through the Kline function, which returns a Pandas DataFrame
with all the data: OCHL & Volume. The client is a required parameter, so is the symbol (Binance pair notation) and the interval which can be from
'1m' to '4d'. Please note that this function will return the latest 1000 data-points.

**Requires:** *obj: client*, *str: symbol*, *str: interval*

**Returns:** *Pandas DataFrame*



Get Multiple Spot Timeseries
*****************************
.. code-block::

    frame = CSuite.get_batch_historic(client, symbols, interval, mode')

Since users often find themselves needing to download multiple timeseries at the same time, we provide the custom :code:`get_batch_historic()` function.
This function allows the download of parrallel historical timeseries data for multiple crypto. Unlike the :code:`get_SpotKline()` function, this one requires an array of strings in the symbols parameter.
It also supports multiple modes through the mode parameter, the following is supported:

* **Nominal** ('N'): Returns the non-normalised closing price of the pair. 
* **Return** ('R'): Returns the daily percentage returns of the price timeseries. 
* **Volatility** ('V'): Return the 5-Day rolling standard deviation of returns. 

**Requires:** *obj: client*, *array of str: symbols*, *str: interval*, *str: mode*

**Returns:** *Pandas DataFrame*



Get Quote & Limit Order Book
----------------------------

Viewing the Orderbook
**********************
.. code::

    book = CSUite.view_book(client, symbol, limit=100)

Retrieving the live limit order book (LOB) is the first step in accessing the real time market on the exchange. Using this limit order
book functionality it is possible to have near-real time access to the access via equivalent DMA. The Binance API has a refresh rate of
200ms for the book.

We can simply call the :code:`view_book()` function to get a snapshot of the book. It returns a
ladder-like DataFrame with bid/ask volumes in num of tokens and Prices. The ticks are NOT uniform.

**Requires:** *obj: client*, *str: symbol*, *int: limit*

**Returns:** *Pandas DataFrame*


Get Quote
**********
.. code-block::

    quote  = CSuite.get_quote(client, symbol)

In certain use cases it may be useful to access only the best bid ask & volume at those ticks
in such cases we offer a parsed version of the book function via :code:`get_quote()` which directly interacts
with the Binance API for high speeds.

**Requires:** *obj: client*, *str: symbol*

**Returns:** *Pandas DataFrame*


Getting Symbol Trade Parameters
*********************************
.. code-block::
   
    info = get_symbol_info(client, symbol)

We have also created a simplified way to parse the Exchange information necessary to execute automated trading
details such as the trading status, tickSize, and minimum notional are included.

**Requires:** *obj: client*, *str: symbol*

**Returns:** *Pandas DataFrame*

Get Futures Data
-----------------
.. code-block::

    future = CSuite.get_FutureKlines(client, symbol, interval)

Alongside Spot functionality, the library supports retrieval and operation in the Binance Futures Market. It is possible to access futures Timeseries data through
the provided functions. 
The :code:`get_FutureKlines()` function works exactly like the :code:`get_SpotKline()` described above.

**Requires:** *obj: client*, *str: symbol*, *str: interval*

**Returns:** *Pandas DataFrame*

Get Futures-Spot Spread
************************
.. code-block::

    spread = get_FuturesSpread(client, symbol, interval)

We have bundled the functionality of comparing the Spot and Futures by 
downloading and parsing both :code:`get_FutureKlines()` & :code:`get_SpotKline()`. This is possible via the following:

**Requires:** *obj: client*, *str: symbol*, *str: interval*

**Returns:** *Pandas DataFrame*

.. note:: 

    The term :code:`period` in the following functions refers to the special interval of derivative statistics which includes the values
    [5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d]

Get Futures Open Interest
**************************
.. code-block::

    open_interest = get_FuturesOI(client, symbol, period)

The `Open Interest <https://en.wikipedia.org/wiki/Open_interest>`_ statistic refering to the volume of currently open contracts is available through Binance API and 
can be retived simply using the relevant function.

**Requires:** *obj: client*, *str: symbol*, *str: period*

**Returns:** *Pandas DataFrame*

Get Futures Long-Short
***********************

.. code-block::

    long_short = get_FuturesLS(client, symbol, period)

The `Long-Short <https://www.investopedia.com/terms/l/longshort-ratio.asp#:~:text=than%20for%20purchases.-,The%20long%2Dshort%20ratio%20represents%20the%20amount%20of%20a%20security,ratio%20indicating%20positive%20investor%20expectations.>`_ statistic of the Binance futures portfolios is also easily accessible as a timeseries.
This function returns a DataFrame which contains the Accounts, Position and standard Long/Short Ratio as per Binance
Docs.

**Requires:** *obj: client*, *str: symbol*, *str: period*

**Returns:** *Pandas DataFrame*

Get Futures Funding Rate
*************************

.. code-block::

    funding_rate = get_FuturesFundingRate(client, symbol, period)

The Futures Funding Rate of the Binance Exchange (i.e. the cost of going long futures), is also packaged. 

**Requires:** *obj: client*, *str: symbol*, *str: period*

**Returns:** *Pandas DataFrame*

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
