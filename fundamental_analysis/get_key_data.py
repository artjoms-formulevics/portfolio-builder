#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 14:43:48 2020

@author: afo
"""
import pandas as pd
import os
from os import listdir
from os.path import abspath, isfile, join
from inspect import getsourcefile
import operator
from math import nan
import numpy as np

# custom function
from get_averages import get_means

p = abspath(getsourcefile(lambda:0))
p = p.rsplit('/', 1)[0]
os.chdir(p)
print('Working Directory is: %s' % os.getcwd())


# Get list of files with data
files = [f for f in listdir(p + '/annual_financials_tech') if isfile(join(p + '/annual_financials_tech', f))]
try :
    files.remove('.DS_Store')
except ValueError:
    print()

# Get means for each indicator from custom function
means = get_means()

lst_hard = []
lst_soft = []
tickers = []

# List of ticker names
tickers = [t.split('.', 1)[0] for t in files]


"""
# Function is evaluating each ratio based on the benchmark value and outputs results
inputs:
    ratio = list of values of ratio
    ratio name = full name
    ratio_short_name = name to be compared with averages & used for outputs
    fail_sign = operator to determine failure of the indicator, if > that means indicator if failing when it is higher than a benchmark
    benchmark_value = an arbitrary value (e.g. 1) that determines a min/max good value of an indicator
    e.g. if fail_sign = '>' & benchmark_value = 5.0 for a D/E ratio, then must be lower than 5 in order not to fail
    last_year = the most recent data value in a dataset (year)
    fmt = the format to be used for the output, usually 3 decimals or %
    growth = to indicate, if the ratio given is a growth ratio in % or flat values
    growth_benchmark = minimum growth rate to not get a fail on the growth rate (e.g. if = 0, than any positive growth would result in success)
    not_zero = special fail operator, if true uses omparison of the ratio to zero (ignoring previous fail_sign)
    
Function returns two dicts that contain all the values, where this company failed at + years when these fails occured 
If the function fails to the arbitrary benchmark, that counted as hard failure, and if it is worse than mean of all companies - soft failure
Currently the number of years failed at does not matter, as it still counted as 1 fail, but that could be improved in future
"""
def evaluate_ratio(ratio, ratio_name, ratio_short_name, fail_sign, benchmark_value=nan, last_year='2020', fmt="{:.3f}", growth=False, growth_benchmark=0, not_zero=False):
    
    
    r = ratio[0:2] ### !!! Get only first 2 years for the hard failure check, can be adjusted for more or less (from 1 to 5)
    
    # Assign the right evaluation operator
    if fail_sign == '>':
        comp = operator.gt
        bmark = "The lower, the better:"
    else:
        comp = operator.lt
        bmark = "The higher, the better:"
    
    # Get global mean for the ratio
    mean_ratio = float(means.at[ratio_short_name, last_year])
    
    # Print ratio values
    print("\n============================================")
    print("\n" + ratio_name + '(s):')
    print(ratio.astype(float).map(fmt.format).to_string())
    
    # Print benchmarking method
    print("\n"+bmark)
    
    # Print arbitrary benchmark
    print("\nBenchmark value for " + ratio_name + ":")
    if benchmark_value != nan:
        print(str(fmt.format(benchmark_value) + " " + fail_sign))
    else: 
        print('No hard benchmark for this indicator.')
    
    # Print benchmark mean
    print("\nMean " + last_year + " " + ratio_name + " for all peers:")
    print(fmt.format(mean_ratio))

    # Compare ratios to global mean
    temp = ratio.to_frame()
    temp['fail'] = comp(temp.iloc[:,0], mean_ratio)
    temp2 = temp.iloc[:,0].loc[temp['fail'] == True]
    if len(temp2) > 0:
        fails_soft[ratio_short_name+'_worse_avg'] = temp2.to_dict()
    
    # Compare to arbitrary benchmark
    if not_zero == True:
        comp = operator.ne
        
    if benchmark_value != nan:
        temp = r[comp(r, benchmark_value)]
        if len(temp)>0:
            fails_hard[ratio_short_name+'_worse_benchmark'] = temp.to_dict()
            
    if growth == True:
        # Calculate mean growth rate
        temp = ratio.mean()
        print("\nMean " + ratio_name + " Growth Rate:")
        print(fmt.format(temp))
        if temp < growth_benchmark:
            fails_hard[ratio_short_name+'_mean_growth'] = temp
    
    return fails_hard, fails_soft

"""
# Similar function that calculates CAGR rate for ratios that matter - currently only for EPS 
inputs:
    ratio = list of values of ratio
    ratio name = full name
    ratio_short_name = name to be compared with averages & used for outputs
    fail_sign = operator to determine failure of the indicator, if > that means indicator if failing when it is higher than a benchmark
    benchmark_value = an arbitrary value (e.g. 1) that determines a min/max good value of an indicator
    e.g. if fail_sign = '>' & benchmark_value = 5.0 for a D/E ratio, then must be lower than 5 in order not to fail
    last_year = the most recent data value in a dataset (year)
    fmt = the format to be used for the output, usually 3 decimals or %
    cagr_benchmark = minimum cagr rate to not get a fail on the growth rate (e.g. if = 0, than any positive cagr would result in success)

