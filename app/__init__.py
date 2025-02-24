from flask import Flask
from dash import Dash
from config.config import Config

def create_app():
    # Initialize Flask
    server = Flask(__name__)
    server.config.from_object(Config)
    
    # Initialize Dash
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/',
        assets_folder='static'
    )
    
    # Import and register routes
    from app.routes.main import init_callbacks
    init_callbacks(app)
    
    # Import and set layout
    from app.routes.main import layout
    app.layout = layout
    
    return app 