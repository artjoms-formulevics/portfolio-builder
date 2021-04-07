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

# Function gathers latest ticker data for selected portfolios
def update_prices():
    
    p = abspath(getsourcefile(lambda:0))
    p = p.rsplit('/', 1)[0]
    os.chdir(p)
    print('Working Directory is: %s' % os.getcwd())
    
    
    file_path = p+ '/results_2015-2019/'  # !!! Editable Folder with files with weights
    start_time = '2020-01-01'  # !!! start date, editable
    end_time = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')  # last day = day before today
    
    # Lists of files with portfolio weights
    files = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    files = [f for f in files if f.startswith('portfolio_weights')]
    files = [file_path+f for f in files]
    
    totals = []
    
    # Main loop updates each file
    for i in range(0, len(files)):
        
        portfolio = pd.read_csv(files[i], index_col=0).iloc[:,0:5]
        
        tickers = portfolio.iloc[:,1].tolist()  # tickers inside portfolio (they will be updated)
        
        # Getting stock data (maybe re-do to for loop, if there be problems with memory)
        temp = pdr.DataReader(tickers, 'yahoo', start_time, end_time)['Close']
        
        weights = portfolio['shares_bought'].to_frame().T
        weights.columns = tickers
        
        temp = temp.mul(weights.values)  # recalculate each ticker according to weight in portfolio
        temp['total'] = temp.sum(axis=1)
        
        
        # Getting the S&P500 (benchmark)
        data = pdr.DataReader('^GSPC', 'yahoo', start_time, end_time)['Close']
        data = data.rename('SP500')
        data = data.to_frame()
    
        data = data.join(temp)
        del temp
        
        
        # Rearrange cols
        cols = data.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        data = data[cols]
        
        # Get paths & filenames for saving with replacing old csv files
        n = files[i].split('_')[-1]
        s = file_path + 'portfolio_ticker_' + n
        
        data.to_csv(s)
        
        # Create one total file with comparison of all of portfolios
        totals.append(data['total'].to_frame())
        totals[i] = totals[i].rename(columns={'total':'portfolio_'+n.split('.')[0]})
        
    
    total = pd.concat(totals, axis=1)
    
    total.to_excel(file_path+'resulting_portfolios.xlsx')
    
    print("All done!")
    
    
update_prices()
    