Function returns two dicts that contain all the values, where this company failed at + years when these fails occured 
Currently the number of years failed at does not matter, as it still counted as 1 fail, but that could be improved in future
"""
def evaluate_cagr(ratio, ratio_name, ratio_short_name, last_year='2020', fmt="{:.3%}", cagr_benchmark=0):
        
     # Calculate CAGR
    if ratio[l-1] != 0:
        if len(ratio) != 1:
            temp = (ratio[0]/ratio[l-1])**(1/(l-1))-1
        else:
            temp = 0
    else:
        temp = 0
    print("\nCAGR " + ratio_name + " Growth Rate:")
    if type(temp) ==  complex:
        print("Result is a complex number")
        fails_hard[ratio_short_name+'_cagr_growth'] = temp
    else:
        print(fmt.format(temp))
        if temp < cagr_benchmark:
            fails_hard[ratio_short_name+'_cagr_growth'] = temp

    return fails_hard, fails_soft


## Function to write back data to excels and add fails tabs
def write_excel(fails_hard, fails_soft, ticker):
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter( p + '/annual_financials_tech/' + ticker + '.xlsx', engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    balance_sheet.to_excel(writer, sheet_name='BS')
    income_statement.to_excel(writer, sheet_name='IS')
    cash_flow.to_excel(writer, sheet_name='CF')
    key_metrics.to_excel(writer, sheet_name='Key Metrics')
    financial_ratios.to_excel(writer, sheet_name='Ratios')
    growth_ratios.to_excel(writer, sheet_name='Growth')
    dcf.to_excel(writer, sheet_name='DCF')
    
    d1 = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in fails_hard.items() ]))
    d1 = d1.transpose()
    d1 = d1.rename(columns={ d1.columns[0]: "general" })
    d1.to_excel(writer, sheet_name='fails_hard')
    
    d2 = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in fails_soft.items() ]))
    d2 = d2.transpose()
    d2 = d2.rename(columns={ d1.columns[0]: "general" })
    d2.to_excel(writer, sheet_name='fails_soft')
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    


# Main Loop through each ticker (file)
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
    
    # Get the number of columns (years), needed for CAGR, to find out, how many years are in the calculation
    l = len(balance_sheet.columns)
    
    # Dicts to store the results for each company
    fails_hard = {}
    fails_soft = {}
    
    ### For each indicator, calling an evaluate_ratio function with set parameters.
    ### for EPS also CAGR function
    ### Results are stored into dicts
    
    # Eps growth should be non-negative each year, non-negative on average and non negative CAGR
    fails_hard, fails_soft = evaluate_ratio(growth_ratios.loc['epsgrowth'], 'EPS Growth', 'epsGr', fail_sign='<', benchmark_value=0.0, fmt="{:.3%}", growth=True, growth_benchmark = 0.0)
    fails_hard, fails_soft = evaluate_cagr(income_statement.loc['eps'], 'EPS', 'eps', cagr_benchmark=0.0)
    
    # P/E ratio should be less than 15 (a long-term S&P 500 average)
    fails_hard, fails_soft = evaluate_ratio(key_metrics.loc['peRatio'], 'P/E Ratio', 'pe', fail_sign='>', benchmark_value=15.0, fmt="{:.3f}")
    # PEG should be less than 1 (arbitrary value)
    fails_hard, fails_soft = evaluate_ratio((key_metrics.loc['peRatio'] / (growth_ratios.loc['epsgrowth']*100)), 'PEG', 'peg', fail_sign='>', benchmark_value=1.0, fmt="{:.3f}")
    # P/B ratios hould be less than 3 (arbitrary value)
    fails_hard, fails_soft = evaluate_ratio(key_metrics.loc['pbRatio'], 'P/B Ratio', 'pb', fail_sign='>', benchmark_value=3.0, fmt="{:.3f}")
    # P/S ratio, no hard benchmark
    fails_hard, fails_soft = evaluate_ratio(key_metrics.loc['priceToSalesRatio'], 'P/S Ratio', 'ps', fail_sign='>', benchmark_value=nan, fmt="{:.3f}")
    # Dividend payout ratio should be not 0 (at least something was paid in dividends)
    fails_hard, fails_soft = evaluate_ratio(financial_ratios.loc['dividendPayoutRatio'], 'Dividend Payout Ratio', 'divPyr', fail_sign='<', benchmark_value=0.0, fmt="{:.3%}", not_zero=True)
    # Dividend payout ratio should more than 0 (at least some dividends are paid)
    fails_hard, fails_soft = evaluate_ratio(key_metrics.loc['dividendYield'], 'Dividend Yield', 'divYield', fail_sign='<', benchmark_value=0.0, fmt="{:.3%}")
    
    # ROE  should be at least 10% (long-term S&P average is 14%)
    fails_hard, fails_soft = evaluate_ratio(key_metrics.loc['roe'], 'ROE', 'roe', fail_sign='<', benchmark_value=0.10, fmt="{:.3%}")
    # ROA  should be at least 5% (own arbitrary value)
    fails_hard, fails_soft = evaluate_ratio(financial_ratios.loc['returnOnAssets'], 'ROA', 'roa', fail_sign='<', benchmark_value=0.05, fmt="{:.3%}")
    # Operating income margin should be more than 13% (S&P 500 average in 2019-2020)
    fails_hard, fails_soft = evaluate_ratio(income_statement.loc['operatingIncomeRatio'], 'Operating Income Ratio', 'opIncR', fail_sign='<', benchmark_value=0.13, fmt="{:.3%}")
    # Growth in operating income margin should be more than 0%, i.e. at least some growth (own arbitrary value)
    fails_hard, fails_soft = evaluate_ratio(growth_ratios.loc['operatingIncomeGrowth'], 'Operating Income Growth', 'opIncGr', fail_sign='<', benchmark_value=0.0, fmt="{:.3%}", growth=True, growth_benchmark=0.0)
    # Net income margin should be more than 9% (S&P 500 average in 2019-2020)
    fails_hard, fails_soft = evaluate_ratio(financial_ratios.loc['netProfitMargin'], 'Net Profit Margin', 'netPrMar', fail_sign='<', benchmark_value=0.09, fmt="{:.3%}")
    
    # Cash ratio should be more than 0.12, as indicator of stability (average for S&P companies in 2019)
    fails_hard, fails_soft = evaluate_ratio(financial_ratios.loc['cashRatio'], 'Cash Ratio', 'cashR', fail_sign='<', benchmark_value=0.12, fmt="{:.3f}")
    # Current ratio should be more than 1, as indicator of stability (arbitrary value)
    fails_hard, fails_soft = evaluate_ratio(financial_ratios.loc['currentRatio'], 'Current Ratio', 'currentR', fail_sign='<', benchmark_value=1, fmt="{:.3f}")
    
    # Current ratio should be less than 5, as indicator of stability (average for S&P companies in 2019-2020)
    fails_hard, fails_soft = evaluate_ratio(key_metrics.loc['debtToEquity'], 'D/E Ratio', 'de', fail_sign='>', benchmark_value=5.0, fmt="{:.3f}")
    
    # Interest Coverage ratio should be more than 5, as indicator of stability (average for S&P companies in 2019-2020)
    fails_hard, fails_soft = evaluate_ratio(key_metrics.loc['interestCoverage'], 'Interest Coverage Ratio', 'intCov', fail_sign='<', benchmark_value=5.0, fmt="{:.3f}")
    
    # Assetturnover ratio should be more than 0.3, as indicator of stability (average for S&P companies in 2019-2020)
    fails_hard, fails_soft = evaluate_ratio(financial_ratios.loc['assetTurnover'], 'Asset Turnover Ratio', 'asTurn', fail_sign='<', benchmark_value=0.3, fmt="{:.3f}")

    # Asset growth should be more than 0%, i.e. at least some growth (own arbitrary value)
    fails_hard, fails_soft = evaluate_ratio(growth_ratios.loc['assetGrowth'], 'Asset Growth', 'asGr', fail_sign='<', benchmark_value=0.0, fmt="{:.3%}", growth=True, growth_benchmark = 0.0)
    # FCF growth should be more than 0%, i.e. at least some growth (own arbitrary value)
    fails_hard, fails_soft = evaluate_ratio(growth_ratios.loc['freeCashFlowGrowth'], 'FCF Growth', 'fcfGr', fail_sign='<', benchmark_value=0.0, fmt="{:.3%}", growth=True, growth_benchmark = 0.0)

    # D/A ratio removed
    #fails_hard, fails_soft = evaluate_ratio(key_metrics.loc['debtToAssets'], 'D/A Ratio', 'da', fail_sign='>', benchmark_value=1, fmt="{:.3f}")
    # Payables turnover removed
    #fails_hard, fails_soft = evaluate_ratio(financial_ratios.loc['payablesTurnover'], 'Payables Turnover Ratio', 'payTurn', fail_sign='<', benchmark_value=0, fmt="{:.3f}")

    # Dicts are appended to lists to preserve order
    lst_hard.append(fails_hard)
    lst_soft.append(fails_soft)
    
    # Write back to files, adding fails tabs
    write_excel(fails_hard, fails_soft, tickers[i])

# All the information is getting wrapped to a pandas df - one for hard, second for soft fails
results_hard = dict(zip(tickers, lst_hard))
results_soft = dict(zip(tickers, lst_soft))

temp = pd.DataFrame.from_dict(results_hard,orient='index')
temp2 = pd.DataFrame.from_dict(results_soft,orient='index')

# Counting how many fails for each ticker occured - softs and hards (fails at multiple years in 1 indicator are counted as a single fail)
temp['count_hard'] = temp.count(axis=1)
temp2['count_soft'] = temp2.count(axis=1)
temp = temp.join(temp2, how='outer')
temp['count_total'] = temp['count_hard'] + (temp['count_soft'] / 2)  # weighted count, where soft fails are twice less of importnace than hard

"""
# Creating list of companies to be selected based on results

