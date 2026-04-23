import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from db.conexao_db import get_engine

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Olist Analytics Dashboard",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CSS PERSONALIZADO (arquivo externo ou embutido fallback)
# =========================
import pathlib
css_path = pathlib.Path(__file__).parent / "src" / "css" / "style.css"
if css_path.exists():
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    # Fallback CSS minimal + Dashboard elements
    st.markdown("""
        <style>
            .kpi-container { display: flex; gap: 15px; margin-bottom: 2rem; justify-content: space-between; flex-wrap: wrap;}
            .kpi-card { background: #1f1c2c; padding: 2.5rem 1.5rem; min-height: 150px; display: flex; flex-direction: column; justify-content: center; border-radius: 12px; flex: 1; text-align: center; border: 1px solid #333; box-shadow: 0 4px 6px rgba(0,0,0,0.3); min-width: 200px;}
            .kpi-value { font-size: 2.2rem; font-weight: 800; margin-top: 10px; }
            .kpi-label { font-size: 1rem; color: #a0a0a0; text-transform: uppercase; letter-spacing: 1px;}
            .section-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; color: #fff; border-bottom: 1px solid #333; padding-bottom: 10px; margin-top: 2rem;}
        </style>
    """, unsafe_allow_html=True)

# =========================
# CARREGAR DADOS V2 (Master Join .sql com Engine SQLAlchemy)
# =========================
@st.cache_data(ttl=600)
def load_data():
    caminho_sql = os.path.join(os.path.dirname(__file__), "db", "queries", "query_informacoes.sql")
    
    with open(caminho_sql, "r", encoding="utf-8") as f:
        query = f.read()

    # Em vez de pymysql raw, puxamos a super-engine
    engine = get_engine()
    
    # O sqlalchemy tem controle automatico de pooling, nao precisamos de bloco try/finally pra dar close manually()
    df = pd.read_sql(query, con=engine)

    # Preencher Valores Nulos em Financeiro caso existam nos JOINs
    if "total_valor_produtos" in df.columns:
        df["total_valor_produtos"] = df["total_valor_produtos"].fillna(0.0)
    if "total_valor_frete" in df.columns:
        df["total_valor_frete"] = df["total_valor_frete"].fillna(0.0)

    # Converter timestamps Core Olist
    if "order_purchase_timestamp" in df.columns:
        df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")

    # Converter Geo (Lat/Lng) e forcar clean
    for col in ["customer_lat", "customer_lng"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

    return df

with st.spinner("Conectando ao MySQL e rodando Query Master Olist..."):
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
        padding: 1.5rem;
        border-radius: 14px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255,255,255,0.1);
    ">
        <div style="font-size: 3rem; margin-bottom:10px;">🛍️</div>
        <div style="color: #fff; font-size: 1.4rem; font-weight: bold; letter-spacing: 1px;">Olist Analytics</div>
    </div>
    """, unsafe_allow_html=True)
    
    pagina = st.selectbox(
        "📂 Menu de Visualizações",
        options=[
            "🏠 Visão Executiva",
            "📈 Análise de Produtos",
            "📍 Dispersão Geográfica",
            "📋 Exportação de Dados"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("## 🎛️ Filtros Globais")

    # Filtro Status Principal
    todos_status = sorted(df["order_status"].dropna().unique().tolist())
    status_selecionados = st.multiselect(
        "📌 Status do Pedido",
        options=todos_status,
        default=[],
        help="Deixe vazio para filtrar todo o fluxo."
    )

    # Filtro Dinâmico de Cidades
    if "customer_state" in df.columns:
        top_estados = df["customer_state"].value_counts().index.tolist()
        estado_selecionados = st.multiselect(
            "🌆 Estados",
            options=sorted(top_estados),
            default=[]
        )
    else:
        estado_selecionados = []

    # Filtro Dinâmico de Ano
    if "order_purchase_timestamp" in df.columns:
        anos = sorted(df["order_purchase_timestamp"].dt.year.dropna().unique().astype(int).tolist())
        ano_selecionado = st.selectbox("📅 Filtrar por Ano", options=["Todos"] + anos, index=0)
    else:
        ano_selecionado = "Todos"



    # Rodapé do Menu Lateral
    st.markdown("""
    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); width: 100%; text-align: center; color: #a0a0a0; font-size: 0.9rem;">
        Feito com ❤️ e matplotly
    </div>
    """, unsafe_allow_html=True)

# =========================
# APLICAR FILTROS
# =========================
df_filtrado = df.copy()

if status_selecionados:
    df_filtrado = df_filtrado[df_filtrado["order_status"].isin(status_selecionados)]

if estado_selecionados:
    df_filtrado = df_filtrado[df_filtrado["customer_state"].isin(estado_selecionados)]

if ano_selecionado != "Todos" and "order_purchase_timestamp" in df.columns:
    df_filtrado = df_filtrado[df_filtrado["order_purchase_timestamp"].dt.year == ano_selecionado]


# =========================
# HEADER E KPIS
# =========================
st.markdown("""
<div style="margin-bottom: 10px;">
    <h1 style='margin-bottom:5px; font-weight:800; font-size: 2.8rem;'>📊 Master Dashboard Olist</h1>
    <p style='color: #888; font-size: 1.1rem;'>Análise Focada do fluxo de Join Principal extraído do seu Banco (Pedidos -> Receita -> Geo)</p>
