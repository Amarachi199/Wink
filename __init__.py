from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
from flask_login import LoginManager
from flask_mail import Mail
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
import secrets
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS



# 

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO()
 


UPLOAD_FOLDER = 'static/uploads'  
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov'}
from app.models import User 

load_dotenv()

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_client = Redis(host=redis_host, port=redis_port, decode_responses=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:Amarachi1994@localhost:5433/mydatabase')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # 1 hour session expiration
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size 
    socketio = SocketIO(app)

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = bool(os.getenv('MAIL_USE_TLS', True))
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    
    
   
    app.redis_client = redis_client

    # group_manager = GroupManager(app.redis_client)
    # app.group_manager = group_manager
    # Initialize Elasticsearch
    elasticsearch_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
    elasticsearch_port = int(os.getenv('ELASTICSEARCH_PORT', 9200))
    elasticsearch_scheme = os.getenv('ELASTICSEARCH_SCHEME', 'http')  # Default to HTTP
 
    app.elasticsearch = Elasticsearch(
        [{'host': elasticsearch_host, 'port': elasticsearch_port, 'scheme': elasticsearch_scheme}]
    )
    

    # Register Blueprints (routes)
    from .routes import routes
    app.register_blueprint(routes)

    return app

# Create the app instance
app = create_app()

# Ensure app runs only when executed directly
if __name__ == '__main__':
     socketio.run(app, debug=True)
