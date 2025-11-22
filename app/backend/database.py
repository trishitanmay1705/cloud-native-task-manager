import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

def init_db(app):
    # Default to SQLite for ease if DATABASE_URL not set
    database_url = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Create tables on startup
    with app.app_context():
        db.create_all()
        # Simple test query
        try:
            db.session.execute(text("SELECT 1"))
        except Exception as e:
            app.logger.error(f"Database connection error: {e}")