Basic logic:
    several lists are created, selecting companies with the least fails
    
    1. companies that have less fails than median
    2. less fails than 75%
    3. less than 90%
    4. less than 95%

As a result, a list with ticker names is returned
"""
end_results = {}
extended_results = {}
percentiles = [50, 25, 10, 5]
for i in percentiles:
    
    selected = temp[temp['count_total']<=np.percentile(temp['count_total'], i)]
    
    selected = selected.sort_index()
   # l = selected.index
    end_results['ticker_'+str(i)] = selected.index
    extended_results['ticker_'+str(i)] = selected
    #selected.to_csv('eligible_companies.csv')
    
# Results are merged into a single dataframe
end_results = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in end_results.items() ]))

# Custom tickers from the file are added - a portfolio without regards to stability, based on pure intuition/non quantifiable research
custom_tickers = pd.read_csv('custom_tickers.csv')

# All tickers from the file are added - a portfolio without regards to stability, based on search within all tickers
all_tickers = pd.DataFrame(tickers, columns = ['ticker_all'])

# Everyting is merged together and getting written to csv - containing several lists of tickers
# Later this file would become a source for Portfolio Theory models
end_results = pd.concat([end_results, custom_tickers], axis=1)
end_results = pd.concat([end_results, all_tickers], axis=1)
end_results.to_csv('stocks.csv', index=False)



