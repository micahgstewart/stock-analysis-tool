from dash import html, dcc, Input, Output, State
from dash.dependencies import Input, Output, State
from app.utils.stock_data import get_stock_data
import plotly.graph_objects as go
from app.utils.prediction import predict_stock_prices, create_prediction_figure
from plotly.subplots import make_subplots
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

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
        [Output('stock-price-graph', 'figure'),
         Output('volume-graph', 'figure'),
         Output('score-visualization', 'figure'),
         Output('metrics-container', 'children'),
         Output('quick-blurb', 'children')],
        [Input('ticker-input', 'value')]
    )
    def update_graphs(ticker):
        try:
            print(f"Fetching data for {ticker}...")
            
            if not ticker:  # Handle empty ticker
                raise ValueError("No ticker symbol provided")
            
            # Fetch stock data
            df = yf.download(
                ticker,
                start=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                end=datetime.now().strftime('%Y-%m-%d')
            )
            
            if df.empty:  # Handle empty dataframe
                raise ValueError(f"No data found for ticker {ticker}")
            
            print("Stock data fetched successfully")
            
            # Fetch financial data
            stock = yf.Ticker(ticker)
            financial_data = {
                'operating_margin': float(stock.info.get('operatingMargins', 0) or 0) * 100,
                'current_ratio': float(stock.info.get('currentRatio', 0) or 0),
                'quick_ratio': float(stock.info.get('quickRatio', 0) or 0),
                'debt_to_equity': float(stock.info.get('debtToEquity', 0) or 0),
                'return_on_equity': float(stock.info.get('returnOnEquity', 0) or 0) * 100,
                'return_on_assets': float(stock.info.get('returnOnAssets', 0) or 0) * 100,
                'asset_turnover': float(stock.info.get('assetTurnover', 0) or 0),
                'inventory_turnover': float(stock.info.get('inventoryTurnover', 0) or 0),
                'revenue_growth': float(stock.info.get('revenueGrowth', 0) or 0) * 100,
                'gross_margins': float(stock.info.get('grossMargins', 0) or 0) * 100,
                'profit_margins': float(stock.info.get('profitMargins', 0) or 0) * 100
            }
            
            print("Financial data fetched successfully")
            
            # Calculate metrics and scores
            metrics, overall_score = calculate_metrics(financial_data)
            print(f"Metrics calculated. Overall score: {overall_score}")
            
            # Create figures
            stock_fig = create_stock_figure(df)
            volume_fig = create_volume_figure(df)
            score_fig = create_score_visualization(overall_score)
            
            print("Figures created successfully")
            
            # Create metrics container
            metrics_container = create_metrics_dashboard(metrics, overall_score)
            
            # Create blurb
            quick_blurb = generate_blurb(ticker, metrics, overall_score)
            
            print("All components created successfully")
            
            # Return all components in the expected order
            return (
                stock_fig,      # stock-price-graph.figure
                volume_fig,     # volume-graph.figure
                score_fig,      # score-visualization.figure
                metrics_container,  # metrics-container.children
                quick_blurb     # quick-blurb.children
            )
            
        except Exception as e:
            print(f"Error in update_graphs: {str(e)}")
            # Return empty/error states for all outputs
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title='No Data Available',
                annotations=[{
                    'text': f"Error: {str(e)}",
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 14}
                }]
            )
            
            return (
                empty_fig,  # Empty stock figure
                empty_fig,  # Empty volume figure
                empty_fig,  # Empty score figure
                html.Div("Error loading metrics", style={'color': 'red'}),  # Error metrics container
                html.Div(f"Error processing data for {ticker}: {str(e)}", style={'color': 'red'})  # Error blurb
            )

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

def create_stock_figure(df):
    """Create stock price figure"""
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ))

    fig.update_layout(
        title='Stock Price',
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis=dict(
            title=dict(
                text='Price',
                font=dict(color='#1E88E5')
            ),
            gridcolor='lightgrey',
            zerolinecolor='lightgrey',
        ),
        xaxis_rangeslider_visible=False
    )

    return fig

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

