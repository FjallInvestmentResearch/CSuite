CTester
=================

Handing Timeseries
-------------------
We provide a Timeseries wrapper in the :code:`TimeSeries` object which can be used
to atain information on a specified timeseries which can be passed normally as a pair OCHL or a custom pandas DataFrame.
Investigating the properties of investable timeseries has never been easier!

Initiating a Timeseries object is made possible by calling and then easily downloadin OCHL data for a 

.. code-block:: 

    timeSeries = TimeSeries(client, data=pd.DataFrame())

Contains object variables: client, data, col, symbol, interval 

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
    :width: 250px
    :height: 150px
    :align: right

This function enables plotting of a timeSeries and automates conversion into either *Returns* or
*Volatility* via the *mode* parameter. 

**Acceptable Modes**

* **Nominal** ('N')
* **Returns** ('R')
* **Volatility** ('V')


Quantile Plots
**************
.. code-block:: 

    Plotter(TimeSeries).plot_qq(period, mode, save)


.. image:: plots/qq.jpg
    :width: 250px
    :height: 150px

Seasonality Plot
*****************
.. code-block:: 

    Plotter(TimeSeries).plot_seasonality(save)


.. image:: plots/szn.jpg
    :width: 250px
    :height: 150px

Autocorrelation Plot
********************
.. code-block:: 

    Plotter(TimeSeries).plot_acf(period, lags, diff, save)

.. image:: plots/acf.jpg
    :width: 250px
    :height: 150px


Benchmark Plot
**************
.. code-block:: 

    Plotter(TimeSeries).benchmark(Benchmark, period, delta, save)

.. image:: plots/bnch.jpg
    :width: 250px
    :height: 150px


Handling Portfolios
--------------------