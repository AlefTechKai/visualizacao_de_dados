import streamlit as st
import pandas as pd
import plotly.express as px

from funcoes.api import buscar_dados_api


# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard de Pedidos",
    layout="wide"
)

st.title("📊 Dashboard de Análise de Pedidos")


# =========================
# CARREGAR DADOS
# =========================
@st.cache_data
def load_data():
    df = buscar_dados_api()

    # Corrigir decimal com vírgula -> ponto
    for col in ["customer_lat", "customer_lng", "seller_lat", "seller_lng"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", ".")
                .astype(float)
            )

    return df


df = load_data()


# =========================
# KPIs
# =========================
st.subheader("📌 Visão Geral")

col1, col2, col3 = st.columns(3)

col1.metric("Total de pedidos", len(df))
col2.metric("Status mais comum", df["order_status"].value_counts().idxmax())
col3.metric("Status únicos", df["order_status"].nunique())


# =========================
# GRÁFICOS
# =========================

st.subheader("📦 Status dos pedidos")

fig_status = px.bar(
    df["order_status"].value_counts().reset_index(),
    x="order_status",
    y="count",
    labels={"order_status": "Status", "count": "Quantidade"},
    color="order_status"
)

st.plotly_chart(fig_status, use_container_width=True)


# =========================
# MAPA (VENDEDORES x CLIENTES)
# =========================

st.subheader("📍 Localização (Clientes x Vendedores)")

map_df = df.dropna(subset=["customer_lat", "customer_lng"])

fig_map = px.scatter_mapbox(
    map_df,
    lat="customer_lat",
    lon="customer_lng",
    zoom=3,
    height=500,
    mapbox_style="open-street-map",
    hover_data=["order_status"]
)

st.plotly_chart(fig_map, use_container_width=True)


# =========================
# HISTÓRICO TEMPORAL
# =========================

st.subheader("📅 Pedidos ao longo do tempo")

df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

timeline = df.groupby(df["order_purchase_timestamp"].dt.date).size().reset_index(name="qtd")

fig_time = px.line(
    timeline,
    x="order_purchase_timestamp",
    y="qtd",
    markers=True
)

st.plotly_chart(fig_time, use_container_width=True)