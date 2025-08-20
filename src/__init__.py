from flask import Flask
import os
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Config from environment variables
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DB_URI", "sqlite:///bookmarks.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["ENV"] = os.environ.get("FLASK_ENV", "development")  # reads the environment variable, default to development if not set
    app.config["DEBUG"] = app.config["ENV"] == "development" # if ENV is development, set Flask’s debug mode as true
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    # Initialize extensions
    db.init_app(app)

    JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    # Auto-create tables in development
    if app.config["ENV"] == "development":
        with app.app_context():
            db.create_all()
            print("Development database tables created!")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
