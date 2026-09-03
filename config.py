import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PROXY_TOKEN = os.getenv("PROXY_TOKEN")

database = os.getenv("DB_NAME")

database_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

ADMIN_ID = int(os.getenv("ADMIN_ID"))


def get_connection():
    conn = mysql.connector.connect(
        **database_config,
        database=database
    )
    return conn
