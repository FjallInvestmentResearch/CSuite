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


**Requires:** *symbol*, *interval*

**Returns:** *Self*

This method passes data into the :code:`data` field using the :code:`get_SpotKlines()` to download OCHL data. It 
requires the *symbol* and *interval* like the pre-mentioned funcion.


Slice
********
.. code::

    TimeSeries = TimeSeries.slice(col)

**Requires:** *col*

**Returns:** *self* 

This method changes the *col* parameter of the :code:`TimeSeries` object which dictates which column of the DataFrame passed in
*data* is used to make the singular TimeSeries for calculations. 

Summarize
***********
.. code::
    
    summary = TimeSeries.summarize(period=365)

**Requires:** *period*

**Returns:** *Pandas DataFrame*

The :code:`summary()` method returns a formatted DataFrame of summary statistics for the timeseries. 

+--------+------------+--------+---------+-------------+--------+------+----------+
| Return | Volatility | Sharpe | Sortino | MaxDrawDown | Calmar | Skew | Kurtosis |
+--------+------------+--------+---------+-------------+--------+------+----------+

Linear Regression
******************
.. code:: 

    est = TimeSeries.lin_reg(period=365)

**Requires:** *period*

**Returns:** *float*

Seasonality
************
.. code:: 

    szn = TimeSeries.seasonality()

**Requires:** *None*

**Returns:** *Pandas DataFrame*

Autocorrelation
****************
.. code:: 

    acf = TimeSeries.autocorrelation(period=365, lags=50, diff=False)

**Requires:** *period*, *lags*, *diff*

**Returns:** *Pandas DataFrame*

A.D. Fuller
************
.. code:: 

    adf = TimeSeries.adfuller(maxlags=5, mode='L', regression='ct')

**Requires:** *maxlags*, *mode*, *regression*

**Returns:** *Pandas DataFrame*


Plotting Timeseries
-------------------


.. image:: plots/test.jpg
    :width: 50px
    :height: 150px

.. image:: plots/szn.jpg
    :width: 250px
    :height: 150px


Handling Portfolios
--------------------