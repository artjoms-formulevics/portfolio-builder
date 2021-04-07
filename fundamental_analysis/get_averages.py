#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 15:31:43 2020

@author: afo
"""

import pandas as pd
import os
from os import listdir
from os.path import abspath, isfile, join
from inspect import getsourcefile
import numpy as np

p = abspath(getsourcefile(lambda:0))
p = p.rsplit('/', 1)[0]
os.chdir(p)
print('Working Directory is: %s' % os.getcwd())

# Function calculates mean ratios accross all companies of interest. This to be used as a soft benchmark
def get_means():
    
    # list of each file with financials
    files = [f for f in listdir(p + '/annual_financials_tech') if isfile(join(p + '/annual_financials_tech', f))]
    try :
        files.remove('.DS_Store')
    except ValueError:
        print()
    
    # lists for each of the ratios
    eps = []
    epsGr = []
    pe = []
    pb = []
    ps = []
    divPyr = []
    divYield = []
    roe = []
    roa = []
    opIncR = []
    opIncGr = []
    netPrMar = []
    cashR = []
    currentR = []
    de = []
    da = []
    intCov = []
    asTurn = []
    payTurn = []
    asGr = []
    fcfGr = []
    peg = []
    
    i = 0
    
    # Main loop for going through each file and exctracting ratios
    for i in range(0, len(files)):
    
        xls = pd.ExcelFile( p + '/annual_financials_tech/' + files[i])
        #xls = pd.ExcelFile( p + '/annual_financials_tech/MSFT.xlsx')
        
        balance_sheet = pd.read_excel(xls, 'BS', index_col=0)
        income_statement = pd.read_excel(xls, 'IS', index_col=0)
        cash_flow = pd.read_excel(xls, 'CF', index_col=0)
        key_metrics = pd.read_excel(xls, 'Key Metrics', index_col=0)
        financial_ratios = pd.read_excel(xls, 'Ratios', index_col=0)
        growth_ratios = pd.read_excel(xls, 'Growth', index_col=0)
        dcf = pd.read_excel(xls, 'DCF', index_col=0)
        
        # If it is the very first file, than it creates the list, otherwise appends
        if i == 0:
            
            # Each part is wrapped in its own try/catch block based on the table, where this ratio is found
            # KeyError means there is no such element, then it just skipped
            try:
                eps = [income_statement.loc['eps'].to_list()]
                opIncR = [income_statement.loc['operatingIncomeRatio'].to_list()]
            except KeyError:
                continue
            
            try:
                epsGr = [growth_ratios.loc['epsgrowth'].to_list()]
                opIncGr = [growth_ratios.loc['operatingIncomeGrowth'].to_list()]
                asGr = [growth_ratios.loc['assetGrowth'].to_list()]
                fcfGr = [growth_ratios.loc['freeCashFlowGrowth'].to_list()]
            except KeyError:
                continue
            
            try:
                pe = [key_metrics.loc['peRatio'].to_list()]
                pb = [key_metrics.loc['pbRatio'].to_list()]
                ps = [key_metrics.loc['priceToSalesRatio'].to_list()]
                divYield = [key_metrics.loc['dividendYield'].to_list()]
                roe = [key_metrics.loc['roe'].to_list()]
                de = [key_metrics.loc['debtToEquity'].to_list()]
                da = [key_metrics.loc['debtToAssets'].to_list()]
                intCov = [key_metrics.loc['interestCoverage'].to_list()]
                
            except KeyError:
                continue
            
            try:
                divPyr = [financial_ratios.loc['dividendPayoutRatio'].to_list()]
                roa = [financial_ratios.loc['returnOnAssets'].to_list()]
                netPrMar = [financial_ratios.loc['netProfitMargin'].to_list()]
                cashR = [financial_ratios.loc['cashRatio'].to_list()]
                currentR = [financial_ratios.loc['currentRatio'].to_list()]
                asTurn = [financial_ratios.loc['assetTurnover'].to_list()]
                payTurn = [financial_ratios.loc['payablesTurnover'].to_list()]
            except KeyError:
                continue
            
        # Append to list, if it is not the first element
        else:
            
            try:
                eps.append(income_statement.loc['eps'].to_list())
                opIncR.append(income_statement.loc['operatingIncomeRatio'].to_list())
            except KeyError:
                continue
            
            try:
                epsGr.append(growth_ratios.loc['epsgrowth'].to_list())
                opIncGr.append(growth_ratios.loc['operatingIncomeGrowth'].to_list())
                asGr.append(growth_ratios.loc['assetGrowth'].to_list())
                fcfGr.append(growth_ratios.loc['freeCashFlowGrowth'].to_list())
            except KeyError:
                continue
            
            try:
                pe.append(key_metrics.loc['peRatio'].to_list())
                pb.append(key_metrics.loc['pbRatio'].to_list())
                ps.append(key_metrics.loc['priceToSalesRatio'].to_list())
                divYield.append(key_metrics.loc['dividendYield'].to_list())
                roe.append(key_metrics.loc['roe'].to_list())
                de.append(key_metrics.loc['debtToEquity'].to_list())
                da.append(key_metrics.loc['debtToAssets'].to_list())
                intCov.append(key_metrics.loc['interestCoverage'].to_list())
            except KeyError:
                continue
            
            try:
                divPyr.append(financial_ratios.loc['dividendPayoutRatio'].to_list())
                roa.append(financial_ratios.loc['returnOnAssets'].to_list())
                netPrMar.append(financial_ratios.loc['netProfitMargin'].to_list())
                cashR.append(financial_ratios.loc['cashRatio'].to_list())
                currentR.append(financial_ratios.loc['currentRatio'].to_list())
                asTurn.append(financial_ratios.loc['assetTurnover'].to_list())
                payTurn.append(financial_ratios.loc['payablesTurnover'].to_list())
            except KeyError:
                continue
            
        
    # Conver lists into the dataframes. years sometimes might be wrong (e.g. if some companies are not yet published their financials)
    # but that does not matter, as what matters is the last available value to be taken into the considerationg
    all_eps = pd.DataFrame(eps, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_epsGr =  pd.DataFrame(epsGr, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_pe = pd.DataFrame(pe, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_pb = pd.DataFrame(pb, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_ps = pd.DataFrame(ps, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_divPyr = pd.DataFrame(divPyr, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_divYield = pd.DataFrame(divYield, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_roe = pd.DataFrame(roe, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_roa = pd.DataFrame(roa, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_opIncR = pd.DataFrame(opIncR, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_opIncGr = pd.DataFrame(opIncGr, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_netPrMar = pd.DataFrame(netPrMar, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_cashR = pd.DataFrame(cashR, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_currentR = pd.DataFrame(currentR, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_de = pd.DataFrame(de, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_da = pd.DataFrame(da, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_intCov = pd.DataFrame(intCov, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_asTurn = pd.DataFrame(asTurn, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_payTurn = pd.DataFrame(payTurn, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_asGr = pd.DataFrame(asGr, columns = ['2020', '2019', '2018', '2017', '2016'])
    all_fcfGr = pd.DataFrame(fcfGr, columns = ['2020', '2019', '2018', '2017', '2016'])
    
    all_peg = all_pe.divide(all_epsGr.replace(np.inf, 0))
    
    # List of means for last available value
    l = [all_eps['2020'].mean(),
    all_epsGr['2020'].mean(),
    all_pe['2020'].mean(),
    all_pb['2020'].mean(),
    all_ps['2020'].mean(),
    all_divPyr['2020'].mean(),
    all_divYield['2020'].mean(),
    all_roe['2020'].mean(),
    all_roa['2020'].mean(),
    all_opIncR['2020'].mean(),
    all_opIncGr['2020'].mean(),
    all_netPrMar['2020'].mean(),
    all_cashR['2020'].mean(),
    all_currentR['2020'].mean(),
    all_de['2020'].mean(),
    all_da['2020'].mean(),
    all_intCov['2020'].mean(),
    all_asTurn['2020'].mean(),
    all_payTurn['2020'].mean(),
    all_asGr['2020'].mean(),
    all_fcfGr['2020'].mean(),
    all_peg['2020'].mean()]
    
    # List of ratio names
    ind = ['eps',
    'epsGr',
    'pe',
    'pb',
    'ps',
    'divPyr',
    'divYield',
    'roe',
    'roa',
    'opIncR',
    'opIncGr',
    'netPrMar',
    'cashR',
    'currentR',
    'de',
    'da',
    'intCov',
    'asTurn',
    'payTurn',
    'asGr',
    'fcfGr',
    'peg']
    
    # Combine values and names into df
    df = pd.DataFrame(l, columns=['2020'])
    df.index = ind

    return df