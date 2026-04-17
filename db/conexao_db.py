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

# V2: Função Otimizada para SQLAlchemy (O Padrão Ouro exigido pelo Pandas hoje)
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

def get_engine():
    # Usar URL.create garante que senhas com @, #, etc não quebrem a conexão!
    url_object = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME")
    )
    return create_engine(url_object)
