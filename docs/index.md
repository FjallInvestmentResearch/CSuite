# CSuite
*CSuite is a Python library enabling easy integration with Binance API for crypto market data analysis, trade execution and portfolio managment.*


## Available Modules
**BConnector**: The BConnector module offers direct conectivity to the Binance API for data retrival. It offers a number of options for fast and formated data retrival. This serves as the key component offering data for static processes (backtesting, risk managment) as well as real-time processes. Use of the `client` object is necessary across the library.  

**Account Managment**: This module offers Account managment and monitoring capabilities, used to analyse a trading account with spot balance and/or trade history. Currently supporting monitoring (data retrival) just for Spot wallet but additional accounts coming soon. 

