import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import plotly.io as pio
import time

# Custom theme
pio.templates["custom"] = pio.templates["plotly_white"]
pio.templates["custom"].update({
    "layout": {
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
        "font": {"color": "#2c3e50", "size": 14},
        "xaxis": {
            "gridcolor": "#f2f2f2",
            "zerolinecolor": "#f2f2f2",
            "tickfont": {"color": "#2c3e50", "size": 12},
            "title_font": {"color": "#2c3e50", "size": 14}
        },
        "yaxis": {
            "gridcolor": "#f2f2f2",
            "zerolinecolor": "#f2f2f2",
            "tickfont": {"color": "#2c3e50", "size": 12},
            "title_font": {"color": "#2c3e50", "size": 14}
        },
    }
})

def create_stock_price_figure(df, title):
    fig = go.Figure()
    
    # Calculate price change
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    price_change = ((end_price - start_price) / start_price) * 100
    
    # Determine color based on price change
    if price_change >= 0:
        line_color = 'rgb(39, 174, 96)'  # Green
    else:
        line_color = 'rgb(192, 57, 43)'  # Red
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color=line_color, width=2)
    ))
    
    fig.update_layout(
        title=dict(
            text=f'{title} ({price_change:+.1f}%)',
            font=dict(size=24, color='black', family="Inter"),
            x=0.5,
            xanchor="center"
        ),
        xaxis_title='Date',
        yaxis_title='Price ($)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=40, l=40, r=40)
    )
    
    return fig

def create_volume_figure(df, title):
    fig = go.Figure()
    
    # Calculate volume change
    start_volume = df['Volume'].iloc[0]
    end_volume = df['Volume'].iloc[-1]
    volume_change = ((end_volume - start_volume) / start_volume) * 100
    
    # Determine color based on volume change
    if volume_change >= 0:
        bar_color = 'rgb(39, 174, 96)'  # Green
    else:
        bar_color = 'rgb(192, 57, 43)'  # Red
    
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        marker_color=bar_color
    ))
    
    fig.update_layout(
        title=dict(
            text=f'{title} ({volume_change:+.1f}%)',
            font=dict(size=24, color='black', family="Inter"),
            x=0.5,
            xanchor="center"
        ),
        xaxis_title='Date',
        yaxis_title='Volume',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=40, l=40, r=40)
    )
    
    return fig

def get_financial_metrics(stock):
    try:
        info = stock.info
        
        # Basic validation of info
        if not info or not isinstance(info, dict):
            print("Invalid info data received")
            return None, None, None
            
        financials = stock.financials
        
        # Calculate metrics
        metrics = {
            'Profitability': {
                'Gross Margin': {
                    'value': info.get('grossMargins', 0) * 100,
                    'threshold': {'good': 40, 'medium': 20}
                },
                'Operating Margin': {
                    'value': info.get('operatingMargins', 0) * 100,
                    'threshold': {'good': 15, 'medium': 8}
                },
                'Net Margin': {
                    'value': info.get('profitMargins', 0) * 100,
                    'threshold': {'good': 10, 'medium': 5}
                },
                'FCF Margin': {
                    'value': (info.get('freeCashflow', 0) / info.get('totalRevenue', 1)) * 100,
                    'threshold': {'good': 10, 'medium': 5}
                },
                'Unprofitable': {
                    'value': info.get('profitMargins', 0) < 0,
                    'threshold': {'good': False, 'medium': False},
                    'inverse': True
                }
            },
            'Management': {
                'ROE': {
                    'value': info.get('returnOnEquity', 0) * 100,
                    'threshold': {'good': 15, 'medium': 10}
                },
                'ROIC': {
                    'value': info.get('returnOnCapital', 0) * 100,
                    'threshold': {'good': 15, 'medium': 10}
                },
                'ROA': {
                    'value': info.get('returnOnAssets', 0) * 100,
                    'threshold': {'good': 5, 'medium': 3}
                }
            },
            'Growth': {
                'Revenue Growth': {
                    'value': info.get('revenueGrowth', 0) * 100,
                    'threshold': {'good': 15, 'medium': 8}
                },
                'Earnings Growth': {
                    'value': info.get('earningsGrowth', 0) * 100,
                    'threshold': {'good': 15, 'medium': 8}
                }
            },
            'Financial Health': {
                'Current Ratio': {
                    'value': info.get('currentRatio', 0),
                    'threshold': {'good': 2, 'medium': 1.5}
                },
                'Debt to Equity': {
                    'value': info.get('debtToEquity', 0) / 100,
                    'threshold': {'good': 1, 'medium': 2},
                    'inverse': True
                },
                'Interest Coverage': {
                    'value': info.get('interestCoverage', 0),
                    'threshold': {'good': 5, 'medium': 3}
                }
            },
            'Valuation': {
                'P/E Ratio': {
                    'value': info.get('forwardPE', 0),
                    'threshold': {'good': 20, 'medium': 30},
                    'inverse': True
                },
                'PEG Ratio': {
                    'value': info.get('pegRatio', 0),
                    'threshold': {'good': 1, 'medium': 2},
                    'inverse': True
                },
                'P/B Ratio': {
                    'value': info.get('priceToBook', 0),
                    'threshold': {'good': 3, 'medium': 5},
                    'inverse': True
                }
            },
            'Analyst': {
                'Recommendation': {
                    'value': info.get('recommendationMean', 3),
                    'threshold': {'good': 2, 'medium': 3},
                    'inverse': True
                },
                'Target Upside': {
                    'value': ((info.get('targetMeanPrice', info.get('currentPrice', 0)) / 
                              info.get('currentPrice', 1)) - 1) * 100,
                    'threshold': {'good': 20, 'medium': 10}
                }
            }
        }
        
        # Calculate overall score
        scores = {}
        for category, category_metrics in metrics.items():
            category_score = 0
            max_score = len(category_metrics) * 2
            for metric_name, metric_data in category_metrics.items():
                if metric_data['value'] >= metric_data['threshold']['good']:
                    category_score += 2
                elif metric_data['value'] >= metric_data['threshold']['medium']:
                    category_score += 1
                if metric_data.get('inverse'):
                    category_score = max_score - category_score
            scores[category] = (category_score / max_score) * 100
        
        overall_score = sum(scores.values()) / len(scores)
        
        return metrics, scores, overall_score
        
    except Exception as e:
        return None, None, None