</div>
""", unsafe_allow_html=True)

# Cálculo de Métricas Focadas em Business
total_pedidos = len(df_filtrado)
faturamento_total = df_filtrado["total_valor_produtos"].sum() if not df_filtrado.empty else 0
frete_total = df_filtrado["total_valor_frete"].sum() if not df_filtrado.empty else 0
ticket_medio = (faturamento_total / total_pedidos) if total_pedidos > 0 else 0

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card kpi-1">
        <div class="kpi-label">Volume de Pedidos</div>
        <div class="kpi-value">{f"{total_pedidos:,}".replace(',', '.')}</div>
    </div>
    <div class="kpi-card kpi-2">
        <div class="kpi-label">Faturamento Total Bruto</div>
        <div class="kpi-value">R$ {f"{faturamento_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')}</div>
    </div>
    <div class="kpi-card kpi-3">
        <div class="kpi-label">Ticket Médio por Pedido</div>
        <div class="kpi-value">R$ {f"{ticket_medio:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')}</div>
    </div>
    <div class="kpi-card kpi-4">
        <div class="kpi-label">Custo Total Logística</div>
        <div class="kpi-value">R$ {f"{frete_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════╗
# ║         PÁGINAS / VISUALIZAÇÕES          ║
# ╚══════════════════════════════════════════╝

# ─────────────────────────────────────
# 🏠 Visão Executiva
# ─────────────────────────────────────
if pagina == "🏠 Visão Executiva":
    col_a, col_b = st.columns(2)

    with col_a:
        if not df_filtrado.empty:
            st.markdown('<div class="section-title">🏆 Top Cidades em Faturamento</div>', unsafe_allow_html=True)
            cidades_receita = df_filtrado.groupby('customer_city')['total_valor_produtos'].sum().reset_index()
            cidades_receita = cidades_receita.sort_values(by='total_valor_produtos', ascending=False).head(10)

            fig_bar_h = px.bar(
                cidades_receita.sort_values("total_valor_produtos"),
                x="total_valor_produtos",
                y="customer_city",
                orientation="h",
                color="total_valor_produtos",
                color_continuous_scale="Purples",
                template=PLOTLY_TEMPLATE,
            )
            fig_bar_h.update_layout(coloraxis_showscale=False, xaxis_title="Receita Gerada (R$)", yaxis_title="")
            st.plotly_chart(fig_bar_h, width="stretch")

    with col_b:
        if not df_filtrado.empty:
            st.markdown('<div class="section-title">📊 Divisão de Status</div>', unsafe_allow_html=True)
            status_counts = df_filtrado["order_status"].value_counts().reset_index()
            status_counts.columns = ["status", "qtd"]

            tipo_grafico_status = st.selectbox(
                "Tipo de Gráfico",
                ["Donut", "Pizza", "Barras", "Funil", "Treemap"],
                label_visibility="collapsed"
            )

            if tipo_grafico_status == "Donut":
                fig_status = px.pie(status_counts, names="status", values="qtd", hole=0.4, color_discrete_sequence=COLORS, template=PLOTLY_TEMPLATE)
                fig_status.update_traces(textposition='inside', textinfo='percent+label')
            elif tipo_grafico_status == "Pizza":
                fig_status = px.pie(status_counts, names="status", values="qtd", hole=0, color_discrete_sequence=COLORS, template=PLOTLY_TEMPLATE)
                fig_status.update_traces(textposition='inside', textinfo='percent+label')
            elif tipo_grafico_status == "Barras":
                fig_status = px.bar(status_counts, x="status", y="qtd", color="status", color_discrete_sequence=COLORS, template=PLOTLY_TEMPLATE)
                fig_status.update_layout(xaxis_title="", yaxis_title="Quantidade")
            elif tipo_grafico_status == "Funil":
                fig_status = px.funnel(status_counts, x="qtd", y="status", color="status", color_discrete_sequence=COLORS, template=PLOTLY_TEMPLATE)
            elif tipo_grafico_status == "Treemap":
                fig_status = px.treemap(status_counts, path=["status"], values="qtd", template=PLOTLY_TEMPLATE, color="qtd", color_continuous_scale="Purples")
                
            st.plotly_chart(fig_status, width="stretch")

    # Gráfico Temporal Vendas vs Meses
    if not df_filtrado.empty and "order_purchase_timestamp" in df_filtrado.columns:
        st.markdown('<div class="section-title">📅 Crescimento do Volume de Faturamento Físico</div>', unsafe_allow_html=True)
        
        tipo_graf_tempo = st.radio("Como deseja visualizar a evolução temporal?", ["Área", "Linhas", "Colunas"], horizontal=True)

        df_temp = df_filtrado.dropna(subset=['order_purchase_timestamp']).copy()
        df_temp['Mes_Ano'] = df_temp['order_purchase_timestamp'].dt.to_period("M").astype(str)
        
        vendas_tempo = df_temp.groupby('Mes_Ano')['total_valor_produtos'].sum().reset_index()
        # Garante explicitamente a ordem natural do tempo (Esquerda para a Direita)
        vendas_tempo = vendas_tempo.sort_values('Mes_Ano')
        
        if tipo_graf_tempo == "Área":
            fig_area = px.area(vendas_tempo, x='Mes_Ano', y='total_valor_produtos', template=PLOTLY_TEMPLATE, color_discrete_sequence=["#4facfe"])
            fig_area.update_traces(line=dict(width=3, color='#4facfe'), fillcolor="rgba(79, 172, 254, 0.3)")
        elif tipo_graf_tempo == "Linhas":
            fig_area = px.line(vendas_tempo, x='Mes_Ano', y='total_valor_produtos', template=PLOTLY_TEMPLATE, color_discrete_sequence=["#43e97b"])
            fig_area.update_traces(line=dict(width=4, color='#43e97b'))
        elif tipo_graf_tempo == "Colunas":
            fig_area = px.bar(vendas_tempo, x='Mes_Ano', y='total_valor_produtos', template=PLOTLY_TEMPLATE, color_discrete_sequence=["#f5576c"])

        fig_area.update_layout(xaxis_title="", yaxis_title="Faturamento Agregado (R$)")
        st.plotly_chart(fig_area, width="stretch")


# ─────────────────────────────────────
# 📈 Análise de Produtos
# ─────────────────────────────────────
elif pagina == "📈 Análise de Produtos":
    st.markdown('<div class="section-title">🛒 Análise de Consumo (Categorias)</div>', unsafe_allow_html=True)

    if not df_filtrado.empty and "categorias_produtos" in df_filtrado.columns:
        cats = df_filtrado['categorias_produtos'].dropna().str.split(', ').explode()
        cat_counts = cats.value_counts().reset_index()
        cat_counts.columns = ['Categoria', 'Qtd_Vendida']
        
        col_grafico, col_metricas = st.columns([2.5, 1])
        
        with col_grafico:
            filtro_produtos = st.radio(
                "Filtro de Ranking:",
                options=["Todos os produtos", "Mais vendidos (10)", "Menos vendidos (10)"],
                horizontal=True
            )
            
            if filtro_produtos == "Mais vendidos (10)":
                df_render = cat_counts.head(10)
            elif filtro_produtos == "Menos vendidos (10)":
                df_render = cat_counts.tail(10)
            else:
                df_render = cat_counts
                
            fig_prod = px.bar(
                df_render.sort_values("Qtd_Vendida"), 
                x="Qtd_Vendida", 
                y="Categoria",
                orientation='h',
                template=PLOTLY_TEMPLATE,
                color="Qtd_Vendida",
                color_continuous_scale="Mint"
            )
            
            altura_grafico = max(400, len(df_render) * 30)
            fig_prod.update_layout(coloraxis_showscale=False, yaxis_title="", height=altura_grafico)
            
            st.plotly_chart(fig_prod, use_container_width=True)

        with col_metricas:
            import re
            categorias_presentes = df_render['Categoria'].tolist()
            
            if categorias_presentes:
                # Utilizamos regex simples para testar contensão em pelo menos 1 categoria do bloco
                regex_cat = '|'.join([re.escape(cat) for cat in categorias_presentes])
                df_kpi_cat = df_filtrado[df_filtrado['categorias_produtos'].str.contains(regex_cat, regex=True, na=False)]
            else:
                df_kpi_cat = pd.DataFrame()
            
            vol_itens = len(df_kpi_cat)
            fat_itens = df_kpi_cat["total_valor_produtos"].sum() if not df_kpi_cat.empty else 0
            frete_itens = df_kpi_cat["total_valor_frete"].sum() if not df_kpi_cat.empty else 0
            tm_itens = (fat_itens / vol_itens) if vol_itens > 0 else 0
            
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
                <div class="kpi-card kpi-1" style="min-height: 100px; padding: 1.5rem;">
                    <div class="kpi-label">Volume (Pedidos)</div>
                    <div class="kpi-value" style="font-size: 1.6rem;">{f"{vol_itens:,}".replace(',', '.')}</div>
                </div>
                <div class="kpi-card kpi-2" style="min-height: 100px; padding: 1.5rem;">
                    <div class="kpi-label">Faturamento</div>
                    <div class="kpi-value" style="font-size: 1.6rem;">R$ {f"{fat_itens:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')}</div>
                </div>
                <div class="kpi-card kpi-3" style="min-height: 100px; padding: 1.5rem;">
                    <div class="kpi-label">Ticket Médio</div>
                    <div class="kpi-value" style="font-size: 1.6rem;">R$ {f"{tm_itens:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')}</div>
                </div>
                <div class="kpi-card kpi-4" style="min-height: 100px; padding: 1.5rem;">
                    <div class="kpi-label">Custo Logística</div>
                    <div class="kpi-value" style="font-size: 1.6rem;">R$ {f"{frete_itens:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────
# 📍 Dispersão Geográfica
# ─────────────────────────────────────
elif pagina == "📍 Dispersão Geográfica":
    st.markdown('<div class="section-title">📍 Mapa de Calor Direto: Clusters de Vendas Olist</div>', unsafe_allow_html=True)
    
    map_df = df_filtrado.dropna(subset=["customer_lat", "customer_lng"])
    if map_df.empty:
        st.warning("Problema ao extrair a Geolocalização do SQL AVG JOIN do DB Master.")
    else:
        fig_map = px.scatter_map(
            map_df,
            lat="customer_lat",
            lon="customer_lng",
            zoom=3.5,
            height=650,
            map_style="carto-darkmatter",
            color="order_status",
            size="total_valor_produtos", 
            size_max=18,
            color_discrete_sequence=COLORS,
            hover_data=["customer_city", "total_valor_produtos", "customer_state"],
            template=PLOTLY_TEMPLATE,
        )
        fig_map.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_map, width="stretch")


# ─────────────────────────────────────
# 📋 Exportação de Dados (Nova GUI de Paginação e Rename)
# ─────────────────────────────────────
elif pagina == "📋 Exportação de Dados":
    st.markdown('<div class="section-title">📋 Snapshot Bruto e Extração Automática</div>', unsafe_allow_html=True)
    st.write("Acesso direto ao núcleo de dados consolidados. Configure seus limites para que não ocorra crash financeiro na memória.")

    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.write("### 📝 Renomeador Master (Dê duplo clique)")
        st.info("Para alterar os nomes das colunas que irão para o Excel/CSV, dê 2 cliques no novo nome antes de extrair.")
        
        # Traz as colunas dinamicamente
        colunas_atuais = list(df_filtrado.columns)
        df_colunas = pd.DataFrame({
            "Coluna Original (Tabela)": colunas_atuais,
            "Nome Final no CSV (Edite)": colunas_atuais
        })
        
        # O Segredo: st.data_editor() que permite edição das celulas livremente!
        df_editado_ui = st.data_editor(
            df_colunas,
            hide_index=True,
            disabled=["Coluna Original (Tabela)"], # Não deixa editar a da esquerda para n perder ref
            width="stretch",
            height=400
        )

    with col2:
        st.write("### 🚀 Engine de Extração Paginada")
        tamanho_lote_ui = st.number_input("Tamanho Máximo do Lote em MB/RAM (Linhas):", min_value=1000, max_value=500000, value=50000, step=10000)
        exportar_sql = st.toggle("Exportar no formato Banco de Dados (.sql)", value=False, help="Se ativo, converte para scripts INSERT automáticos.")
        
        if st.button("🔌 Ativar Pulling Paginado (Direto da DB)", type="primary", width="stretch"):
            import math
            import re
            
            # Buscando na raiz o SQL limpo
            caminho_sql = os.path.join(os.path.dirname(__file__), "db", "queries", "query_informacoes.sql")
            with open(caminho_sql, "r", encoding="utf-8") as f:
                query_bruta = f.read()
                
            query_limpa = re.sub(r'(?i)\s+LIMIT\s+\d+\s*$', '', query_bruta.strip())
            if query_limpa.endswith(';'): query_limpa = query_limpa[:-1]

            engine = get_engine()
            
            painel_alertas = st.empty()
            painel_alertas.info("Contando volume arquitetural da DB...")
            
            # Step 1: Count()
            query_count = f"SELECT COUNT(*) as total FROM (\n{query_limpa}\n) as db_temp;"
            total_linhas = pd.read_sql(query_count, con=engine).iloc[0,0]
            
            qtd_partes = math.ceil(total_linhas / tamanho_lote_ui)
            
            barra_progresso = st.progress(0)
            
            st.success(f"**Volume Oficial Detectado:** {total_linhas:,} linhas.")
            st.write(f"O Streamlit fragmentará e juntará a db em **{qtd_partes} lote(s)**.")
            
            # Step 2: Extracting (Assim como no bot.py)
            pedacos = []
            for i in range(qtd_partes):
                offset = i * tamanho_lote_ui
                painel_alertas.warning(f"Engajando Lote {i+1} de {qtd_partes}...")
                q_part = f"{query_limpa}\nLIMIT {tamanho_lote_ui} OFFSET {offset}"
                
                df_part = pd.read_sql(q_part, con=engine)
                pedacos.append(df_part)
                barra_progresso.progress((i + 1) / qtd_partes)
                
            painel_alertas.info("Montando DataFrame master em RAM e convertendo as colunas Editadas...")
            df_final_export = pd.concat(pedacos, ignore_index=True)
            
            # Aplica o truque da Interface para Renomear
            dicionario_renomeio = dict(zip(df_editado_ui["Coluna Original (Tabela)"], df_editado_ui["Nome Final no CSV (Edite)"]))
            df_final_export.rename(columns=dicionario_renomeio, inplace=True)
            
            # Converte e prepara o formato de saída
            painel_alertas.info("Preparando formato de saída do Dataframe final...")
            
            if exportar_sql:
                def escape_sql_it(val):
                    if pd.isna(val): return "NULL"
                    if isinstance(val, (int, float)): return str(val)
                    return "'" + str(val).replace("'", "''") + "'"

                columns_sql = ", ".join([f"`{c}`" for c in df_final_export.columns])
                sql_linhas = []
                for tupla in df_final_export.itertuples(index=False, name=None):
                    vals = ", ".join(escape_sql_it(x) for x in tupla)
                    sql_linhas.append(f"INSERT INTO tabela_exportada ({columns_sql}) VALUES ({vals});")
                    
                dados_prontos = "\\n".join(sql_linhas).encode('utf-8')
                tipo_mime = "application/sql"
                nome_arq = "extracao_paginada.sql"
                txt_botao = "✅ [CLIQUE AQUI] Download da Base Massiva (.sql Otimizado)"
            else:
                dados_prontos = df_final_export.to_csv(index=False).encode('utf-8')
                tipo_mime = "text/csv"
                nome_arq = "extracao_paginada.csv"
                txt_botao = "✅ [CLIQUE AQUI] Download da Base Massiva (.csv)"
            
            painel_alertas.empty()
            st.toast('Sua carga está pronta!', icon='😍')
            
            # Libera o Download Otimizado na tela
            st.download_button(
                label=txt_botao,
                data=dados_prontos,
                file_name=nome_arq,
                mime=tipo_mime,
                type="primary",
                width="stretch"
            )

# =========================
# FOOTER
# =========================
st.markdown("""
<div class="footer" style="margin-top: 50px; text-align: center; color: rgba(255,255,255,0.4); font-size: 0.8rem;">
    <p>Olist Analytics Master Console • Dados fornecidos diretamente da DB via Query Oficial Mapeada</p>
    <p>Desenvolvido por <strong>Alef Barbosa</strong></p>
</div>
""", unsafe_allow_html=True)