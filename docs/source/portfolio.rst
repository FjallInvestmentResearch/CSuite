CTester
=================

Handing Timeseries
-------------------
We provide a Timeseries wrapper in the :code:`TimeSeries` object which can be used
to atain information on a specified timeseries which can be passed normally as a pair OCHL or a custom pandas DataFrame.
Investigating the properties of investable timeseries has never been easier!

.. code-block:: 

    timeSeries = TimeSeries(client, data=pd.DataFrame())

A :code:`TimeSeries()` requires a :code:`client` object and an optional :code:`data` input to calculate values from. The TimeSeries can be
filled with the appropriate data using a custom pass argument on :code:`data` or via the standard :code:`download()` function. 
Each TimeSeries contains 5 internal variables these being:

+------------+------------+-----------+-----------+------------------------------------+
| **Name**   | **Type**   |**Example**|**Default**|  **Decription**                    |
+------------+------------+-----------+-----------+------------------------------------+
| *client*   | Client     | Object    |  None     | API client                         |
+------------+------------+-----------+-----------+------------------------------------+
| *data*     | DataFrame  | pd.frame  |  None     |pd.DataFrame containing TimeSeries  |
+------------+------------+-----------+-----------+------------------------------------+
| *col*      | String     |'adj_close'|  'close'  | Frame to Series pointer            |
+------------+------------+-----------+-----------+------------------------------------+
| *symbol*   | String     | 'BTCUSDT' |  None     |TimeSeries name                     |
+------------+------------+-----------+-----------+------------------------------------+
| *interval* | String     | '1d'      |  None     |Specifies timeseries interval       |
+------------+------------+-----------+-----------+------------------------------------+


Download
***********
.. code:: 

    timeSeries = TimeSeries.download(symbol, interval)


**Requires:** *str: symbol*, *str: interval*

**Returns:** *Self*

This method passes data into the :code:`data` field using the :code:`get_SpotKlines()` to download OCHL data. It 
requires the *symbol* and *interval* like the pre-mentioned funcion.


Slice
********
.. code::

    TimeSeries = TimeSeries.slice(col)

**Requires:** *str: col*

**Returns:** *self* 

This method changes the *col* parameter of the :code:`TimeSeries` object which dictates which column of the DataFrame passed in
*data* is used to make the singular TimeSeries for calculations. 

Summarize
***********
.. code::
    
    summary = TimeSeries.summarize(period=365)

**Requires:** *int: period*

**Returns:** *Pandas DataFrame*

The :code:`summary()` method returns a formatted DataFrame of summary statistics for the timeseries.

+--------+------------+--------+---------+-------------+--------+------+----------+
| Return | Volatility | Sharpe | Sortino | MaxDrawDown | Calmar | Skew | Kurtosis |
+--------+------------+--------+---------+-------------+--------+------+----------+

Linear Regression
******************
.. code:: 

    est = TimeSeries.lin_reg(period=365)

**Requires:** *int: period*

**Returns:** *float*

This method returns the estimated annualised returns using Linear Regression. 

Seasonality
************
.. code:: 

    szn = TimeSeries.seasonality()

**Requires:** *None*

**Returns:** *Pandas DataFrame*

This method returns a Panadas DataFrame with the average performed return by buissness month over the history of the timeSeries. 
This only works for intervals of '1d' or more. 

Autocorrelation
****************
.. code:: 

    acf = TimeSeries.autocorrelation(period=365, lags=50, diff=False)

**Requires:** *int: period*, *int: lags*, *bool: diff*

**Returns:** *Pandas DataFrame*

Returns autocorrrelation estimation across different lags as specified in the *lag* parameter.
Autocorrelation differencing is possible by enabling the *diff* parameter. 

A.D. Fuller
************
.. code:: 

    adf = TimeSeries.adfuller(maxlags=5, mode='L', regression='ct')

**Requires:** *int: maxlags*, *str: mode*, *str: regression*

**Returns:** *Pandas DataFrame*

This method performs the A.D. Fuller test using the `statsmodels adf module <https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.adfuller.html#statsmodels.tsa.stattools.adfuller>`_ 
and returns a Pandas DataFrame of relevant values as shown below. The regression input is directly related to the statsmodels implementation and represents the type of 
regression calculated.

+-----------+---------+------+--------+---------+----------+-----+
| ADF Value | P-Value | Lags | N Obs  | C.V. 1% | C.V. 10% | IC  |
+-----------+---------+------+--------+---------+----------+-----+

The A.D. Fuller test supports multiple price calculation methods, we have simplified the application
of Logarithmic price transformation for the test through the *mode* parameter.  

**Acceptable Modes**

* **Nominal** ('N'): Standard non-normalised price as downloaded via OCHL & sliced using *col*
* **Logarithmic** ('L'): Applies Logarithmic transformation to prices. 

.. note:: 

    We are working on implementing a Normalized Price Ratio (NPR) mode. 


Plotting Timeseries
-------------------

.. code-block:: 

    plotter = Plotter(TimeSeries, path)

