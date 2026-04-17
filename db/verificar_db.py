import os
import pandas as pd
from db.conexao_db import get_connection

def verificar_db():
    try:
        # Pega a conexao usando o modulo que ja temos
        conexao = get_connection()
        
        # -----------------------------------------------------------------------------
        # 1. ENTENDENDO AS TABELAS (O que cada uma faz e como se relacionam)
        # -----------------------------------------------------------------------------
        """
        ========================================================================================
        Mapeamento de Domínio (Olist):
        ========================================================================================
        a) olist_orders_dataset: Tabela Fato. O coração do modelo. Contém o status do pedido e timestamps vitais.
           Chave Primária: order_id
           
        b) olist_order_items_dataset: Tabela Fato. Cada produto do pedido.
           Chave Estrangeira: order_id (para orders), product_id (para products), seller_id (para sellers).
           
        c) olist_customers_dataset: Tabela Dimensão. Quem comprou. Note que customer_id muda por pedido, 
           mas o customer_unique_id identifica a pessoa única.
           
        d) olist_products_dataset: Tabela Dimensão. O catálogo de produtos.
        
        e) olist_sellers_dataset: Tabela Dimensão. Quem vendeu (o marketplace).
           
        f) olist_order_payments_dataset: Dimensão/Fato. Como foi pago. Relaciona por order_id.
           
        g) olist_order_reviews_dataset: Dimensão. Avaliações (estrelas/comentários). Relaciona por order_id.
           
        h) olist_geolocation_dataset: Dimensão. Coordenadas por CEP.
           CUIDADO: Se fizer join direto aqui, vai gerar duplicidade massiva, pois um CEP pode ter múltiplos pontos (lat/long) mapeados.
        ========================================================================================
        """

        # -----------------------------------------------------------------------------
        # 2. QUERY FINAL: query_informacoes
        # -----------------------------------------------------------------------------
        # Dica Ouro: Use LEFT JOIN a partir da tabela central (orders) em um modelo Star/Snowflake.
        # Assim garantimos que mesmo que um pedido não tenha avaliação, ele ainda aparece no DataFrame final.
        query_informacoes = """
            SELECT 
                -- 1. Info Core do Pedido
                o.order_id,
                o.order_status,
                o.order_purchase_timestamp,
                
                -- 2. Info do Cliente
                c.customer_unique_id,
                c.customer_city,
                c.customer_state,
                
                -- 3. Info de Finanças / Itens
                oi.product_id,
                oi.price,
                oi.freight_value,
                
                -- 4. Info Produto e MarketPlace
                p.product_category_name,
                s.seller_city,
                s.seller_state,
                
                -- 5. Info de Pagamento e Satisfação
                pay.payment_type,
                pay.payment_value,
                r.review_score
                
            FROM olist_orders_dataset AS o
            
            -- O que o cliente pediu?
            LEFT JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
            
            -- Quais os itens desse pedido? (Atenção: multiplicará as linhas de orders pelos n itens)
            LEFT JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
            
            -- O que são esses itens?
            LEFT JOIN olist_products_dataset p ON oi.product_id = p.product_id
            
            -- Quem vendeu esses itens?
            LEFT JOIN olist_sellers_dataset s ON oi.seller_id = s.seller_id
            
            -- Como foi pago? (Atenção: Um pedido pode ter mais de um método de pagamento)
            LEFT JOIN olist_order_payments_dataset pay ON o.order_id = pay.order_id
            
            -- Como o cliente avaliou a compra?
            LEFT JOIN olist_order_reviews_dataset r ON o.order_id = r.order_id
            
            -- Limitado para testes, pra não travar sua máquina com milhares de joins atoa
            LIMIT 10;
        """

        print("Executando a Mestra: query_informacoes...")
        
        # O pulo do gato: já jogar no Pandas para uma visualização elegante no terminal
        df_informacoes = pd.read_sql(query_informacoes, con=conexao)
        
        print("\n=== Resultado da Master Query Olist (Head) ===")
        print(df_informacoes.to_string())
        print("\nDimensões do DF Retornado:", df_informacoes.shape)

    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")
    finally:
        conexao.close()
        print("\nConexão fechada com sucesso. Tudo nos conformes!")

if __name__ == "__main__":
    verificar_db()