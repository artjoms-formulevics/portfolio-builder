#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 12:13:52 2020

@author: afo
"""

import pandas as pd
import plotly.express as px
import os
from os.path import abspath
from inspect import getsourcefile

def data_loader():

    p = abspath(getsourcefile(lambda:0))
    p = p.rsplit('/', 1)[0]
    os.chdir(p)
    print('Working Directory is: %s' % os.getcwd())
    
    pd.options.display.float_format = '${:.2f}'.format
    
    # Get intial data (from files)
    df = pd.read_csv(p + '/portfoliotheory/results_2015-2019/portfolio_ticker_25.csv')
    portfolio = pd.read_csv(p+'/portfoliotheory/results_2015-2019/portfolio_weights_ticker_25.csv', index_col=0).iloc[:,0:5]
    all_portfolios = pd.read_excel(p+'/portfoliotheory/results_2015-2019/resulting_portfolios.xlsx')
    
    df = df.rename(columns={'total':'portfolio_25'})  # !!! naming
    df = df.sort_values(by=['Date'], ascending=False)
    
    # Store graphs to be plotted
    fig = px.line(df, x="Date", y=["portfolio_25", "SP500"], title='Our portfolio')  # !!! naming
    fig2 = px.line(all_portfolios, x="Date", y=all_portfolios.columns, title='All portfolios')

    return df, portfolio, all_portfolios, fig, fig2
