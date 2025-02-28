import sqlite3
import io
import torch
import os
from app.models.lstm import LSTMModel

class ModelStorage:
    def __init__(self, db_path='instance/models.db'):
        # Create instance directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            ticker TEXT PRIMARY KEY,
            model_data BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_model(self, model, ticker):
        """Save PyTorch model to SQLite"""
        buffer = io.BytesIO()
        torch.save(model.state_dict(), buffer)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO models (ticker, model_data, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (ticker, buffer.getvalue()))
        
        conn.commit()
        conn.close()
    
    def load_model(self, ticker):
        """Load PyTorch model from SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT model_data FROM models WHERE ticker = ?', (ticker,))
        result = cursor.fetchone()
        
        if result:
            buffer = io.BytesIO(result[0])
            model = LSTMModel()
            model.load_state_dict(torch.load(buffer))
            return model
        
        return None