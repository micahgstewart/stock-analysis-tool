from dash import html, dcc
from dash.dependencies import Input, Output, State
from app.utils.stock_data import get_stock_data

# Define the layout
layout = html.Div([
    html.H1("Stock Analysis Tool", className="header-title"),
    
    html.Div([
        html.Label("Enter Stock Ticker:"),
        dcc.Input(
            id='ticker-input',
            type='text',
            value='AAPL',
            placeholder='Enter stock ticker...'
        ),
        html.Button('Submit', id='submit-button', n_clicks=0)
    ], className="input-container"),
    
    html.Div([
        dcc.Graph(id='stock-price-graph'),
        dcc.Graph(id='volume-graph')
    ], className="graphs-container"),
    
    dcc.Loading(
        id="loading",
        type="default",
        children=html.Div(id="loading-output")
    )
])

def init_callbacks(app):
    @app.callback(
        [
            Output('stock-price-graph', 'figure'),
            Output('volume-graph', 'figure'),
            Output('loading-output', 'children')
        ],
        [
            Input('submit-button', 'n_clicks')
        ],
        [
            State('ticker-input', 'value')
        ]
    )
    def update_graphs(n_clicks, ticker):
        return get_stock_data(ticker) 