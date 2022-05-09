BConnector
===================================
The BConnector module acts as the API interface between custom CSuite functionality and the Binance Exchange.
Connectivity with Binance is achieved via the `binance-python library <https://python-binance.readthedocs.io/en/latest/index.html#>`_ developed by Sam McHardy; thank you Sam!

The API Client
--------------
The object which enables API calls is the :code:`client` which is derived from a connection via the binance-python lib.
The client can be used to connect with the exchange and send, recive data ad-hoc or in real-time and is necessary for most connected functionality such
as data retrival and order submission. A client can be easily created:

:code:`client = CSuite.connect_client('filename.json')`

To initiate the client one must provide a JSON file with the two API keys for Binance, indexed as 'API KEY' and 'SECRET KEY'.
Once the client has been called succesfully by providing up-to-date keys, the returned client object must be kept for later use.

Get Spot Timeseries
--------------------------
Downloading timeseries (OCHL) data for a specific crypto made extremely easy through the Kline function, which returns a Pandas DataFrame
with all the data: OCHL & Volume. The client is a required parameter, so is the symbol (Binance pair notation) and the interval which can be from
'1m' to '4d'. Please note that this function will return the latest 1000 data-points. 

:code:`BTC = CSuite.get_SpotKlines(client, 'BTCUSDT', '1d')`

Get Multiple Spot Timeseries
*****************************
Since users often find themselves needing to download multiple timeseries at the same time, we provide the custom :code:`get_batch_historic()` function.
This function allows the download of parrallel historical timeseries data for multiple crypto. Unlike the :code:`get_SpotKline()` function, this one requires an array of strings in the symbols parameter. 
It also supports multiple modes through the mode parameter, the following is supported:

* Nominal - Closing Price ('N')
* Return - Daily Closing % Return ('R')
* Volatility - Rolling 5-day Standard Deviation ('V')


:code:`frame = CSuite.get_batch_historic(client, ['BTCUSDT', 'ADAUSDT'], '1d', 'N')`

Get Futures Data
-----------------
Alongside Spot functionality, the library supports retrival and operation in the Binance Futures Market. It is possible to access futures Timeseries data through
the provided functions. 

:code:`BTC_PERP = CSuite.get_FutureKlines(client, 'BNBUSDT', '1d')`

Get Futures-Spot Spread
************************
The connection to both futures & spot markets on Binance, it may be useful to monitor the spread. This is possible via the following:

:code:`spread = get_FuturesSpread(client, 'BTCUSDT', '1m')`

Get Futures Open Interest
**************************

:code:`open_interest = get_FuturesOI(client, 'BTCUSDT', '30m')`

Get Futures Long-Short
***********************

:code:`long_short = get_FuturesLS(client, 'BTCUSDT, )`

Get Futures Funding Rate
*************************

:code:`funding_rate = get_FuturesFundingRate(client, 'BTCUSDT', )`


Options Data
-----------------

Get Option Skew
*****************

:code:`skew = get_options_skew(client, maturity, strikes)`