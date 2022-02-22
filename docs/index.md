# CSuite
*CSuite is a Python library enabling easy integration with Binance API for crypto market data analysis, trade execution and portfolio managment.*


## Available Modules
**BConnector**: The BConnector module offers direct conectivity to the Binance API for data retrival. It offers a number of options for fast and formated data retrival. This serves as the key component offering data for static processes (backtesting, risk managment) as well as real-time processes. Use of the `client` object is necessary across the library.  

**Account Managment**: This module offers Account managment and monitoring capabilities, used to analyse a trading account with spot balance and/or trade history. Currently supporting monitoring (data retrival) just for Spot wallet but additional accounts coming soon. 


# Documentation

## BConnector Functions

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

#### get_LiveSpread(client, symbol)
Returns current spot-futures sprad of pair in % terms, due to API limitations futures price is 5m average; please do not use this to trade in real-time.

#### get_FuturesLS(client, symbol, period)
Returns futures long-short ratio of pair in DataFrame format with 3 columns (Long (%), SHort (%), Long/Short Ratio).

#### get_FuturesFundingRate(client, ticker, period)
Returns futures funding rate (max 8h interval) as DataFrame.

### Options
#### get_options_skew(client, maturity, strikes)
This function downloads BTC Vanillia Option data from Binance API. Requires single maturity and strike in String format. Returns DataFrame with Columns: *'strike', 'direction', 'bidIV', 'askIV', 'delta', 'gamma', 'theta', 'vega'*.

**Binance Maturity Format**: YYMMDD -> e.g. 24/12/21 = 211224


#### get_omm_skew(client, maturities, strikes):
This function downloads BTC Vanillia Option data from Binance API. Requires multiple maturities and strikes in Array format. This function enables batch Options data download, all strikes for a maturity must be present.
Returns DataFrame with Columns: *'strike', 'direction', 'bidIV', 'askIV', 'delta', 'gamma', 'theta', 'vega'*.

**Example Call:**
`multi_expiry_skew = csuite.get_omm_skew(client,['211224','211231','220128'],[['35000','40000','42000','44000','46000','48000','50000','52000','54000','56000','58000','60000','65000','70000'],['32000','36000','40000','44000','48000','52000','56000','60000','65000','75000','80000'],
['30000','35000','40000','45000','50000','55000','60000','65000','70000','80000']])`

#### IV_skew(data, price)
This function transforms the output of *get_omm_skew* (data/table format) into a symetric put-call Implied volatility array. It returns an array with the IV of Puts under the price and IV of Calls over the price. As price, pass current price. 

## Account Managment Functions

### Spot Data

#### get_trade_history(client, symbol)
Calls client `get_my_trades()` function and converts JSON output into Pandas Frame. Returns order-book.
Shows executed (filled) order trading book for requested symbol.

#### adjust_fx_trades(client, symbol)
Calls `get_trade_history()` function for two currencies, one base and one FX; currently supporting USDT/EUR. Returns parsed order-book.
Shows the executed (filled) order trading book for the requested symbol for two currency pairs, all converted to base currency (USDT).

#### get_asset_status(client, symbol)
Calls `adjust_fx_trades()` function and parses response frame into a single status row with details on overall position performance. This reponse has 8 columns and describes the performance of retrived spot orders, with unrealized and realized gains. 
Show performance of asset in spot wallet by calulating purchase price from order book. *ISSUES RETRIVING BUY, SELL & CONVERSION via Pay system*.

#### get_account_snapshot(client, type):
Calls client `account_snapshot()` function and parses JSON into Pandas DataFrame. Returns snapshot (`snap`).
Shows current open spot balances in Binance wallet. 

#### get_spot_balances(client, snap):
Requires the snapshot from the *above* function as input, then runs `get_asset_status()` for listed assets and returns a built status frame. 
Shows status and performance of all assets present in snapshot. 

#### wallet_composition(client, snap):
Requires snapshot. Returns value weighted portfolio in Pandas DataFrame format. 

## Limit Order Book 

### Spot Order Book

#### view_book(symbol, client)
Directly interfaces with the API to get a snapshot of the Limit Order Book (LOB) at a depth of 100 ticks (defualt). It parses JSON response and returns DataFrame and timestamp string. The return frame is in three column ladder design with bid_volume, quote and, ask_volume. 

#### monitor_book(symbol, client, limit)
Function uses `view_book()` continously in a loop and returns LOB metrics: mid-point, spread, book balance, WA bid, WA ask, best bid. It 'monitors' the health of the book by writting down vitals in real-time. It works until it hits its loop limit specified by limit (int). 