def create_volume_figure(df):
    """Create volume figure"""
    fig = go.Figure()
    
    # Calculate colors for volume bars using numpy for vectorized comparison
    colors = np.where(df['Close'].values >= df['Open'].values, '#33FF33', '#FF3333')
    
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        marker_color=colors,
        opacity=0.7,
        name='Volume'
    ))
    
    fig.update_layout(
        title='Trading Volume',
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis=dict(
            title=dict(
                text='Volume',
                font=dict(color='#43A047')
            ),
            gridcolor='lightgrey',
            zerolinecolor='lightgrey',
        ),
        showlegend=False
    )
    
    return fig

def create_score_visualization(score):
    """Create score visualization figure"""
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Overall Score"},
        gauge={
            'axis': {'range': [1, 5]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [1, 2], 'color': "#FF0D0D"},
                {'range': [2, 3], 'color': "#FF4E11"},
                {'range': [3, 4], 'color': "#FAB733"},
                {'range': [4, 5], 'color': "#69B34C"}
            ],
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=30, b=30)
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
    max_score = len(metrics) * 5  # Now using 5 as max score per metric
    
    for metric_data in metrics.values():
        if isinstance(metric_data, dict) and 'score' in metric_data:
            total_score += metric_data['score']
            
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
                html.Div([
                    html.Span(
                        f"{metric_data['raw_value']:.1f}{'%' if '%' in metric_name else ''}", 
                        className='raw-value'
                    ),
                    html.Span(
                        f" (Score: {metric_data['score']}/5)", 
                        className='score-value',
                        style={'color': get_color(
                            metric_data['score'], 
                            {'good': 4, 'medium': 3}, 
                            False
                        )}
                    )
                ])
            ], className='metric-row')
            for metric_name, metric_data in metrics.items()
            if isinstance(metric_data, dict) and 'score' in metric_data
        ], className='metric-content')
    ], className='metric-box', style={'borderTopColor': border_color})

def score_metric(value, thresholds, inverse=False):
    """Score a metric from 1-5"""
    try:
        # Convert pandas Series or numpy values to float
        if hasattr(value, 'item'):
            value = value.item()
        elif hasattr(value, 'iloc'):
            value = value.iloc[0]
        
        # Handle NaN or None values
        if pd.isna(value) or value is None:
            return 1
            
        # Convert to float to ensure proper comparison
        value = float(value)
        
        if inverse:
            if value <= thresholds['very_good']: return 5
            if value <= thresholds['good']: return 4
            if value <= thresholds['medium']: return 3
            if value <= thresholds['bad']: return 2
            return 1
        else:
            if value >= thresholds['very_good']: return 5
            if value >= thresholds['good']: return 4
            if value >= thresholds['medium']: return 3
            if value >= thresholds['bad']: return 2
            return 1
            
    except Exception as e:
        print(f"Error in score_metric: {str(e)} for value {value}")
        return 1

def calculate_metrics(financial_data):
    # Define all metrics with their thresholds
    metrics = {
        'Profitability': {
            'Operating Margin': {
                'value': financial_data.get('operating_margin', 0),
                'threshold': {
                    'very_good': 25,
                    'good': 15,
                    'medium': 10,
                    'bad': 5
                }
            },
            'Profit Margin': {
                'value': financial_data.get('profit_margins', 0),
                'threshold': {
                    'very_good': 20,
                    'good': 15,
                    'medium': 10,
                    'bad': 5
                }
            },
            'ROE': {
                'value': financial_data.get('return_on_equity', 0),
                'threshold': {
                    'very_good': 20,
                    'good': 15,
                    'medium': 10,
                    'bad': 5
                }
            }
        },
        'Liquidity': {
            'Current Ratio': {
                'value': financial_data.get('current_ratio', 0),
                'threshold': {
                    'very_good': 3.0,
                    'good': 2.0,
                    'medium': 1.5,
                    'bad': 1.0
                }
            },
            'Quick Ratio': {
                'value': financial_data.get('quick_ratio', 0),
                'threshold': {
                    'very_good': 2.0,
                    'good': 1.5,
                    'medium': 1.0,
                    'bad': 0.5
                }
            },
            'Debt to Equity': {
                'value': financial_data.get('debt_to_equity', 0),
                'threshold': {
                    'very_good': 0.5,
                    'good': 1.0,
                    'medium': 1.5,
                    'bad': 2.0
                },
                'inverse': True
            }
        },
        'Efficiency': {
            'Asset Turnover': {
                'value': financial_data.get('asset_turnover', 0),
                'threshold': {
                    'very_good': 2.0,
                    'good': 1.5,
                    'medium': 1.0,
                    'bad': 0.5
                }
            },
            'Revenue Growth': {
                'value': financial_data.get('revenue_growth', 0),
                'threshold': {
                    'very_good': 20,
                    'good': 15,
                    'medium': 10,
                    'bad': 5
                }
            }
        }
    }

    # Calculate scores for each metric
    for category in metrics:
        category_score = 0
        valid_metrics = 0
        for metric_name, metric_data in metrics[category].items():
            if isinstance(metric_data, dict) and 'value' in metric_data:
                try:
                    score = score_metric(
                        metric_data['value'],
                        metric_data['threshold'],
                        metric_data.get('inverse', False)
                    )
                    metrics[category][metric_name]['score'] = score
                    category_score += score
                    valid_metrics += 1
                except Exception as e:
                    print(f"Error scoring {metric_name}: {str(e)}")
                    continue
        
        # Calculate average score for category (1-5 scale)
        if valid_metrics > 0:
            metrics[category]['category_score'] = category_score / valid_metrics
        else:
            metrics[category]['category_score'] = 1

    # Calculate overall score (1-5 scale)
    total_score = 0
    valid_categories = 0
    for category in metrics:
        if 'category_score' in metrics[category]:
            total_score += metrics[category]['category_score']
            valid_categories += 1
    
    overall_score = total_score / valid_categories if valid_categories > 0 else 1
    
    return metrics, overall_score

