from dash import html, dcc, Input, Output, State
from dash.dependencies import Input, Output, State
from app.utils.stock_data import get_stock_data
import plotly.graph_objects as go
from app.utils.prediction import predict_stock_prices, create_prediction_figure

# Define the layout
layout = html.Div([
    # Header
    html.Header([
        html.H1("Stock Analysis Tool", className="header-title"),
    ], className="header"),
    
    # Main content
    html.Main([
        # Tabs
        dcc.Tabs([
            dcc.Tab(label='Fundamental Analysis', children=[
                # Input section
                html.Div([
                    html.Div([
                        html.Label("Enter Stock Ticker:", htmlFor="ticker-input"),
                    ], className="input-label-group"),
                    
                    dcc.Input(
                        id='ticker-input',
                        type='text',
                        value='AAPL',
                        placeholder='Enter stock ticker...',
                        className='ticker-input',
                        autoComplete='off'
                    ),
                    
                    html.Button([
                        html.I(className="fas fa-chart-line"),
                        "Analyze"
                    ], 
                    id='submit-button', 
                    n_clicks=0,
                    className='analyze-button')
                ], className="input-container"),
                
                # Quick Blurb
                html.Div([
                    html.Div(id='quick-blurb', className='blurb-box')
                ], className='blurb-container'),
                
                # Score and Graphs
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='score-visualization',
                            config={'displayModeBar': False}
                        )
                    ], className='score-card'),
                    
                    html.Div([
                        dcc.Graph(
                            id='stock-price-graph',
                            config={'displayModeBar': True, 'scrollZoom': True}
                        )
                    ], className='graph-card'),
                    
                    html.Div([
                        dcc.Graph(
                            id='volume-graph',
                            config={'displayModeBar': True, 'scrollZoom': True}
                        )
                    ], className='graph-card'),
                ], className='graphs-container'),
                
                # Metrics Boxes
                html.Div(id='metrics-container', className='metrics-container'),
            ], className='tab-content'),
            
            dcc.Tab(label='Predictive Analysis', children=[
                # Input section for prediction
                html.Div([
                    html.Div([
                        html.Label("Enter Stock Ticker:"),
                        dcc.Input(
                            id='predict-ticker-input',
                            type='text',
                            placeholder='Enter stock ticker (e.g., AAPL)',
                            className="input-field"
                        ),
                    ], className="input-group"),
                    
                    html.Div([
                        html.Label("Prediction Timeframe (days)"),
                        dcc.Input(
                            id='prediction-timeframe',
                            type='number',
                            value=30,
                            min=1,
                            max=365,
                            className="input-field"
                        ),
                    ], className="input-group"),
                    
                    html.Button(
                        'Predict', 
                        id='predict-button',
                        className="button"
                    ),
                ], className="controls-container"),
                
                # Results Section
                html.Div([
                    html.Div(id='prediction-summary'),
                    dcc.Graph(id='prediction-graph'),
                    html.Div(id='prediction-metrics', className="metrics-container")
                ], className="results-container"),
                
                # Loading spinner
                dcc.Loading(
                    id="loading-spinner",
                    type="default",
                    children=html.Div(id="loading-output-container")
                )
            ], className='tab-content')
        ], className='tabs-container')
    ])
])

def init_callbacks(app):
    @app.callback(
        [
            Output('stock-price-graph', 'figure'),
            Output('volume-graph', 'figure'),
            Output('score-visualization', 'figure'),
            Output('metrics-container', 'children'),
            Output('quick-blurb', 'children'),
        ],
        [Input('submit-button', 'n_clicks')],
        [State('ticker-input', 'value')]
    )
    def update_graphs(n_clicks, ticker):
        price_fig, volume_fig, score_fig, metrics, overall_score, error = get_stock_data(ticker)
        
        if error:
            return price_fig, volume_fig, {}, [], error
            
        metric_boxes = [
            create_metric_box(category, category_metrics)
            for category, category_metrics in metrics.items()
        ]
        
        blurb = generate_blurb(ticker, metrics, overall_score)
        
        return price_fig, volume_fig, score_fig, metric_boxes, blurb

    @app.callback(
        [Output('prediction-graph', 'figure'),
         Output('prediction-summary', 'children'),
         Output('prediction-metrics', 'children'),
         Output('loading-output-container', 'children')],
        Input('predict-button', 'n_clicks'),
        [State('predict-ticker-input', 'value'),
         State('prediction-timeframe', 'value')],
        prevent_initial_call=True
    )
    def update_prediction(n_clicks, ticker, days):
        if not ticker:
            return {}, html.P("Please enter a stock ticker"), "", ""
            
        if not days or days < 1:
            days = 30  # Default to 30 days
            
        print(f"Making prediction for {ticker} for {days} days")
        predictions, future_dates, historical_data = predict_stock_prices(ticker, days)
        
        if predictions is None or historical_data is None:
            return {}, html.P(f"Could not fetch data for {ticker}"), "", ""
            
        figure = create_prediction_figure(historical_data, predictions, future_dates, ticker)
        
        summary = html.H3(f"Prediction Results for {ticker}")
        
        metrics = html.Div([
            html.P(f"Last Close Price: ${historical_data['Close'].iloc[-1]:.2f}"),
            html.P(f"Predicted Price (in {days} days): ${predictions[-1][0]:.2f}"),
            html.P(f"Predicted Change: {((predictions[-1][0] / historical_data['Close'].iloc[-1]) - 1) * 100:.1f}%")
        ])
        
        return figure, summary, metrics, ""

