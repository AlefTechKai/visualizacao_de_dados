import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from db.conexao_db import get_connection
from funcoes.api import buscar_dados_api


def testar_db():
    """
    Testa conexão com banco
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1;")
        resultado = cursor.fetchone()

        cursor.close()
        conn.close()

        print("✅ Banco conectado:", resultado)
        return True

    except Exception as e:
        print("❌ Erro no banco:", e)
        return False


def testar_api():
    """
    Testa conexão com API
    """
    try:
        df = buscar_dados_api()

        print("✅ API conectada! Linhas recebidas:", len(df))
        return True

    except Exception as e:
        print("❌ Erro na API:", e)
        return False


def testar_conexao(origem="api"):
    """
    Função anfíbia: decide o que testar
    """
    if origem == "db":
        return testar_db()

    elif origem == "api":
        return testar_api()

    else:
        raise ValueError("Origem inválida. Use 'db' ou 'api'")

if __name__ == "__main__":
    print("--- INICIANDO TESTE ---")
    # Testa a API e o banco de uma vez
    testar_conexao("api")
    testar_conexao("db")