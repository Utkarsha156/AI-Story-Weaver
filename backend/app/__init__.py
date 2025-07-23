import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from .extensions import db, jwt

def create_app():
    # Load environment variables in development
    if os.environ.get('FLASK_ENV') != 'production':
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(dotenv_path=dotenv_path)

    app = Flask(__name__, static_folder='../static')

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "query_string"]

    # CORS Configuration for production
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    allowed_origins = [frontend_url]
    
    # In development, also allow localhost variations
    if 'localhost' in frontend_url or os.environ.get('FLASK_ENV') != 'production':
        allowed_origins.extend([
            'http://localhost:5173',
            'http://127.0.0.1:5173',
            'https://localhost:5173'
        ])
    
    CORS(app, 
         resources={r"/api/*": {"origins": allowed_origins}}, 
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()
        
        # Register blueprints
        from .auth import auth_bp
        from .routes import main_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(main_bp, url_prefix='/api')

    return app