def create_stock_price_figure(df, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price'))
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Price ($)',
        template='none',  # Remove template for cleaner look
        plot_bgcolor='white',  # White background for plot area
        paper_bgcolor='white',  # White background for figure
        font=dict(
            size=14,
            color='black'
        ),
        xaxis=dict(
            gridcolor='lightgrey',  # Light grid lines
            tickfont=dict(size=12, color='black'),
            title_font=dict(size=14, color='black'),
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='lightgrey',  # Light grid lines
            tickfont=dict(size=12, color='black'),
            title_font=dict(size=14, color='black'),
            showgrid=True
        )
    )
    
    return fig

def create_volume_figure(df, title):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'))
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Volume',
        template='none',  # Remove template for cleaner look
        plot_bgcolor='white',  # White background for plot area
        paper_bgcolor='white',  # White background for figure
        font=dict(
            size=14,
            color='black'
        ),
        xaxis=dict(
            gridcolor='lightgrey',  # Light grid lines
            tickfont=dict(size=12, color='black'),
            title_font=dict(size=14, color='black'),
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='lightgrey',  # Light grid lines
            tickfont=dict(size=12, color='black'),
            title_font=dict(size=14, color='black'),
            showgrid=True
        )
    )
    
    return fig

def get_color(value, thresholds, inverse=False):
    if inverse:
        if value <= thresholds['good']:
            return 'rgb(39, 174, 96)'  # green
        elif value <= thresholds['medium']:
            return 'rgb(241, 196, 15)'  # yellow
        else:
            return 'rgb(192, 57, 43)'  # red
    else:
        if value >= thresholds['good']:
            return 'rgb(39, 174, 96)'  # green
        elif value >= thresholds['medium']:
            return 'rgb(241, 196, 15)'  # yellow
        else:
            return 'rgb(192, 57, 43)'  # red

def create_metric_box(title, metrics):
    # Calculate box score
    total_score = 0
    max_score = len(metrics) * 2
    
    for metric_data in metrics.values():
        if metric_data['value'] >= metric_data['threshold']['good']:
            total_score += 2
        elif metric_data['value'] >= metric_data['threshold']['medium']:
            total_score += 1
            
    score_percentage = (total_score / max_score) * 100
    
    # Determine border color based on score
    if score_percentage >= 70:
        border_color = 'rgb(39, 174, 96)'  # Green
    elif score_percentage >= 50:
        border_color = 'rgb(241, 196, 15)'  # Yellow
    else:
        border_color = 'rgb(192, 57, 43)'  # Red
    
    return html.Div([
        html.H3(title, className='metric-box-title'),
        html.Div([
            html.Div([
                html.Span(metric_name, className='metric-name'),
                html.Span(
                    f"{metric_data['value']:.1f}{'%' if '%' in metric_name else ''}", 
                    style={'color': get_color(
                        metric_data['value'], 
                        metric_data['threshold'], 
                        metric_data.get('inverse', False)
                    )}
                )
            ], className='metric-row')
            for metric_name, metric_data in metrics.items()
        ], className='metric-content')
    ], className='metric-box', style={'borderTopColor': border_color})

def generate_blurb(ticker, metrics, overall_score):
    strength = "strong" if overall_score >= 70 else "moderate" if overall_score >= 50 else "weak"
    return html.Div([
        html.H3("Quick Analysis"),
        html.P([
            f"{ticker} shows {strength} fundamentals with an overall score of {overall_score:.1f}%. ",
            "Key strengths include: ",
            html.Span([
                metric_name for category, category_metrics in metrics.items()
                for metric_name, metric_data in category_metrics.items()
                if (not metric_data.get('inverse') and metric_data['value'] >= metric_data['threshold']['good'])
                or (metric_data.get('inverse') and metric_data['value'] <= metric_data['threshold']['good'])
            ][:3]),
            ". Areas for improvement: ",
            html.Span([
                metric_name for category, category_metrics in metrics.items()
                for metric_name, metric_data in category_metrics.items()
                if (not metric_data.get('inverse') and metric_data['value'] < metric_data['threshold']['medium'])
                or (metric_data.get('inverse') and metric_data['value'] > metric_data['threshold']['medium'])
            ][:3])
        ])
    ]) 