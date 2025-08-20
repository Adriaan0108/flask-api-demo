from src import create_app, db

app = create_app()

with app.app_context():  # Must push context for Flask-SQLAlchemy
    db.create_all()
    print("Database tables created!")