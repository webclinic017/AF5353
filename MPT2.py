import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr

#########################################################
### Step 1                                             ##   
### Select your assets, data range and risk-free rate  ##
#########################################################


symbols = ['AAPL', 'MSFT', 'SPY', 'GLD']
start_date = '2010-01-04'
end_date = '2018-06-29'
risk_free_rate= 0.01

symbol_dict = {}
for symbol in symbols:
    symbol_df = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
    symbol_dict[symbol] = symbol_df["Adj Close"]
