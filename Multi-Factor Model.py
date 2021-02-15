### Step 1. Import the libraries:
import pandas as pd
import yfinance as yf
import statsmodels.formula.api as smf
import pandas_datareader.data as web


### Step 2. Specify the risky asset and the time horizon:
RISKY_ASSET = 'AMZN'
START_DATE = '2013-12-31'
END_DATE = '2018-12-31'


### Step 3. Download the risk factors from prof. French's website:
# three factors
df_three_factor = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start=START_DATE, end=END_DATE)[0]
df_three_factor.index = df_three_factor.index.format()
# momentum factor
df_mom = web.DataReader('F-F_Momentum_Factor', 'famafrench', start=START_DATE, end=END_DATE)[0]
df_mom.index = df_mom.index.format()
# five factors
df_five_factor = web.DataReader('F-F_Research_Data_5_Factors_2x3', 'famafrench', start=START_DATE, end=END_DATE)[0]
df_five_factor.index = df_five_factor.index.format()


### Step 4. Download the data of the risky asset from Yahoo Finance:
asset_df = yf.download(RISKY_ASSET, start=START_DATE, end=END_DATE, adjusted=True, progress=False)


### Step 5. Calculate the monthly returns:
y = asset_df['Adj Close'].resample('M').last().pct_change().dropna()
y.index = y.index.strftime('%Y-%m')
y.name = 'return'


### Step 6. Merge the datasets for the four-factor model:
# join all datasets on the index
four_factor_data = df_three_factor.join(df_mom).join(y)

# rename columns
four_factor_data.columns = ['mkt', 'smb', 'hml', 'rf', 'mom', 'rtn']

# divide everything (except returns) by 100
four_factor_data.loc[:, four_factor_data.columns != 'rtn'] /= 100

# calculate excess returns
four_factor_data['excess_rtn'] = four_factor_data.rtn - four_factor_data.rf


### Step 7. Merge the datasets for the five-factor model:
# join all datasets on the index
five_factor_data = df_five_factor.join(y)

# rename columns
five_factor_data.columns = ['mkt', 'smb', 'hml', 'rmw', 'cma', 'rf', 'rtn']

# divide everything (except returns) by 100
five_factor_data.loc[:, five_factor_data.columns != 'rtn'] /= 100

# calculate excess returns
five_factor_data['excess_rtn'] = five_factor_data.rtn - five_factor_data.rf


### Step 8-1. Estimate the four-factor model:
four_factor_model = smf.ols(formula='excess_rtn ~ mkt + smb + hml + mom', data=four_factor_data).fit()
print(four_factor_model.summary())


### Step 8-2. Estimate the five-factor model:
five_factor_model = smf.ols(formula='excess_rtn ~ mkt + smb + hml + rmw + cma', data=five_factor_data).fit()
print(five_factor_model.summary())