TimeSeries Plots
****************
.. code-block:: 

    Plotter(TimeSeries).plot(period, mode, save)

.. image:: plots/test.jpg
    :width: 350px
    :height: 210px
    :align: left

This function enables plotting of a timeSeries and automates conversion into either *Returns* or
*Volatility* via the *mode* parameter. This is a simplified way to see the basic (Level I) timeseries data.

**Requires:** *int: period*, *str: mode*, *bool: save*

**Returns:** *Null*

**Acceptable Modes**

* **Nominal** ('N'): Plots the prices in standard nominal format.
* **Returns** ('R'): Plots the return as % gain/loss since period start.
* **Volatility** ('V'): Plots 7-day rolling standard deviation (Volatility) since period start.


Quantile Plots
**************
.. code-block:: 

    Plotter(TimeSeries).plot_qq(period, mode, save)

.. image:: plots/qq.jpg
    :width: 350px
    :height: 210px
    :align: left

This function plots *Quantile-Quantile* with reference to normal distributions for quick analysis of 
the Return or Volatility distributions. 

**Requires:** *int: period*, *str: mode*, *bool: save*

**Returns:** *Null*

**Acceptable Modes**

* **Returns** ('R'): Plots the distribution of returns.
* **Volatility** ('V'): Plots the distribution of volatility. 

Seasonality Plot
*****************
.. code-block:: 

    Plotter(TimeSeries).plot_seasonality(save)


.. image:: plots/szn.jpg
    :width: 350px
    :height: 210px
    :align: left

This function plots the seasonality statistic, i.e. the average performed monthly return of the timeseries. 
It shows a matplotlib barplot with relevant information which can be saved. 

**Requires:** *bool: save*

**Returns:** *Null*


Autocorrelation Plot
********************
.. code-block:: 

    Plotter(TimeSeries).plot_acf(period, lags, diff, save)

.. image:: plots/acf.jpg
    :width: 350px
    :height: 210px
    :align: left

This function plots the autocorrelation for specified lags; it can plot differenced autocorrelation by enabling the :code:`diff` parameter.
It shows a matplotlib stemplot which can be saved. 

**Requires:** *int: period*, *int: lags*, *bool: diff*, *bool: save*

**Returns:** *Null*

Benchmark Plot
**************
.. code-block:: 

    Plotter(TimeSeries).benchmark(benchmark, period, delta, save)

.. image:: plots/bnch.jpg
    :width: 350px
    :height: 210px
    :align: left

This function plots the specified timeseries against a benchmark timeseries. It may return the 1:1 spread (delta) between the two timeseries via 
the :code:`delta` parameter. It shows a matplotlib lineplot which can be saved.

**Requires:** *str: benchmark*, *int: period*, *bool: delta*, *bool: save*

**Returns:** *Null*


Handling Portfolios
--------------------
We have packaged additional functionality through the :code:`Portfolio` object which enables users to calculate performance analyses on portfolios. 
Through this object, it is possible to define and parameterise portfolio level quantitative data-points. This is also connected to the portoflio backtesting suite
via the :code:`MonteCarlo` engine. 

.. code-block:: 

    portfolio = Portfolio(client, symbols, weights, interval, download)

In the above statement, there is a simple definition of a portfolio, it contains a list of symbols and coresponding weights, a timeseries interval and a download check. 
First, the :code:`symbols` need always get passed and represent the basic parameter of the portfolio. Second, the :code:`weights` parameter needs to be an array of floats summing to 1; however,
if it ommitted it is automatically set to equal weighting across symbols. Third, the :code:`interval` paarameter represents the timeseries interval for the download, if the :code:`donwload` parameter is 
False then :code:`interval` is ommitted. In the cases where :code:`download` is false, the :code:`weights` & :code:`interval` may be ommitted. 

The input format for the :code:`data` parameter is a *Pandas DataFrame* with each column being a select single-variable timeseries of each asset, with the columns being the tickers. 

+------------+------------+-----------+-----------+------------------------------------+
| **Name**   | **Type**   |**Example**|**Default**|  **Decription**                    |
+------------+------------+-----------+-----------+------------------------------------+
| *client*   | Client     | Object    |  None     | API client                         |
+------------+------------+-----------+-----------+------------------------------------+
| *symbols*  |str array   |['ADAUSDT']|  None     |pd.DataFrame containing TimeSeries  |
+------------+------------+-----------+-----------+------------------------------------+
| *weights*  | float array|[0.3, 0.7] |  None     | Frame to Series pointer            |
+------------+------------+-----------+-----------+------------------------------------+
| *interval* | String     | '1d'      |  None     |Specifies timeseries interval       |
+------------+------------+-----------+-----------+------------------------------------+
| *download* | bool       | True      |  True     |  Download timeseries data or not?  |
+------------+------------+-----------+-----------+------------------------------------+


Calculte Equity Curve
**********************

Load Data
*********

Summarize
**********

Monte Carlo Engine
-------------------

Run Simulation
***************

Efficient Frontier
******************