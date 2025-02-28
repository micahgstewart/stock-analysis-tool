import yfinance as yf
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import plotly.graph_objects as go
from app.models.lstm import LSTMModel
from app.utils.model_storage import ModelStorage
import time

def prepare_data(df, sequence_length):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df['Close'].values.reshape(-1, 1))
    
    sequences, targets = [], []
    for i in range(len(scaled_data) - sequence_length):
        sequences.append(scaled_data[i:(i + sequence_length)])
        targets.append(scaled_data[i + sequence_length])
    
    # Convert to PyTorch tensors
    X = torch.FloatTensor(sequences)
    y = torch.FloatTensor(targets)
    
    return X, y, scaler

def train_and_save_model(X, y, ticker):
    """Train model and save to cloud"""
    model = LSTMModel()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters())
    
    # Training
    model.train()
    for _ in range(50):  # epochs
        optimizer.zero_grad()
        y_pred = model(X)
        loss = criterion(y_pred, y)
        loss.backward()
        optimizer.step()
    
    # Save to cloud
    model_path = f"{CloudConfig.MODEL_STORAGE_PATH}{ticker}_model.pt"
    save_model_to_cloud(model, CloudConfig.BUCKET_NAME, model_path)
    
    return model

model_storage = ModelStorage()

def predict_stock_prices(ticker, prediction_days):
    try:
        print(f"Fetching data for {ticker}...")
        
        # Use Ticker object with retry logic
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(
                    period="1y",
                    interval="1d"
                )
                
                if not df.empty:
                    break
                    
                print(f"Attempt {attempt + 1}: Retrying...")
                time.sleep(retry_delay)
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue
        
        if df.empty:
            print(f"No data found for {ticker}")
            return None, None, None
            
        print(f"Successfully downloaded data for {ticker}, shape: {df.shape}")
        
        # Prepare and train model
        X, y, scaler = prepare_data(df, 60)
        
        model = LSTMModel()
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters())
        
        # Training
        model.train()
        for epoch in range(50):
            optimizer.zero_grad()
            y_pred = model(X)
            loss = criterion(y_pred, y)
            loss.backward()
            optimizer.step()
            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Loss: {loss.item():.4f}")
        
        # Make predictions
        model.eval()
        with torch.no_grad():
            last_sequence = X[-1:]
            predictions = []
            
            for _ in range(prediction_days):
                next_pred = model(last_sequence)
                predictions.append(next_pred.item())
                
                new_sequence = last_sequence.clone()
                new_sequence[0] = torch.roll(new_sequence[0], -1)
                new_sequence[0, -1] = next_pred
                last_sequence = new_sequence
        
        predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        future_dates = pd.date_range(start=df.index[-1], periods=prediction_days + 1)[1:]
        
        return predictions, future_dates, df
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return None, None, None

def create_prediction_figure(df, predictions, future_dates, ticker):
    fig = go.Figure()
    
    # Plot historical data
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Historical',
        line=dict(color='rgb(41, 128, 185)')
    ))
    
    # Plot predictions
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=predictions.flatten(),
        mode='lines',
        name='Prediction',
        line=dict(color='rgb(39, 174, 96)', dash='dash')
    ))
    
    fig.update_layout(
        title=dict(
            text=f'{ticker} Stock Price Prediction',
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