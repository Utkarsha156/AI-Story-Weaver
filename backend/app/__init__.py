import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from .extensions import db, jwt

def create_app():
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)

    app = Flask(__name__, static_folder='../static')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "query_string"]

    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    CORS(app, resources={r"/api/*": {"origins": [frontend_url]}}, supports_credentials=True)

    db.init_app(app)
    jwt.init_app(app)

    # The with app.app_context() is needed to ensure the app is ready for blueprints
    with app.app_context():
        from .auth import auth_bp
        from .routes import main_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(main_bp, url_prefix='/api')

    return app