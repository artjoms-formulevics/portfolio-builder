#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 15:49:18 2020

@author: afo
"""
import pandas as pd  
import pandas_datareader as pdr
import os
from os.path import abspath
from inspect import getsourcefile

def load_data(portfolio, start_time, end_time):
        
    p = abspath(getsourcefile(lambda:0))
    p = p.rsplit('/', 1)[0]
    os.chdir(p)
    print('Working Directory is: %s' % os.getcwd())
    
    # Read csv stored weights
    portfolio = portfolio[portfolio.allocation_weight != 0]  # ignoring zero weights
    stock = portfolio.index.tolist()
    
    # Getting the S&P500 (benchmark)
    data = pdr.DataReader('^GSPC', 'yahoo', start_time, end_time)['Close']
    data = data.rename('SP500')
    data = data.to_frame()
    
    # Getting stock data (maybe re-do to for loop, if there be problems with memory)
    temp = pdr.DataReader(stock, 'yahoo', start_time, end_time)['Close']
    data = data.join(temp)
    del temp
    
    return portfolio, data
    

# Function that cretes a test portfolio based on the optimization results
def create_index(start_time, end_time, start_of_investment, portfolio_name, portfolio, data_new):
    
    p = abspath(getsourcefile(lambda:0))
    p = p.rsplit('/', 1)[0]
    os.chdir(p)
    print('Working Directory is: %s' % os.getcwd())
    
    # Portfolio size
    portfolio_size = 1
    
    # Getting starting of investment point. 
    inv_start = data_new.loc[[start_of_investment]].T  # prices of securities at the starting date, i.e. buy price
    inv_start = inv_start[1:]
    inv_start.columns = [*inv_start.columns[:-1], 'buy_price']
    inv_start['ticker'] = inv_start.index
    
    # Get S&P data starting at the investoment point
    tracked_sp500 = data_new['SP500'].to_frame()
    tracked_sp500 = tracked_sp500.loc[start_of_investment:]
    
    # Get the value of the S&P index at the starting date, to see the amount of investment, to compare it then to S&P
    portfolio_size = tracked_sp500.iloc[0,0]
    
    # Get the price to be paid for each security, plus the number (fraction) of shares bought
    portfolio['ticker'] = portfolio.index
    portfolio['buy_investment'] = (portfolio['allocation_weight']) * portfolio_size # money to be invested in to each security
    portfolio = pd.merge(portfolio, inv_start, on='ticker', how='outer')  # add buy price
    portfolio['shares_bought'] = portfolio['buy_investment'] / portfolio['buy_price']  # get the fraction of shares bought
    
    # Separate shares bought values
    portfolio_shares = portfolio['shares_bought'].to_frame().T
    
    # Get the tracked portfolio without S&P
    tracked_portfolio = data_new.loc[start_of_investment:]
    del tracked_portfolio['SP500']
    
    # Get the exact value of each security in the portfolio in each time point
    tracked_portfolio = tracked_portfolio * portfolio_shares.values 
    tracked_portfolio['total'] = tracked_portfolio.sum(axis=1)  # get total value
    total_portfolio = tracked_portfolio.join(tracked_sp500)  # bring back S&P
    
    # Rearrange cols
    cols = total_portfolio.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    total_portfolio = total_portfolio[cols]
    
    # Write portfolio to the file & separate file with weightrs & other data
    total_portfolio.to_csv(p + '/portfolios/portfolio_' + portfolio_name + '.csv')
    portfolio.to_csv(p + '/portfolios/portfolio_weights_' + portfolio_name + '.csv')
    
    return total_portfolio, portfolio

def create_portfolio(start_of_investment, portfolio_name, portfolio, data_new):
    
    p = abspath(getsourcefile(lambda:0))
    p = p.rsplit('/', 1)[0]
    os.chdir(p)
    print('Working Directory is: %s' % os.getcwd())
    
    data_new = data_new[:1]
    
    # Getting starting of investment point. 
    inv_start = data_new.loc[[start_of_investment]].T  # prices of securities at the starting date, i.e. buy price
    inv_start = inv_start[1:]
    inv_start.columns = [*inv_start.columns[:-1], 'buy_price']
    inv_start['ticker'] = inv_start.index
    
    # Get the price to be paid for each security, total amount to be invested
    portfolio['ticker'] = portfolio.index
    portfolio = pd.merge(portfolio, inv_start, on='ticker', how='outer')  # add buy price
    portfolio['buy_investment'] = portfolio['allocation_discrete'] * portfolio['buy_price'] # money to be invested in to each security
    portfolio['actual_allocation'] = portfolio['buy_investment'] / portfolio['buy_investment'].sum()
    
    # Write portfolio to the file & separate file with weightrs & other data
    portfolio.to_csv(p + '/portfolios/portfolio_investment_' + portfolio_name + '.csv')
    
    return portfolio