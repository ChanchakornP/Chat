import os


class Config(object):
    """Base config, uses staging database server."""

    TESTING = False
    DB_SERVER = "localhost"
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5002")
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///your-database.db'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SECRET_KEY = 'your-secret-key'
    SERVER_NAME = "localhost:5002"  # Update this to your server name and port
    APPLICATION_ROOT = "/"  # Update this if your app is not at the root
    PREFERRED_URL_SCHEME = "http"  # Use 'https' if your app uses HTTPS
    # Celery configurations
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

    @property
    def DATABASE_URI(self):  # Note: all caps
        return f"mysql://user@{self.DB_SERVER}/foo"


class ProductionConfig(Config):
    """Uses production database server."""

    DB_SERVER = "192.168.19.32"


class DevelopmentConfig(Config):
    DB_SERVER = "localhost"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "mysql+pymysql://user:password@localhost:3307/dbname"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"


class TestingConfig(Config):
    DB_SERVER = "localhost"
    DATABASE_URI = "sqlite:///:memory:"
