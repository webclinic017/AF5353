# install pandas-datareader package if you haven't before
# conda install -c anaconda pandas-datareader (if you use conda)
# pip install pandas-datareader (if you don't use conda)

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
df = pd.DataFrame(symbol_dict)
    
daily_ret = df.pct_change() 
annual_ret = daily_ret.mean() * 252
daily_cov = daily_ret.cov() 
annual_cov = daily_cov * 252
daily_std = daily_ret.std()
annual_std = daily_std*(252**0.5)


#########################################################
### Step 2                                             ##   
### Investment Opportunity Sets                        ##
#########################################################

port_ret = [] 
port_risk = [] 
port_weights = []

for _ in range(20000): 
    weights = np.random.random(len(symbols)) 
    weights /= np.sum(weights) 

    returns = np.dot(weights, annual_ret) 
    risk = np.sqrt(np.dot(weights, np.dot(annual_cov, weights))) 

    port_ret.append(returns) 
    port_risk.append(risk) 
    port_weights.append(weights) 
    
portfolio = {'Returns': port_ret, 'Risk': port_risk}
for i, s in enumerate(symbols): 
    portfolio[s] = [weight[i] for weight in port_weights]
df = pd.DataFrame(portfolio) 

df['SR'] = (df.Returns-risk_free_rate)/df.Risk 

df.plot.scatter(x='Risk', y='Returns', figsize=(8, 6), grid=True, c='SR', cmap='coolwarm')
plt.plot(annual_std, annual_ret, 'y.', markersize=15.0)
plt.title('Efficient Frontier') 
plt.xlabel('Risk') 
plt.ylabel('Expected Returns') 
plt.show() 
