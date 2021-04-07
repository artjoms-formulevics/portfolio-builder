#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 10:35:28 2020

@author: afo
"""

from os import listdir
from os.path import isfile, join, abspath
import os
from inspect import getsourcefile
import pandas as pd
from datetime import datetime, timedelta
import pandas_datareader as pdr
from pypfopt.efficient_frontier import EfficientFrontier, objective_functions
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

# Function rebalances selected portfolios

def rebalnce_portfolios():
    
    p = abspath(getsourcefile(lambda:0))
    p = p.rsplit('/', 1)[0]
    os.chdir(p)
    print('Working Directory is: %s' % os.getcwd())
    
    file_path = p+ '/results_2015-2019/'  # !!! Editable Folder with files with weights
    start_time = '2015-01-01'  # !!! start date, editable
    end_time = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')  # last day = day before today
    
    # Lists of files with portfolio weights
    files = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    files = [f for f in files if f.startswith('portfolio_investment')]
    files = [file_path+f for f in files]
    files = sorted(files)

    
    weight_bounds_tuple =((0.0, 0.1),(0.0, 0.1),(0.0, 0.15),(0.0, 0.05),(0.0, 0.05),(0.01, 0.1))  # !!! Weights to be adjusted for every iteration by arbitrary value
    gamma = 0.05
    
    total_portfolio_value = 20000
    
    for i in range(0, len(files)):
        
        portfolio = pd.read_csv(files[i], index_col=0).iloc[:,0:6]
        
        tickers = portfolio.iloc[:,2].tolist()  # tickers inside portfolio (they will be updated)
        
        # Getting stock data (maybe re-do to for loop, if there be problems with memory)
        temp = pdr.DataReader(tickers, 'yahoo', start_time, end_time)['Close']
        
        current_weights = portfolio['allocation_weight'].to_list()
        
        
        risk_free_rate = 0.0085 # !!! Risk-free rate, 10Y US treasury bond, could be adjusted
        weight_bounds = weight_bounds_tuple[i]  # taken from the tuple each iteration, defined at the beginning
            
        # !!! Different approaches could be taken from here
        mu = mean_historical_return(temp) # Getting returns
        S = CovarianceShrinkage(temp).ledoit_wolf() # Getting cov matrix
            
        # Main function to find optimal portfolio, determining optimal weights
        ef = EfficientFrontier(mu, S, weight_bounds=weight_bounds)
        ef.add_objective(objective_functions.transaction_cost, w_prev=current_weights, k=0.005)
        ef.add_objective(objective_functions.L2_reg, gamma=gamma) 
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate) # using max sharpe optimization
        cleaned_weights = ef.clean_weights() # weights with pretty formatting
        print(cleaned_weights)
        
        # Printing info on returns, variance & sharpe
        ef.portfolio_performance(verbose=True)
            
        ### This function would change the weights to a number of shares based on the last price in the observable interval
        latest_prices = get_latest_prices(temp)
        da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=total_portfolio_value)
        allocation, leftover = da.lp_portfolio()
        print(allocation)
        print("Money left: " + str(leftover))
        print(da._allocation_rmse_error())
        
        allocation = pd.DataFrame.from_dict(allocation, orient='index')
        allocation.columns = ['allocation_discrete'] 
    
        
        weights =  pd.DataFrame.from_dict(weights, orient='index')
        weights.columns =['allocation_weight'] 
        
        latest_prices =  pd.DataFrame(latest_prices)
        latest_prices.columns =['buy_price'] 
        
        tickers = pd.DataFrame(tickers)
        tickers.columns =['ticker'] 
        tickers.index = tickers['ticker'] 
        
        result = pd.concat([weights, allocation, tickers, latest_prices], axis=1)
        
        result['buy_investment'] = result['allocation_discrete'] * result['buy_price']
        result['actual_allocation'] = result['buy_investment'] / result['buy_investment'].sum()
     
        # Get paths & filenames for saving with replacing old csv files
        n = files[i].split('_')[-1]
        s = file_path + 'portfolio_ticker_' + n
        
        result.to_csv(s)
            
rebalnce_portfolios()