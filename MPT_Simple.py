# install pandas-datareader package if you haven't before
# conda install -c anaconda pandas-datareader (if you use conda)
# pip install pandas-datareader (if you don't use conda)

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()


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
df = pd.DataFrame(symbol_dict)

# Historical chart 
(df / df.iloc[0]*100).plot(figsize=(10, 6))

# choose log_return or simple_return 
daily_ret = np.log(df / df.shift(1)) 
#daily_ret = df.pct_change() 
    
annual_ret = daily_ret.mean() * 252
daily_cov = daily_ret.cov() 
annual_cov = daily_cov * 252
daily_std = daily_ret.std()
annual_std = daily_std*(252**0.5)


#########################################################
### Step 2                                             ##   
### Investment Opportunity Sets, MVP, ORP              ##
#########################################################

port_ret = [] 
port_risk = [] 
port_weights = []

for _ in range(20000): 
    weights = np.random.random(len(symbols)) 
    weights /= np.sum(weights) 

    returns = weights.T @ annual_ret 
    risk = (weights.T @ annual_cov @ weights)**0.5 
    
    port_ret.append(returns) 
    port_risk.append(risk) 
    port_weights.append(weights) 
    
portfolio = {'Returns': port_ret, 'Risk': port_risk}
for i, s in enumerate(symbols): 
    portfolio[s] = [weight[i] for weight in port_weights] 
df = pd.DataFrame(portfolio) 
df['Sharpe'] = (df.Returns-risk_free_rate)/df.Risk 

max_sharpe = df.loc[df['Sharpe']==df['Sharpe'].max()]
min_risk = df.loc[df['Risk']==df['Risk'].min()]


plt.figure(figsize=(10, 6))
plt.scatter(port_risk, port_ret, c=sharpe_ratio, marker='.', cmap='coolwarm')
plt.scatter(max_sharpe['Risk'], max_sharpe['Returns'], c='r', marker='*', s=300) 
plt.scatter(min_risk['Risk'], min_risk['Returns'], c='r', marker='X', s=200)
plt.plot(annual_std, annual_ret, 'y.', markersize=15.0)
plt.grid()
plt.title('Portfolio Optimization') 
plt.xlabel('Expected Volatility')
plt.ylabel('Expected Return')
plt.colorbar(label='Sharpe ratio');

# type to find portfolio weights
max_sharpe
min_risk

