#!/usr/bin/env python3
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import os
from os.path import abspath
from inspect import getsourcefile
from dash_table.Format import Format, Group, Scheme
from dash.dependencies import Input, Output

# custom import
from data_loading import data_loader

p = abspath(getsourcefile(lambda:0))
p = p.rsplit('/', 1)[0]
os.chdir(p)
print('Working Directory is: %s' % os.getcwd())

pd.options.display.float_format = '${:.2f}'.format

# Get intial data (from files)
df, portfolio, all_portfolios, fig, fig2 = data_loader()

# Start server
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    # All elements from the top of the page
    html.Div([
        html.Div([
            html.H1(children='Portfolio Performance vs S&P500'),
            html.Div(children='''
                        Some sample text.
                        '''),
            dcc.Graph(id='g1', figure=fig),
            dcc.Interval(
            id='interval-component1',
            interval=1*86400000, # in milliseconds (1 day)
            n_intervals=0
        )
        ], className="six columns"),

        html.Div([
            html.H1(children='All Portfolios'),
            html.Div(children='''
                    Some sample text.
                        '''),
            dcc.Graph(id='g2', figure=fig2),
            dcc.Interval(
            id='interval-component2',
            interval=1*87000000, # in milliseconds (1 day + 10 min)
            n_intervals=0
        )
        ], className="six columns"),
    ], className="row"),
               
           # New Div for all elements in the new 'row' of the page
    html.Div([
        html.Div([
            html.H1(children='Detailed Prices'),
            html.Div(children='''
                Some sample .
                '''),
            dash_table.DataTable(
                id='table1',
                columns=[{"name": i, "id": i, "type": 'numeric', 'format': Format(
                scheme=Scheme.fixed, 
                precision=2,
                group=Group.yes,
                groups=3,
                group_delimiter=',',
                decimal_delimiter='.')} for i in df.columns],
                data=df.to_dict('records'),
                page_size=25,
                                style_table={
                    'overflowY': 'scroll'
                            }
                ), 
                dcc.Interval(
                id='interval-component3',
                interval=1*87000000, # in milliseconds
                n_intervals=0
        )                   
         ], className="six columns"),
 
    html.Div([
            html.H1(children='Portfolio Info'),
            html.Div(children='''
                Some sample .
                '''),
            dash_table.DataTable(
                id='table2',
                columns=[{"name": i, "id": i, "type": 'numeric', 'format': Format(
                scheme=Scheme.fixed, 
                precision=3,
                group=Group.yes,
                groups=3,
                group_delimiter=',',
                decimal_delimiter='.')} for i in portfolio.columns],
                data=portfolio.to_dict('records'),
                page_size=30,
                style_table={
                    'overflowY': 'scroll'
                            }
                ),                    
         ], className="six columns"),
                     
                     ], className="row"),
])
                     
@app.callback(Output('g1', 'figure'),
              Input('interval-component1', 'n_intervals'))
def update_graph_1(n):
    
    #update_prices()
    
    _, _, _, fig, _ = data_loader()
    
    return fig

@app.callback(Output('g2', 'figure'),
              Input('interval-component2', 'n_intervals'))
def update_graph_2(n):
    
    #update_prices()
    
    _, _, _, _, fig2 = data_loader()

    return fig2

@app.callback(Output('table1', 'data'),
              Input('interval-component3', 'n_intervals'))
def update_table_1(n):
    
    df, _, _, _, _ = data_loader()

    return df.to_dict('records')

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)  # port=8050 & host=127.0.0.1 for Mac // 80 & 0.0.0.0 for AWS
    
    
    
    
    
    