import os

class CloudConfig:
    # Replace with your actual project ID from gcloud init
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'stock-analysis-tool-mgs1')
    GOOGLE_CLOUD_REGION = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
    MODEL_ENDPOINT = os.getenv('MODEL_ENDPOINT', 'stock-analysis-endpoint')
    
    # Storage configuration
    # Replace with your bucket name from step 2
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'stock-models-mgs1')
    MODEL_STORAGE_PATH = 'models/stock_prediction/' 