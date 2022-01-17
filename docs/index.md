# CSuite
*CSuite is a Python library enabling easy integration with Binance API for crypto market data analysis, trade execution and portfolio managment.*


## Available Modules
**BConnector**: The BConnector module offers direct conectivity to the Binance API for data retrival. It offers a number of options for fast and formated data retrival. This serves as the key component offering data for static processes (backtesting, risk managment) as well as real-time processes. Use of the `client` object is necessary across the library.  

**Account Managment**: This module offers Account managment and monitoring capabilities, used to analyse a trading account with spot balance and/or trade history. Currently supporting monitoring (data retrival) just for Spot wallet but additional accounts coming soon. 


# Documentation

## Available BConnector Functions

#### connect_client(filename)
The connect client function takes a formated JSON file as input and returns a Binance client object. This returned object is necessary input in most following functions.

### Spot
#### get_SpotKlines(client,symbol,interval)
Requires client (above), symbol in Binance ('BTCUSDT') pair format and, interval ('1m','5m','30m'...'3d'). Returns pandas DataFrame Timeseries. 

#### batch_historic(client, symbols, interval, mode)
This function downloads historic data for multiple pairs at the same time, it works exactly the same as *get_SpotKlines* but requires mode field and symbols to be an *array* **NOT** *string*. The mode changes the return format.
##### Modes available:
1. Nominal ('N'): Returns timeseries of nominal prices
2. Return ('R'): Returns timeseries of *pct_change()* of prices
3. Volatility ('V'): Returns timeseries of rolling 7-day standard deviation of returns

### Futures
#### get_FuturesKlines(client, symbol, interval)
First of the futures functions, works like *get_SpotKlines(client,symbol,interval)* but returns Binance futures prices.

#### get_FuturesSpread(client, symbol, interval):
This function returns the Spread between the futures and spot in % terms (already multiplied) for the last 100 data-points.

#### get_FuturesOI(client, symbol, interval):
This function returns the futures Open Interest for the last 100 data-points of the specified interval. 
