from db.conexao_db import get_connection
import pandas as pd


def buscar_dados():
    conn = get_connection()

    query = "SELECT 1 as exemplo"

    df = pd.read_sql(query, conn)

    conn.close()

    return df