def generate_blurb(ticker, metrics, overall_score):
    # Convert score to descriptive text based on 1-5 scale
    def get_score_text(score):
        if score >= 4.5: return "very strong"
        if score >= 3.5: return "strong"
        if score >= 2.5: return "average"
        if score >= 1.5: return "weak"
        return "very weak"

    strength = get_score_text(overall_score)
    
    return html.Div([
        html.H3("Analysis Summary"),
        html.P([
            f"{ticker} shows {strength} fundamentals with an overall score of {overall_score:.1f}/5.0. ",
            get_company_summary(ticker),
        ], style={'color': 'black'}),
        
        # Category Scores
        html.Ul([
            html.Li([
                f"{category}: {metrics[category]['category_score']:.1f}/5.0"
            ], style={'color': 'black'})
            for category in metrics if 'category_score' in metrics[category]
        ], style={'color': 'black'}),
        
        # Key Metrics Bullet Points
        html.Ul([
            html.Li([
                f"Strong Metrics (4+ rating): ",
                ", ".join([
                    f"{metric_name} ({metric_data['score']}/5)" 
                    for category, category_metrics in metrics.items()
                    for metric_name, metric_data in category_metrics.items()
                    if isinstance(metric_data, dict) and 'score' in metric_data and metric_data['score'] >= 4
                ][:3])
            ], style={'color': 'black'}),
            
            html.Li([
                f"Weak Metrics (2 or below): ",
                ", ".join([
                    f"{metric_name} ({metric_data['score']}/5)"
                    for category, category_metrics in metrics.items()
                    for metric_name, metric_data in category_metrics.items()
                    if isinstance(metric_data, dict) and 'score' in metric_data and metric_data['score'] <= 2
                ][:3])
            ], style={'color': 'black'})
        ], style={'color': 'black'})
    ])

def get_company_summary(ticker):
    try:
        # You'll need to implement this function using your preferred financial data API
        # (e.g., yfinance, alpha_vantage, etc.) to fetch:
        # - Company description
        # - Recent news
        # - Product releases
        # - Important milestones
        # For now, returning a placeholder
        return "Company summary and recent news will appear here."
    except Exception as e:
        return "Company information unavailable."

