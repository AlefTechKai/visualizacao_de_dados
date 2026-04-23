import pandas as pd
from db.conexao_db import get_engine

engine = get_engine()
df = pd.read_sql('SHOW TABLES', con=engine)
for table in df.iloc[:, 0].tolist():
    if 'olist' in table.lower():
        print(table)
