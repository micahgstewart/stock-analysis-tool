from dash import Dash
from flask import Flask
from app.config import Config

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
    from app.routes.main import init_callbacks, layout
    app.layout = layout
    init_callbacks(app)
    
    return app 