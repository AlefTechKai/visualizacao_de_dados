import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def buscar_dados_api():
    url = os.getenv("API_URL")

    if not url:
        raise ValueError("API_URL não definida")

    df = pd.read_csv(url)

    return df