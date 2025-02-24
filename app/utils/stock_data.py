import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

def get_stock_data(ticker):
    if not ticker:
        return {}, {}, ''
    
    try:
        # Fetch stock data
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        df = stock.history(start=start_date, end=end_date)
        
        # Create price figure
        price_fig = go.Figure()
        price_fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price'
        ))
        price_fig.update_layout(
            title=f'{ticker} Stock Price',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            template='plotly_white'
        )
        
        # Create volume figure
        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume'
        ))
        volume_fig.update_layout(
            title=f'{ticker} Trading Volume',
            xaxis_title='Date',
            yaxis_title='Volume',
            template='plotly_white'
        )
        
        return price_fig, volume_fig, ''
        
    except Exception as e:
        return {}, {}, f'Error: {str(e)}' 