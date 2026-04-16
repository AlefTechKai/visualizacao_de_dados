import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from funcoes.api import buscar_dados_api


# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard de Pedidos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================
# CSS PERSONALIZADO (arquivo externo)
# =========================
import pathlib

css_path = pathlib.Path(__file__).parent / "src" / "css" / "style.css"
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



# =========================
# CARREGAR DADOS
# =========================
@st.cache_data(ttl=600)
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

    # Converter timestamps
    if "order_purchase_timestamp" in df.columns:
        df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")

    if "order_delivered_customer_date" in df.columns:
        df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"], errors="coerce")

    if "order_estimated_delivery_date" in df.columns:
        df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"], errors="coerce")

    return df


df = load_data()


# =========================
# PALETA DE CORES PARA GRÁFICOS
# =========================
COLORS = [
    "#667eea", "#764ba2", "#f093fb", "#f5576c",
    "#4facfe", "#00f2fe", "#43e97b", "#38f9d7",
    "#fa709a", "#fee140", "#a18cd1", "#fbc2eb",
]

PLOTLY_TEMPLATE = "plotly_dark"


# =========================
# SIDEBAR - NAVEGAÇÃO E FILTROS
# =========================
with st.sidebar:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        text-align: center;
    ">
        <div style="font-size: 2.5rem;">🚀</div>
        <div style="color: #fff; font-size: 1.2rem; font-weight: 500; margin-top: 0.2rem;">Navegação</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    pagina = st.selectbox(
        "📂 Selecione a visualização",
        options=[
            "🏠 Visão Geral",
            "📦 Análise de Status",
            "📍 Mapa Geográfico",
            "📅 Histórico Temporal",
            "📋 Dados Brutos"
        ],
        index=0,
        help="Escolha qual seção do dashboard deseja visualizar"
    )

    st.markdown("---")
    st.markdown("## 🎛️ Filtros")

    # Filtro de Status
    todos_status = sorted(df["order_status"].unique().tolist())
    status_selecionados = st.multiselect(
        "📌 Filtrar por Status",
        options=todos_status,
        default=[],
        help="Deixe vazio para ver todos. Selecione para filtrar."
    )

    # Filtro de Data (com toggle)
    if "order_purchase_timestamp" in df.columns and df["order_purchase_timestamp"].notna().any():
        filtrar_periodo = st.toggle("📆 Filtrar por Período", value=False)

        if filtrar_periodo:
            datas_validas = df["order_purchase_timestamp"].dropna()
            data_min = datas_validas.min().date()
            data_max = datas_validas.max().date()

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                data_inicio = st.date_input("De", value=data_min, min_value=data_min, max_value=data_max)
            with col_d2:
                data_fim = st.date_input("Até", value=data_max, min_value=data_min, max_value=data_max)
        else:
            data_inicio = None
            data_fim = None
    else:
        data_inicio = None
        data_fim = None

    st.markdown("---")

    # Botão de recarregar
    if st.button("🔄 Recarregar Dados", width="stretch", type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        "<div style='text-align:center; color: rgba(180,180,210,0.5); font-size:0.75rem; margin-top: 100px;'>"
        "Dashboard v2.0<br>Feito com ❤️ e Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


# =========================
# APLICAR FILTROS
# =========================
# Se nenhum status selecionado → mostra TODOS os dados
if status_selecionados:
    df_filtrado = df[df["order_status"].isin(status_selecionados)].copy()
else:
    df_filtrado = df.copy()

if data_inicio and data_fim and "order_purchase_timestamp" in df_filtrado.columns:
    mask = (
        (df_filtrado["order_purchase_timestamp"].dt.date >= data_inicio) &
        (df_filtrado["order_purchase_timestamp"].dt.date <= data_fim)
    )
    df_filtrado = df_filtrado[mask]


# =========================
# HEADER
# =========================
st.markdown("""
<div class="dashboard-header">
    <h1>📊 Dashboard de Análise de Pedidos</h1>
    <p>Análise completa e interativa dos seus dados de pedidos em tempo real</p>
</div>
""", unsafe_allow_html=True)


# =========================
# KPIs (sempre visíveis)
# =========================
total_pedidos = len(df_filtrado)
status_mais_comum = df_filtrado["order_status"].value_counts().idxmax() if not df_filtrado.empty else "N/A"
qtd_status = df_filtrado["order_status"].nunique() if not df_filtrado.empty else 0

# Calcular pedidos entregues
pedidos_entregues = len(df_filtrado[df_filtrado["order_status"] == "delivered"]) if not df_filtrado.empty else 0
taxa_entrega = f"{(pedidos_entregues / total_pedidos * 100):.1f}%" if total_pedidos > 0 else "0%"

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card kpi-1" align="center">
        <div class="kpi-icon">📦</div>
        <div class="kpi-value">{total_pedidos:,}</div>
        <div class="kpi-label">Total de Pedidos</div>
    </div>
    <div class="kpi-card kpi-2" align="center">
        <div class="kpi-icon">🏆</div>
        <div class="kpi-value">{status_mais_comum}</div>
        <div class="kpi-label">Status Mais Comum</div>
    </div>
    <div class="kpi-card kpi-3" align="center">
        <div class="kpi-icon">🏷️</div>
        <div class="kpi-value">{qtd_status}</div>
        <div class="kpi-label">Status Únicos</div>
    </div>
    <div class="kpi-card kpi-4" align="center">
        <div class="kpi-icon">✅</div>
        <div class="kpi-value">{taxa_entrega}</div>
        <div class="kpi-label">Taxa de Entrega</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ╔══════════════════════════════════════════╗
# ║         PÁGINAS / VISUALIZAÇÕES          ║
# ╚══════════════════════════════════════════╝

# ─────────────────────────────────────
# 🏠 VISÃO GERAL
# ─────────────────────────────────────
if pagina == "🏠 Visão Geral":
    st.markdown('<div class="section-title">🏠 Visão Geral do Dashboard</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Gráfico de pizza - Distribuição de status
        if not df_filtrado.empty:
            status_counts = df_filtrado["order_status"].value_counts().reset_index()
            status_counts.columns = ["status", "quantidade"]

            fig_pizza = px.pie(
                status_counts,
                names="status",
                values="quantidade",
                title="🍕 Distribuição por Status",
                color_discrete_sequence=COLORS,
                hole=0.45,
                template=PLOTLY_TEMPLATE,
            )
            fig_pizza.update_traces(
                textposition="inside",
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Qtd: %{value}<br>Porcentagem: %{percent}<extra></extra>"
            )
            fig_pizza.update_layout(
                font=dict(family="Inter"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=60, b=80, l=20, r=20),
                height=420,
            )
            st.plotly_chart(fig_pizza, width="stretch")

    with col_b:
        # Gráfico de barras horizontal - Top status
        if not df_filtrado.empty:
            status_counts = df_filtrado["order_status"].value_counts().reset_index()
            status_counts.columns = ["status", "quantidade"]

            fig_bar_h = px.bar(
                status_counts.sort_values("quantidade"),
                x="quantidade",
                y="status",
                orientation="h",
                title="📊 Ranking de Status",
                color="quantidade",
                color_continuous_scale=["#764ba2", "#667eea", "#4facfe", "#43e97b"],
                template=PLOTLY_TEMPLATE,
            )
            fig_bar_h.update_layout(
                font=dict(family="Inter"),
                coloraxis_showscale=False,
                margin=dict(t=60, b=40, l=20, r=20),
                height=420,
                yaxis_title="",
                xaxis_title="Quantidade",
            )
            fig_bar_h.update_traces(
                hovertemplate="<b>%{y}</b><br>Quantidade: %{x}<extra></extra>"
            )
            st.plotly_chart(fig_bar_h, width="stretch")

    # Linha do tempo resumida
    if not df_filtrado.empty and "order_purchase_timestamp" in df_filtrado.columns:
        st.markdown('<div class="section-title">📈 Tendência de Pedidos</div>', unsafe_allow_html=True)

        timeline = (
            df_filtrado
            .dropna(subset=["order_purchase_timestamp"])
            .groupby(df_filtrado["order_purchase_timestamp"].dt.to_period("M").astype(str))
            .size()
            .reset_index(name="qtd")
        )
        timeline.columns = ["mes", "qtd"]

        fig_area = px.area(
            timeline,
            x="mes",
            y="qtd",
            title="📅 Pedidos por Mês",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=["#667eea"],
        )
        fig_area.update_layout(
            font=dict(family="Inter"),
            margin=dict(t=60, b=40, l=20, r=20),
            height=350,
            xaxis_title="Mês",
            yaxis_title="Quantidade de Pedidos",
        )
        fig_area.update_traces(
            line=dict(width=3),
            fillcolor="rgba(102, 126, 234, 0.15)",
            hovertemplate="<b>%{x}</b><br>Pedidos: %{y}<extra></extra>"
        )
        st.plotly_chart(fig_area, width="stretch")


# ─────────────────────────────────────
# 📦 ANÁLISE DE STATUS
# ─────────────────────────────────────
elif pagina == "📦 Análise de Status":
    st.markdown('<div class="section-title">📦 Análise Detalhada de Status</div>', unsafe_allow_html=True)

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    else:
        # Seletor de tipo de gráfico
        tipo_grafico = st.selectbox(
            "🎨 Tipo de Gráfico",
            options=["Barras Verticais", "Barras Horizontais", "Pizza", "Donut", "Treemap", "Funil"],
            index=0,
        )

        status_counts = df_filtrado["order_status"].value_counts().reset_index()
        status_counts.columns = ["status", "quantidade"]

        if tipo_grafico == "Barras Verticais":
            fig = px.bar(
                status_counts,
                x="status",
                y="quantidade",
                color="status",
                color_discrete_sequence=COLORS,
                template=PLOTLY_TEMPLATE,
                title="📊 Status dos Pedidos - Barras Verticais",
            )
        elif tipo_grafico == "Barras Horizontais":
            fig = px.bar(
                status_counts.sort_values("quantidade"),
                x="quantidade",
                y="status",
                orientation="h",
                color="status",
                color_discrete_sequence=COLORS,
                template=PLOTLY_TEMPLATE,
                title="📊 Status dos Pedidos - Barras Horizontais",
            )
        elif tipo_grafico == "Pizza":
            fig = px.pie(
                status_counts,
                names="status",
                values="quantidade",
                color_discrete_sequence=COLORS,
                template=PLOTLY_TEMPLATE,
                title="🍕 Status dos Pedidos - Pizza",
            )
        elif tipo_grafico == "Donut":
            fig = px.pie(
                status_counts,
                names="status",
                values="quantidade",
                hole=0.5,
                color_discrete_sequence=COLORS,
                template=PLOTLY_TEMPLATE,
                title="🍩 Status dos Pedidos - Donut",
            )
        elif tipo_grafico == "Treemap":
            fig = px.treemap(
                status_counts,
                path=["status"],
                values="quantidade",
                color="quantidade",
                color_continuous_scale=["#764ba2", "#667eea", "#4facfe", "#43e97b"],
                template=PLOTLY_TEMPLATE,
                title="🌳 Status dos Pedidos - Treemap",
            )
        elif tipo_grafico == "Funil":
            fig = px.funnel(
                status_counts.sort_values("quantidade", ascending=False),
                x="quantidade",
                y="status",
                color="status",
                color_discrete_sequence=COLORS,
                template=PLOTLY_TEMPLATE,
                title="🔻 Status dos Pedidos - Funil",
            )

        fig.update_layout(
            font=dict(family="Inter"),
            margin=dict(t=60, b=40, l=20, r=20),
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig, width="stretch")

        # Tabela resumo
        st.markdown('<div class="section-title">📋 Resumo Numérico</div>', unsafe_allow_html=True)

        resumo = status_counts.copy()
        resumo["percentual"] = (resumo["quantidade"] / resumo["quantidade"].sum() * 100).round(2)
        resumo.columns = ["Status", "Quantidade", "Percentual (%)"]

        st.dataframe(
            resumo.style.format({"Percentual (%)": "{:.2f}%", "Quantidade": "{:,}"}),
            width="stretch",
            hide_index=True,
        )


# ─────────────────────────────────────
# 📍 MAPA GEOGRÁFICO
# ─────────────────────────────────────
elif pagina == "📍 Mapa Geográfico":
    st.markdown('<div class="section-title">📍 Localização Geográfica</div>', unsafe_allow_html=True)

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    else:
        # Seletor de estilo do mapa com nomes amigáveis
        estilos_mapa = {
            "🌙 Mapa Escuro": "carto-darkmatter",
            "☀️ Mapa Claro": "carto-positron",
        }
        estilo_escolhido = st.selectbox(
            "🗺️ Estilo do Mapa",
            options=list(estilos_mapa.keys()),
            index=0,
        )
        estilo_mapa = estilos_mapa[estilo_escolhido]

        map_df = df_filtrado.dropna(subset=["customer_lat", "customer_lng"])
        if map_df.empty:
            st.info("ℹ️ Sem dados de localização disponíveis.")
        else:
            fig_map = px.scatter_map(
                map_df,
                lat="customer_lat",
                lon="customer_lng",
                zoom=3,
                height=600,
                map_style=estilo_mapa,
                color="order_status",
                color_discrete_sequence=COLORS,
                hover_data=["order_status"],
                title="📍 Localização dos Pedidos",
                template=PLOTLY_TEMPLATE,
            )
            fig_map.update_layout(
                font=dict(family="Inter"),
                margin=dict(t=60, b=20, l=0, r=0),
            )
            st.plotly_chart(fig_map, width="stretch")

        # Estatísticas do mapa
        with st.expander("📊 Estatísticas de Localização", expanded=False):
            pontos_no_mapa = df_filtrado.dropna(subset=["customer_lat", "customer_lng"]).shape[0]
            st.metric("Pontos com localização", f"{pontos_no_mapa:,}")


# ─────────────────────────────────────
# 📅 HISTÓRICO TEMPORAL
# ─────────────────────────────────────
elif pagina == "📅 Histórico Temporal":
    st.markdown('<div class="section-title">📅 Análise Temporal</div>', unsafe_allow_html=True)

    if df_filtrado.empty or "order_purchase_timestamp" not in df_filtrado.columns:
        st.warning("⚠️ Nenhum dado temporal encontrado.")
    else:
        df_temp = df_filtrado.dropna(subset=["order_purchase_timestamp"]).copy()

        if df_temp.empty:
            st.warning("⚠️ Nenhum dado com data válida.")
        else:
            # Seletor de granularidade
            granularidade = st.selectbox(
                "⏱️ Granularidade Temporal",
                options=["Diário", "Semanal", "Mensal"],
                index=2,
            )

            if granularidade == "Diário":
                df_temp["periodo"] = df_temp["order_purchase_timestamp"].dt.date
            elif granularidade == "Semanal":
                df_temp["periodo"] = df_temp["order_purchase_timestamp"].dt.to_period("W").astype(str)
            else:
                df_temp["periodo"] = df_temp["order_purchase_timestamp"].dt.to_period("M").astype(str)

            timeline = df_temp.groupby("periodo").size().reset_index(name="qtd")
            timeline["periodo"] = timeline["periodo"].astype(str)

            # Seletor tipo de gráfico temporal
            tipo_temporal = st.radio(
                "📈 Tipo de visualização",
                options=["Linha", "Área", "Barras"],
                horizontal=True,
            )

            if tipo_temporal == "Linha":
                fig_time = px.line(
                    timeline,
                    x="periodo",
                    y="qtd",
                    markers=True,
                    title=f"📈 Pedidos - Visão {granularidade}",
                    template=PLOTLY_TEMPLATE,
                    color_discrete_sequence=["#667eea"],
                )
                fig_time.update_traces(line=dict(width=3))
            elif tipo_temporal == "Área":
                fig_time = px.area(
                    timeline,
                    x="periodo",
                    y="qtd",
                    title=f"📈 Pedidos - Visão {granularidade}",
                    template=PLOTLY_TEMPLATE,
                    color_discrete_sequence=["#667eea"],
                )
                fig_time.update_traces(
                    line=dict(width=3),
                    fillcolor="rgba(102, 126, 234, 0.2)",
                )
            else:
                fig_time = px.bar(
                    timeline,
                    x="periodo",
                    y="qtd",
                    title=f"📊 Pedidos - Visão {granularidade}",
                    template=PLOTLY_TEMPLATE,
                    color="qtd",
                    color_continuous_scale=["#764ba2", "#667eea", "#4facfe"],
                )
                fig_time.update_layout(coloraxis_showscale=False)

            fig_time.update_layout(
                font=dict(family="Inter"),
                margin=dict(t=60, b=40, l=20, r=20),
                height=450,
                xaxis_title="Período",
                yaxis_title="Quantidade de Pedidos",
            )
            fig_time.update_traces(
                hovertemplate="<b>%{x}</b><br>Pedidos: %{y}<extra></extra>"
            )
            st.plotly_chart(fig_time, width="stretch")

            # Gráfico de status ao longo do tempo
            st.markdown('<div class="section-title">📊 Status ao Longo do Tempo</div>', unsafe_allow_html=True)

            timeline_status = (
                df_temp
                .groupby(["periodo", "order_status"])
                .size()
                .reset_index(name="qtd")
            )
            timeline_status["periodo"] = timeline_status["periodo"].astype(str)

            fig_stack = px.bar(
                timeline_status,
                x="periodo",
                y="qtd",
                color="order_status",
                title="📊 Composição de Status por Período",
                template=PLOTLY_TEMPLATE,
                color_discrete_sequence=COLORS,
                barmode="stack",
            )
            fig_stack.update_layout(
                font=dict(family="Inter"),
                margin=dict(t=60, b=40, l=20, r=20),
                height=450,
                xaxis_title="Período",
                yaxis_title="Quantidade",
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            )
            st.plotly_chart(fig_stack, width="stretch")


# ─────────────────────────────────────
# 📋 DADOS BRUTOS
# ─────────────────────────────────────
elif pagina == "📋 Dados Brutos":
    st.markdown('<div class="section-title">📋 Explorador de Dados</div>', unsafe_allow_html=True)

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
    else:
        # Seletor de colunas
        todas_colunas = df_filtrado.columns.tolist()
        colunas_selecionadas = st.multiselect(
            "📑 Selecionar Colunas para Exibir",
            options=todas_colunas,
            default=todas_colunas[:8] if len(todas_colunas) > 8 else todas_colunas,
        )

        if colunas_selecionadas:
            # Pesquisa
            busca = st.text_input("🔍 Pesquisar nos dados", placeholder="Digite para filtrar...")

            df_display = df_filtrado[colunas_selecionadas].copy()

            if busca:
                mask = df_display.astype(str).apply(
                    lambda col: col.str.contains(busca, case=False, na=False)
                ).any(axis=1)
                df_display = df_display[mask]

            st.markdown(f"**Exibindo {len(df_display):,} de {len(df_filtrado):,} registros**")

            st.dataframe(
                df_display,
                width="stretch",
                height=500,
            )

            # Botão para download
            csv = df_display.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=csv,
                file_name="dados_filtrados.csv",
                mime="text/csv",
                width="stretch",
                type="primary",
            )
        else:
            st.info("ℹ️ Selecione ao menos uma coluna para visualizar.")


# =========================
# FOOTER
# =========================
st.markdown("""
<div class="footer">
    <p>📊 Dashboard de Pedidos • Desenvolvido por Alef B.R. /Opus 4.6(thinking) com Streamlit & Plotly • Dados em tempo real</p>
</div>
""", unsafe_allow_html=True)