from google.cloud import storage
import torch
from app.utils.prediction import LSTMModel
from app.config.cloud_config import CloudConfig

def save_model_to_cloud(model, ticker):
    """Save PyTorch model to Google Cloud Storage"""
    client = storage.Client()
    bucket = client.bucket(CloudConfig.BUCKET_NAME)
    
    # Save model locally first
    model_path = f"{ticker}_model.pt"
    torch.save(model.state_dict(), model_path)
    
    # Upload to cloud
    blob = bucket.blob(f"{CloudConfig.MODEL_STORAGE_PATH}{ticker}_model.pt")
    blob.upload_from_filename(model_path)
    
    # Clean up local file
    import os
    os.remove(model_path)

def load_model_from_cloud(ticker):
    """Load PyTorch model from Google Cloud Storage"""
    try:
        client = storage.Client()
        bucket = client.bucket(CloudConfig.BUCKET_NAME)
        blob = bucket.blob(f"{CloudConfig.MODEL_STORAGE_PATH}{ticker}_model.pt")
        
        # Download to temporary file
        model_path = f"{ticker}_model.pt"
        blob.download_to_filename(model_path)
        
        # Load model
        model = LSTMModel()
        model.load_state_dict(torch.load(model_path))
        
        # Clean up
        import os
        os.remove(model_path)
        
        return model
    except Exception as e:
        print(f"Error loading model from cloud: {str(e)}")
        return None 