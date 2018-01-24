import datetime as dt
import pandas as pd
import numpy as np
import scipy.optimize as spo
import util 
from util import *

def normalize_data(df):
    return df/ df.ix[0,:]
    
def compute_daily_returns(df):
    daily_returns = (df/df.shift(1)) -1
    daily_returns.ix[0] = 0 #has some issues, only works with one column as is
    return daily_returns
    
def calculate_sharpe_ratio(allocs, normed_data): 

    alloced = normed_data*allocs
    port_val = alloced.sum(axis=1)
    daily_returns = compute_daily_returns(port_val)
    sddr = daily_returns.std()
    sr = ((daily_returns).mean()/sddr)*(252.**(1./2)) #computes sharpe ratio
    return sr*-1 # maximize sr

def calculate_portfolio_statistics(sd, ed, syms, allocs, sv, rfr, sf, gen_plot): 
    normed_data = normalize_data(get_data(syms, sd, ed))
    alloced = normed_data*allocs 
    port_val = (alloced * sv).sum(axis=1) #the portfolio value on a given date
    daily_returns = compute_daily_returns(port_val)
    
    cr = (port_val[-1]/port_val[0])-1 #the cumulative return for the portfolio, 
    adr = daily_returns.mean() #the average daily return
    sddr = daily_returns.std() #standard deviation of daily returns
    dailyrfr = ((1.0 + rfr)**(1./sf))-1. #the daily risk free rate
    sr = ((daily_returns - dailyrfr).mean()/sddr)*(sf**(1./2)) #sharpe ratio is Rp - Rf / stdp
    er = (1+cr) * sv #the cumulative return times the start value
    return cr, adr, sddr, sr, er #return so they can be accessed and worked with if necessary


def calculate_optimum_portfolio(sd, ed, syms, gen_plot):
    normed_data = normalize_data(get_data(syms, sd, ed))
    
    guess_allocs = [(1./len(syms))] *len(syms) #just guess all the same allocations for initial guess
    bnds = ((0.,1.),) * len(syms) #make sure all allocations are between 0 and 1
    
    allocs = spo.minimize(calculate_sharpe_ratio, guess_allocs, args = (normed_data,), \
        method='SLSQP', options = {'disp':True}, bounds = bnds, \
        constraints = ({ 'type': 'eq', 'fun': lambda allocs: 1.0 - np.sum(allocs) })) #make sure allocations sum up to 1
    
    cr,adr,sddr,sr,er = calculate_portfolio_statistics(sd, ed, syms, allocs.x,1,0,252,False)   #use 1 as startvalue, 0 as rfr, and 252 as sampling frequency
    
    print ("Computed Sharpe Ratio:", sr)
    print ("Volatility:", sddr)
    print ("Cumulative Return:", cr)
    print ("Average Daily Return:", adr)
    return allocs.x,cr,adr,sddr,sr
    
def test_run():
    budget = 1000
    sd = dt.datetime(2017,1,23)
    ed = dt.datetime(2018,1,23)
    gen_plot=True
    data = get_data(get_SPTickers(),sd,ed)
    syms = list(data)
    allocs, cr, adr, sddr, sr = \
    calculate_optimum_portfolio(sd, ed, syms, gen_plot)

    stocks = []
    for i in range(len(allocs)):
        if allocs[i] > 0.01:
            stocks.append(syms[i])
    printer = dict()
    print(stocks)
    for i in range(len(syms)):
        if syms[i] in stocks:
            printer[syms[i]] = allocs[i] * budget
    frame = pd.Series(printer, name = 'Allocations')
    print(frame)

if __name__ == "__main__":
    test_run()