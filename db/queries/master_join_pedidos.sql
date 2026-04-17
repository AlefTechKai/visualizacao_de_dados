SELECT 
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
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
LEFT JOIN olist_customers_dataset c 
    ON o.customer_id = c.customer_id
LEFT JOIN olist_order_items_dataset oi 
    ON o.order_id = oi.order_id
LEFT JOIN olist_products_dataset p 
    ON oi.product_id = p.product_id
LEFT JOIN (
    -- Importante agrupar as coordenadas por CEP para evitar duplicidade em massa
    SELECT 
        geolocation_zip_code_prefix, 
        AVG(geolocation_lat) AS geolocation_lat, 
        AVG(geolocation_lng) AS geolocation_lng 
    FROM olist_geolocation_dataset 
    GROUP BY geolocation_zip_code_prefix
) geo_c 
    ON c.customer_zip_code_prefix = geo_c.geolocation_zip_code_prefix
GROUP BY 
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    geo_c.geolocation_lat,
    geo_c.geolocation_lng
-- Limitando a 50.000 para não estourar a memória do Streamlit local
LIMIT 50000;
