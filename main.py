from db.teste_db import testar_conexao
from funcoes.api import buscar_dados_api


def main():
    origem = "api"  # fixo como você pediu

    print("🔍 Testando conexão...\n")

    if not testar_conexao(origem):
        print("❌ Falha na conexão. Encerrando.")
        return

    print("\n🚀 Buscando dados...\n")

    df = buscar_dados_api()

    print("📊 Preview:1 ")
    print(df.head())


if __name__ == "__main__":
    main()
    
