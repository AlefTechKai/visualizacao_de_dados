-- ========================================================================================
-- MAPEAMENTO DE DOMÍNIO (OLIST)
-- ========================================================================================
-- a) olist_orders_dataset: Tabela Core. Contém o status do pedido e timestamps vitais.
-- b) olist_order_items_dataset: Detalhes dos itens de cada pedido.
-- c) olist_order_customer_dataset: Dimensão. Dados geográficos e de perfil de quem comprou.
-- d) olist_products_dataset: Dimensão. O catálogo de produtos.
-- e) olist_sellers_dataset: Dimensão. Quem vendeu (o marketplace).
-- f) olist_order_payments_dataset: Como foi pago. Relaciona por order_id.
-- g) olist_order_reviews_dataset: Avaliações (estrelas/comentários). Relaciona por order_id.
-- h) olist_geolocation_dataset: Coordenadas por CEP (Processamos com AVG para evitar duplicidade).
-- ========================================================================================

SELECT 
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    geo_c.geolocation_lat AS customer_lat,
    geo_c.geolocation_lng AS customer_lng,
    SUM(oi.price) AS total_valor_produtos,
    SUM(oi.freight_value) AS total_valor_frete,
    COUNT(oi.order_item_id) AS qtd_itens,
    GROUP_CONCAT(DISTINCT p.product_category_name SEPARATOR ', ') AS categorias_produtos
FROM olist_orders_dataset o

-- 1. Juntando com Cliente (1 para 1 no contexto da compra)
LEFT JOIN olist_order_customer_dataset c 
    ON o.customer_id = c.customer_id

-- 2. Juntando com Itens do Pedido (1 para N)
LEFT JOIN olist_order_items_dataset oi 
    ON o.order_id = oi.order_id

-- 3. Juntando com Produto para saber nome das categorias
LEFT JOIN olist_products_dataset p 
    ON oi.product_id = p.product_id

-- 4. Juntando com Geolocalização de forma inteligente
LEFT JOIN (
    SELECT 
        geolocation_zip_code_prefix, 
        AVG(geolocation_lat) AS geolocation_lat, 
        AVG(geolocation_lng) AS geolocation_lng 
    FROM olist_geolocation_dataset 
    GROUP BY geolocation_zip_code_prefix
) geo_c 
    ON c.customer_zip_code_prefix = geo_c.geolocation_zip_code_prefix

-- Agrupando em nível de PEDIDO para o Dashboard não ter linhas duplicadas!
GROUP BY 
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    geo_c.geolocation_lat,
    geo_c.geolocation_lng
