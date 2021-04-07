#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 13:38:12 2020

@author: afo
"""


import FundamentalAnalysis as fa
import pandas as pd
import os
from os.path import abspath
from inspect import getsourcefile

import config

# API calls limited to a 250 calls/day, so multiple Keys could be used
api_key = config.api_key


p = abspath(getsourcefile(lambda:0))
p = p.rsplit('/', 1)[0]
os.chdir(p)
print('Working Directory is: %s' % os.getcwd())

#ticker = ["RDS-A"]

# Function that reads txt file by row and appends tickers there to a list
def get_tickers():
    
    tickers = []
    f = open(p + "/stocks.txt", "r")
    for x in f:
        x=x.strip()
        if x.isalpha():
            tickers.append(x)
    return tickers

# Function that takes ticker name and api key to download with API several financials tables
def save_stock_data(ticker, api_key):

    #Obtain DCFs over time
    dcf_annually = fa.discounted_cash_flow(ticker, api_key, period="annual")
    
    #Collect the Balance Sheet statements
    balance_sheet_annually = fa.balance_sheet_statement(ticker, api_key, period="annual")
    
    #Collect the Income Statements
    income_statement_annually = fa.income_statement(ticker, api_key, period="annual")
    
    #Collect the Cash Flow Statements
    cash_flow_statement_annually = fa.cash_flow_statement(ticker, api_key, period="annual")
    
    #Show Key Metrics
    key_metrics_annually = fa.key_metrics(ticker, api_key, period="annual")
    
    #Show a large set of in-depth ratios
    financial_ratios_annually = fa.financial_ratios(ticker, api_key, period="annual")
    
    #Show the growth of the company
    growth_annually = fa.financial_statement_growth(ticker, api_key, period="annual")
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter( p + '/annual_financials_tech/' + ticker + '.xlsx', engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    balance_sheet_annually.to_excel(writer, sheet_name='BS')
    income_statement_annually.to_excel(writer, sheet_name='IS')
    cash_flow_statement_annually.to_excel(writer, sheet_name='CF')
    key_metrics_annually.to_excel(writer, sheet_name='Key Metrics')
    financial_ratios_annually.to_excel(writer, sheet_name='Ratios')
    growth_annually.to_excel(writer, sheet_name='Growth')
    dcf_annually.to_excel(writer, sheet_name='DCF')
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    
    return print(ticker + ' saved!')

# List of tickers to be collected    
stocks = get_tickers()

j = 0  # to keep track of api keys
n_calls = 250  # max number of calls per day with one API

# Main loop for stock data gathering
for i in range(0, len(stocks)):
    for attempt in range(10):
        print(stocks[i], "Gathering")
        try:
            if n_calls < 10:  # if less than 10 calls remain, pick next API key
                j = j + 1
                n_calls = 250
            
            save_stock_data(stocks[i], api_key[j])
            n_calls = n_calls - 7
        except Exception as e:
            print(stocks[i], e)
            j = j + 1
            n_calls = 250
        else:
            break
    else:
        print(stocks[i] + 'failed!')