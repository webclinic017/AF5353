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
data = pd.DataFrame(symbol_dict)

# Historical chart and return distribution
(data / data.iloc[0]*100).plot(figsize=(10, 6))
rets = np.log(data / data.shift(1))
rets.hist(bins=40, figsize=(10, 6));


#########################################################
### Step 2                                             ##   
### Investment Opportunity Sets                        ##
#########################################################


def port_ret(weights):
    return weights.T @ rets.mean()*252

def port_vol(weights):
    return (weights.T @ rets.cov() @ weights * 252)**0.5

noa = len(symbols) # noa = number of assets

prets = []
pvols = []
for p in range (2500):  #Assume the number of simulation (here 2500 but better to have > 100,000)
    weights = np.random.random(noa) 
    weights /= np.sum(weights)
    prets.append(port_ret(weights))
    pvols.append(port_vol(weights))
prets = np.array(prets)
pvols = np.array(pvols)

plt.figure(figsize=(10, 6))
plt.scatter(pvols, prets, c=(prets-risk_free_rate) / pvols, marker='o', cmap='coolwarm')
plt.plot(rets.std()*math.sqrt(252), rets.mean()*252, 'y.', markersize=15.0)
plt.xlabel('expected volatility')
plt.ylabel('expected return')
plt.colorbar(label='Sharpe ratio');

print(f'Volatiltiy: \n{(rets.std()*math.sqrt(252)).round(4)} \n\nReturn: \n{(rets.mean()*252).round(4)} \n\nCorrelation: \n{rets.corr().round(4)}')



#########################################################
### Step 3                                             ##   
### Efficient Frontier                                 ##
#########################################################

import scipy.optimize as sco


# Minium Variance Portfolio
bnds = tuple((0, 1) for x in range(noa))
cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
eweights = np.array(noa * [1. / noa,])
optv = sco.minimize(port_vol, eweights, method='SLSQP', bounds=bnds, constraints=cons)


# Efficient Frontier => Find min vol at each target return
cons = ({'type': 'eq', 'fun': lambda x: port_ret(x) - tret},
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
bnds = tuple((0, 1) for x in range(noa))

min_return = port_ret(optv['x'])
max_return = np.max(rets.mean()*252)

trets = np.linspace(min_return, max_return, 50)
tvols = []
for tret in trets:
    res = sco.minimize(port_vol, eweights, method='SLSQP', bounds=bnds, constraints=cons)
    tvols.append(res['fun'])
tvols = np.array(tvols)

plt.figure(figsize=(10, 6))
plt.scatter(pvols, prets, c=(prets-risk_free_rate) / pvols, marker='.', alpha=0.8, cmap='coolwarm')
plt.plot(tvols, trets, 'b', lw=4.0)
plt.plot(port_vol(optv['x']), port_ret(optv['x']), 'r*', markersize=15.0)
plt.plot(rets.std()*math.sqrt(252), rets.mean()*252, 'y.', markersize=15.0)
plt.grid(True)
plt.xlabel('expected volatility')
plt.ylabel('expected return')
plt.colorbar(label='Sharpe ratio');

print('At MVP, \nVol:', port_vol(optv['x']).round(3), '\nReturn:', port_ret(optv['x']).round(3), \
      '\nSharpe Ratio:', ((port_ret(optv['x'])-risk_free_rate) / port_vol(optv['x'])).round(3), '\nWeights:', optv['x'].round(3))



#########################################################
### Step 4                                             ##   
### Optimal Risk Portfolio and Capital Market Line     ##
#########################################################


# Optimal Risk Portfolio (ORP)
def min_func_sharpe(weights):
    return -(port_ret(weights)-risk_free_rate) / port_vol(weights)

bnds = tuple((0, 1) for x in range(noa))
cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
eweights = np.array(noa * [1. / noa,])
opts = sco.minimize(min_func_sharpe, eweights, method='SLSQP', bounds=bnds, constraints=cons)

print('At ORP \nVol:', port_vol(opts['x']).round(3), '\nReturn:', port_ret(opts['x']).round(3), \
      '\nSharpe Ratio:', ((port_ret(opts['x'])-risk_free_rate) / port_vol(opts['x'])).round(3), '\nWeights:', opts['x'].round(3))


# Capital Market Line (CML) 
import scipy.interpolate as sci

ind = np.argmin(tvols)
evols = tvols[ind:]
erets = trets[ind:]

tck = sci.splrep(evols, erets)

def f(x):
    ''' Efficient frontier function (splines approximation). '''
    return sci.splev(x, tck, der=0)
def df(x):
    ''' First derivative of efficient frontier function. '''
    return sci.splev(x, tck, der=1)

def equations(p, rf=risk_free_rate):
    eq1 = rf - p[0]
    eq2 = rf + p[1] * p[2] - f(p[2])
    eq3 = p[1] - df(p[2])
    return eq1, eq2, eq3

a = risk_free_rate
b = (port_ret(opts['x'])-risk_free_rate) / port_vol(opts['x']) 
x = port_ret(opts['x'])
opt = sco.fsolve(equations, [a, b, x]) ## Initial guess for opt = a+bx

plt.figure(figsize=(10, 6))
plt.scatter(pvols, prets, c=(prets - risk_free_rate) / pvols, marker='.', cmap='coolwarm')
plt.plot(evols, erets, 'b', lw=4.0)
cx = np.linspace(0.0, max_return+0.05) 
plt.plot(cx, opt[0] + opt[1] * cx, 'r', lw=1.5)
plt.plot(opt[2], f(opt[2]), 'y*', markersize=15.0)
plt.grid(True)
plt.axhline(0, color='k', ls='--', lw=2.0)
plt.axvline(0, color='k', ls='--', lw=2.0)
plt.plot(rets.std()*math.sqrt(252), rets.mean()*252, 'c.', markersize=15.0)
plt.xlabel('expected volatility')
plt.ylabel('expected return')
plt.colorbar(label='Sharpe ratio')


# Capital Market Line Formula
print(f'\nCapital Market Line is \nRp = {a} + {b.round(3)} * Volatility')