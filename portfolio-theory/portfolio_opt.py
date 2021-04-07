#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 11:18:37 2020

@author: afo
"""

import pandas as pd  
import numpy as np
import pandas_datareader as pdr
import pandas_market_calendars as mcal
import os
from os.path import abspath
from inspect import getsourcefile
from pypfopt.efficient_frontier import EfficientFrontier, objective_functions
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt.plotting import plot_weights, plot_covariance
from datetime import datetime, timedelta

# Custom function
from index_creation import create_index, create_portfolio, load_data


# Function that prints df (or anything else) without truncating it
def print_full(x):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', None)
    print(x)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')


p = abspath(getsourcefile(lambda:0))
p = p.rsplit('/', 1)[0]
os.chdir(p)
print('Working Directory is: %s' % os.getcwd())

# Get portfolio candidates from the file that was created by FA function
stock_list = pd.read_csv(p + '/stocks.csv')
stock_list = stock_list.reindex(sorted(stock_list.columns), axis=1)

weight_bounds_tuple =((0.0, 0.1),(0.0, 0.1),(0.0, 0.15),(0.0, 0.05),(0.0, 0.05),(0.01, 0.1))  # !!! Weights to be adjusted for every iteration by arbitrary value
filter_recent_stocks = [True, True, True, True, True, False]  # boolean to determine if need to filter recent stocks with low amount of data
discrete_algo_lp = [True, True, True, True, False, True]   # boolean to use LP for discrete allocation. Greedy alo if false
gamma = 0.05

total_portfolio_value = 20000

# Set timeframe for analysis (e.g. train set, seen data)
start_time = '2015-01-01'
end_time = '2020-01-01'

# Set timeframe to test the portfolio (e.g. unseen, new data)
# Should overlap by 1 day with train set
test_start_time = '2020-01-01'
#test_end_time = '2020-11-17'
test_end_time = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

# Add trading days tracker in the entire period, to ensure start end dates would be consistent
nyse = mcal.get_calendar('NYSE')
trading_days = nyse.valid_days(start_date=start_time, end_date=datetime.today() + timedelta(days=7))
trading_days =pd.Series(trading_days, name='days')
trading_days = trading_days.astype('str')
trading_days = trading_days.str.rsplit('+', expand=True).iloc[:,0]
trading_days.name = 'days'

# Adjust test end time if falls on a weekend/holiday
start_of_investment = test_end_time + " 00:00:00"
while np.any(start_of_investment in trading_days.values) ==  False:
           start_of_investment = (datetime.strptime(start_of_investment, '%Y-%m-%d %H:%M:%S') - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')   
test_end_time = start_of_investment.rsplit(" ")[0]

def call_portfolios(trading_days, start_time, end_time, test_start_time = "", test_end_time = "", add_index=False):
    
    total_portfolio = []
    portfolio_weights = []
    portfolio_invests = []
    performances = []
    
    # Getting the S&P500 (benchmark)
    sp500 = pdr.DataReader('^GSPC', 'yahoo', start_time, end_time)['Close']
    sp500 = sp500.rename('SP500')
    sp500 = sp500.to_frame()
    
    for i in range(0, len(stock_list.columns)): 
    #for i in range(0, 1):
        
        stock = []
        stock = stock_list.iloc[:,i].tolist() ### !!! Important: change the number to get the portfolio of interest (first one is 50% percentile, etc.)
        stock = [x for x in stock if str(x) != 'nan']
        
        portfolio_name = stock_list.columns[i]
        
        # Getting stock data (maybe re-do to for loop, if there be problems with memory)
        temp = pdr.DataReader(stock, 'yahoo', start_time, end_time)['Close']
        data = sp500.join(temp)
        del temp
        
        # Main dataset with all tickers and without S&P
        stocks = data.drop('SP500', 1)
        
        # Drop stocks where are less than 50% of data points available, if applicable
        if filter_recent_stocks[i]:
            stocks = stocks.loc[:, (stocks.count() >= stocks.count().max()/2)]
        
        risk_free_rate = 0.0085 # !!! Risk-free rate, 10Y US treasury bond, could be adjusted
        weight_bounds = weight_bounds_tuple[i]  # taken from the tuple each iteration, defined at the beginning
        
        # !!! Different approaches could be taken from here
        mu = mean_historical_return(stocks) # Getting returns
        S = CovarianceShrinkage(stocks).ledoit_wolf() # Getting cov matrix
        
        current_weights = [0] * len(stocks.columns)
        
        # Main function to find optimal portfolio, determining optimal weights
        ef = EfficientFrontier(mu, S, weight_bounds=weight_bounds)
        ef.add_objective(objective_functions.transaction_cost, w_prev=current_weights, k=0.005)
        ef.add_objective(objective_functions.L2_reg, gamma=gamma) 
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate) # using max sharpe optimization
        cleaned_weights = ef.clean_weights() # weights with pretty formatting
        print(cleaned_weights)
        
        # Printing info on returns, variance & sharpe
        temp_tuple = ef.portfolio_performance(verbose=True)
        
        temp_dict = {}
        temp_dict['Portfolio'] = portfolio_name
        temp_dict['Return'] = "{:.4f}".format(temp_tuple[0])
        temp_dict['Risk'] = "{:.4f}".format(temp_tuple[1])
        temp_dict['Sharpe'] = "{:.4f}".format(temp_tuple[2])
        performances.append(temp_dict)
        
        # Putting weights into pandas df
        max_sharpe_allocation = pd.DataFrame.from_dict(cleaned_weights, orient='index')
        max_sharpe_allocation.columns =['allocation_weight']    
        
        ### This function would change the weights to a number of shares based on the last price in the observable interval
        latest_prices = get_latest_prices(stocks)
        if add_index == False:
            da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=total_portfolio_value)    
            if discrete_algo_lp[i] == True:
                allocation, leftover = da.lp_portfolio()
            else: allocation, leftover = da.greedy_portfolio()
            
            print(allocation)
            print("Money left: " + str(leftover))
            print(da._allocation_rmse_error())
            
            # Adding discrete allocation to portfolio dataframe
            allocation = pd.DataFrame.from_dict(allocation, orient='index')
            allocation.columns =['allocation_discrete']   
            max_sharpe_allocation = max_sharpe_allocation.join(allocation)
                
            
        # Add some plots
        plot_covariance(S)
        plot_weights(weights)
        
        
        start_of_investment = str(latest_prices.name)
        if add_index == True:
            if np.any(start_of_investment in trading_days.values) ==  True:
                start_of_investment = trading_days[trading_days.index[trading_days == start_of_investment].tolist()[0] + 1]
            
            ### Function to crete a portfolio and test it on the new data
            portfolio, data_new = load_data(max_sharpe_allocation, test_start_time, test_end_time)
            tmp = create_index(test_start_time, test_end_time, start_of_investment, portfolio_name, portfolio, data_new)
            
            # Add all results to list
            total_portfolio.append(tmp[0])
            portfolio_weights.append(tmp[1])
            
            with open(p+'/portfolios/performance_index.txt', 'w') as outFile:
                for d in performances:
                    line =  str(i) + ": " + " ".join([str(key)+' : '+str(value) for key,value in d.items()]) + '\n'
                    outFile.write(line)
            
            
        else:
            if np.any(start_of_investment in trading_days.values) ==  False:
                start_of_investment = trading_days[trading_days.index[trading_days == start_of_investment].tolist()[0] + 1]
        
            portfolio, data_new = load_data(max_sharpe_allocation, test_end_time, test_end_time)
            tmp2 = create_portfolio(start_of_investment, portfolio_name, portfolio, data_new)
            
            # Add all results to list
            portfolio_invests.append(tmp2)
            
            with open(p+'/portfolios/performance_investment.txt', 'w') as outFile:
                for d in performances:
                    line =  str(i) + ": " + " ".join([str(key)+' : '+str(value) for key,value in d.items()]) + '\n'
                    outFile.write(line)
    
        
    return total_portfolio, portfolio_weights, portfolio_invests 


# Call for creating index with backtest
ttl_portfolio, weights_portf, _ = call_portfolios(trading_days, start_time, end_time, test_start_time, test_end_time, add_index=True)

# Call for creating portfolio up to latest date for investment
_, _, allocated_investment = call_portfolios(trading_days, start_time, test_end_time, test_end_time, test_end_time, add_index=False)


# Get column identificator of each portfolio
cols = list(stock_list.columns)

d = {}
d['S&P500'] = ttl_portfolio[0].iloc[:,1]
for i in range(0, len(ttl_portfolio)):
    d[cols[i]] = ttl_portfolio[i].iloc[:,0]

df = pd.DataFrame.from_dict(d,orient='columns')

df.to_excel(p + '/portfolios/resulting_portfolios.xlsx')