def fetch_stock_data(ticker_symbol, period='1y', interval='1d'):
    print(f"Fetching data for {ticker_symbol}...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Remove the progress parameter
        stock_data = ticker.history(period=period, interval=interval)
        return stock_data
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {str(e)}")
        return None

def get_stock_data(ticker):
    if not ticker:
        return {}, {}, {}, {}, 0, ''
    
    try:
        print(f"Fetching data for {ticker}...")
        
        # Use Ticker object with retry logic
        max_retries = 5
        retry_delay = 5
        df = None  # Initialize df outside the loop
        stock = None
        
        for attempt in range(max_retries):
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(
                    period="1y",
                    interval="1d"
                )
                
                # Try to access info to verify the connection
                _ = stock.info
                
                if not df.empty:
                    print(f"Successfully fetched data for {ticker}")
                    break
                    
                print(f"Attempt {attempt + 1}: Empty data, retrying...")
                time.sleep(retry_delay * (attempt + 1))  # Increase delay with each attempt
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                continue
        
        # Check if we got valid data
        if df is None or df.empty:
            return {}, {}, {}, {}, 0, f"Could not fetch data for {ticker} after {max_retries} attempts"
            
        # Create figures
        price_fig = create_stock_price_figure(df, f"{ticker} Stock Price")
        volume_fig = create_volume_figure(df, f"{ticker} Trading Volume")
        
        # Get metrics with separate retry logic
        metrics = None
        scores = None
        overall_score = 0
        
        for attempt in range(max_retries):
            try:
                metrics, scores, overall_score = get_financial_metrics(stock)
                if metrics is not None:
                    break
                print(f"Attempt {attempt + 1}: Metrics fetch failed, retrying...")
                time.sleep(retry_delay * (attempt + 1))
            except Exception as e:
                print(f"Metrics fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                continue
        
        if metrics is None:
            return price_fig, volume_fig, {}, {}, 0, "Could not fetch financial metrics"
            
        score_fig = create_score_visualization(scores, overall_score)
        
        return price_fig, volume_fig, score_fig, metrics, overall_score, ''
        
    except Exception as e:
        print(f"Error in get_stock_data: {str(e)}")
        return {}, {}, {}, {}, 0, f'Error: {str(e)}'

def create_score_visualization(scores, overall_score):
    categories = list(scores.keys())
    values = list(scores.values())
    
    # Determine color based on overall score
    if overall_score >= 70:
        color = 'rgb(39, 174, 96)'  # Green
    elif overall_score >= 50:
        color = 'rgb(241, 196, 15)'  # Yellow
    else:
        color = 'rgb(192, 57, 43)'  # Red
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor=f'rgba{color[3:-1]}, 0.3)',  # Convert rgb to rgba
        line=dict(color=color, width=2),
        name='Company Score'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(0,0,0,0.1)',  # Darker grid lines
                tickfont=dict(color=color)
            ),
            angularaxis=dict(
                tickfont=dict(color=color),
                gridcolor='rgba(0,0,0,0.1)'  # Darker grid lines
            ),
            bgcolor='rgba(0,0,0,0.02)'  # Very light gray background
        ),
        showlegend=False,
        title=dict(
            text=f'Overall Score: {overall_score:.1f}%',
            font=dict(size=24, color=color, family="Inter"),
            x=0.5,
            xanchor="center"
        ),
        paper_bgcolor='white',
        margin=dict(t=60, b=40)
    )
    
    return fig 