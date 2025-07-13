import os
from flask import Flask
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)

    # Register blueprints or routes
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app 