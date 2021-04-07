import pandas as pd
import yfinance as yf
import pandas_datareader
import pandas_datareader.data as web

## Step 1. Define the data period
START_DATE = '2000-01-01'
END_DATE = '2020-12-31'


### Step 2. Download the risk factors from prof. French's website:

df_five_factor = web.DataReader('F-F_Research_Data_5_Factors_2x3', 'famafrench', start=START_DATE, end=END_DATE)[0]
df_mom = web.DataReader('F-F_Momentum_Factor', 'famafrench', start=START_DATE, end=END_DATE)[0]
result = pd.merge(df_five_factor, df_mom, left_index=True, right_index=True)
result.drop(['RF'], axis=1).corr().round(4)


## You can check the available data from french library and add to your correlation calculation 
pandas_datareader.famafrench.get_available_datasets()
