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

Get Spot Timeseries (OCHL)
--------------------------
Downloading timeseries (OCHL) data for a specific crypto made extremely easy through the Kline function, which returns a Pandas DataFrame
with all the data: OCHL & Volume. The client is a required parameter, so is the symbol (Binance pair notation) and the interval which can be from
'1m' to '4d'. Please note that this function will return the latest 1000 data-points. 

:code:`BTC = CSuite.get_SpotKlines(client, 'BTCUSDT', '1d')`


