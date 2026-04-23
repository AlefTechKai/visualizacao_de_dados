import pandas as pd
from db.conexao_db import get_engine

try:
    engine = get_engine()
    with open('db/queries/query_informacoes.sql', 'r', encoding='utf-8') as f:
        query = f.read()
    df = pd.read_sql(query, con=engine)
    print("Sucesso! Linhas:", len(df))
except Exception as e:
    import traceback
    traceback.print_exc()
