import os
from dotenv import load_dotenv
import pymysql

load_dotenv()


def get_connection():
    conn = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port= int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return conn