def create_metric_indicator(value, thresholds, name, inverse=False):
    """Create a metric indicator with a 1-5 scale"""
    # Calculate score using the new threshold structure
    score = score_metric(value, thresholds, inverse)
    
    # Define color based on score
    colors = {
        1: "#FF0D0D",  # Very Bad - Red
        2: "#FF4E11",  # Bad - Orange-Red
        3: "#FAB733",  # Average - Yellow
        4: "#69B34C",  # Good - Light Green
        5: "#00B050"   # Very Good - Green
    }
    
    color = colors.get(score, "#FAB733")  # Default to yellow if score is invalid
    
    # Format the value based on if it's a percentage or ratio
    if isinstance(value, float) and abs(value) < 10:
        formatted_value = f"{value:.2f}"
    else:
        formatted_value = f"{value:.1f}%"
    
    return html.Div([
        html.P(name, className="metric-name"),
        html.Div([
            html.Div(className="metric-bar-container", children=[
                html.Div(className="metric-bar", style={
                    'width': f'{(score/5)*100}%',
                    'background-color': color,
                    'height': '20px',
                    'borderRadius': '10px'
                })
            ]),
            html.P(f"Score: {score}/5", className="metric-value"),
            html.P(f"Value: {formatted_value}", className="metric-actual-value")
        ])
    ], className="metric-container")

def create_metrics_section(metrics, section_name):
    """Create a section of metrics"""
    return html.Div([
        html.H3(section_name),
        html.Div([
            create_metric_indicator(
                metric_data['value'],
                metric_data['threshold'],
                metric_name,
                metric_data.get('inverse', False)
            )
            for metric_name, metric_data in metrics.items()
            if isinstance(metric_data, dict) and 'value' in metric_data
        ], className="metrics-grid")
    ], className="metrics-section")

def create_metrics_dashboard(metrics, overall_score):
    """Create the metrics dashboard with scores on 1-5 scale"""
    return html.Div([
        html.Div([
            html.H2("Overall Score", className="overall-score-title"),
            html.Div(f"{overall_score:.1f}/5.0", className="overall-score-value"),
            html.Div([
                create_metrics_section(metrics.get('Profitability', {}), "Profitability"),
                create_metrics_section(metrics.get('Management', {}), "Management"),
                create_metrics_section(metrics.get('Growth', {}), "Growth"),
                create_metrics_section(metrics.get('Financial Health', {}), "Financial Health"),
                create_metrics_section(metrics.get('Valuation', {}), "Valuation")
            ], className="metrics-grid")
        ], className="metrics-dashboard")
    ])

def calculate_overall_score(metrics):
    """Calculate the overall score on a 1-5 scale"""
    total_score = 0
    total_metrics = 0
    
    for category, category_data in metrics.items():
        for metric_name, metric_data in category_data.items():
            if isinstance(metric_data, dict) and 'score' in metric_data:
                total_score += metric_data['score']
                total_metrics += 1
    
    return total_score / total_metrics if total_metrics > 0 else 1

def process_stock_data(ticker):
    try:
        # Fetch stock data
        df = yf.download(
            ticker,
            start=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
            end=datetime.now().strftime('%Y-%m-%d')
        )
        
        # Fetch financial data
        stock = yf.Ticker(ticker)
        financial_data = {
            'operating_margin': stock.info.get('operatingMargins', 0) * 100,
            'current_ratio': stock.info.get('currentRatio', 0),
            'quick_ratio': stock.info.get('quickRatio', 0),
            'debt_to_equity': stock.info.get('debtToEquity', 0),
            'return_on_equity': stock.info.get('returnOnEquity', 0) * 100,
            'return_on_assets': stock.info.get('returnOnAssets', 0) * 100,
            'asset_turnover': stock.info.get('assetTurnover', 0),
            'inventory_turnover': stock.info.get('inventoryTurnover', 0),
            'revenue_growth': stock.info.get('revenueGrowth', 0) * 100,
            'earnings_growth': stock.info.get('earningsGrowth', 0) * 100 if stock.info.get('earningsGrowth') else 0,
            'gross_margins': stock.info.get('grossMargins', 0) * 100,
            'profit_margins': stock.info.get('profitMargins', 0) * 100,
            'pe_ratio': stock.info.get('forwardPE', 0),
            'peg_ratio': stock.info.get('pegRatio', 0)
        }
        
        # Calculate metrics with raw scores (1-5)
        metrics, overall_score = calculate_metrics(financial_data)
        
        # Create the metrics dashboard
        return html.Div([
            html.H1(f"{ticker} Analysis"),
            generate_blurb(ticker, metrics, overall_score),
            create_metrics_dashboard(metrics, overall_score),
            dcc.Graph(figure=create_stock_figure(df)),
            html.Div([
                create_metrics_section(metrics[category], category)
                for category in metrics
            ], className="all-metrics-container")
        ])
        
    except Exception as e:
        return html.Div(f"Error processing data for {ticker}: {str(e)}") 