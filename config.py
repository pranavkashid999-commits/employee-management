import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv("db_host")
    DB_USER = os.getenv("db_user")
    DB_PASSWORD = os.getenv("db_password")
    DB_NAME = os.getenv("db_name")
    DB_PORT = os.getenv("db_port")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False