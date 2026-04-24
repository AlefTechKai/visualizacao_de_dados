# 📊 Dashboard de Visualização de Dados

> Dashboard interativo de análise de pedidos construído com **Streamlit** e **Plotly**, com sistema de temas dinâmicos, filtros avançados e múltiplas visualizações.

---

## 🖼️ Sobre o Projeto

Este projeto é um dashboard de exploração e visualização de dados de pedidos (e-commerce), permitindo análises visuais através de gráficos interativos, mapas geográficos e filtros dinâmicos.

### 📈 Exploração dos Dados

A análise dos dados revelou insights sobre o comportamento de pedidos:

- **Distribuição de Status**: A grande maioria dos pedidos possui status `delivered` (entregue), mostrando uma taxa de entrega consistente. Outros status como `shipped`, `canceled` e `processing` aparecem em menor proporção.
- **Padrões Temporais**: Os dados mostram variações sazonais no volume de pedidos ao longo dos meses, com picos identificáveis em determinados períodos — visíveis na granularidade mensal, semanal e diária.
- **Geolocalização**: O mapa de calor geográfico revela concentração de pedidos nas regiões Sudeste e Sul do Brasil, com São Paulo sendo o principal polo.
- **KPIs em Tempo Real**: O dashboard calcula automaticamente métricas como total de pedidos, status mais comum, quantidade de status únicos e taxa de entrega.

---

## 📸 Telas do Dashboard (Prints)

Aqui estão as demonstrações visuais das diversas funcionalidades do dashboard atualizado:

### 🏠 Visão Geral & Filtros
<p align="center">
  <img src="imagens/menu_lateral.png" width="30%" alt="Menu Lateral Premium"/>
  <img src="imagens/filtros_globais.png" width="30%" alt="Filtros Globais de Status e Ano"/>
  <br>
  <img src="imagens/menu_principal.png" width="80%" alt="Dashboard Visão Executiva e KPIs Modernos"/>
</p>

### 📊 Análise de Produtos e Rank
<p align="center">
  <img src="imagens/ranking_heatmap.png" width="80%" alt="Ranking de Vendas e Heatmap de Estados"/>
</p>

### 📈 Análise Temporal
<p align="center">
  <img src="imagens/faturamento_temporal.png" width="45%" alt="Evolução Temporal em Área"/>
  <img src="imagens/faturamento_temporal_colunas.png" width="45%" alt="Evolução Temporal em Colunas"/>
</p>

### 🗺️ Dispersão Geográfica
<p align="center">
  <img src="imagens/mapa_hotgeo.png" width="80%" alt="Mapa de Calor Olist (Carto-Darkmatter)"/>
</p>

### 📋 Exportação e Dados Brutos (.csv / .sql)
<p align="center">
  <img src="imagens/funcao_export.png" width="80%" alt="Engine de Extração Paginada e Toggle SQL/CSV"/>
</p>

---

## 🛠️ Bibliotecas Utilizadas

| Biblioteca | Versão | Finalidade |
|---|---|---|
| `streamlit` | 1.56+ | Framework do dashboard web |
| `pandas` | 3.0+ | Manipulação e análise de dados |
| `plotly` | 6.0+ | Gráficos interativos (barras, pizza, mapa, área, etc.) |
| `python-dotenv` | 1.2+ | Carregamento seguro de variáveis de ambiente (`.env`) |
| `psycopg2` | 2.9+ | Conexão com banco PostgreSQL |
| `PyMySQL` | 1.1+ | Conexão com banco MySQL |
| `requests` | 2.33+ | Requisições HTTP para APIs |

---

## 🐸 Método de Busca Anfíbio

O projeto utiliza um **sistema de busca anfíbio** — capaz de buscar dados de **múltiplas fontes** de forma flexível:

| Método | Status | Descrição |
|---|---|---|
| 📄 **CSV via API/URL** | ✅ Implementado | Lê dados de um arquivo CSV hospedado remotamente via URL |
| 🗄️ **SQL (PostgreSQL/MySQL)** | ✅ Implementado | Conexão direta com banco de dados relacional |
| 🔜 **REST API (JSON)** | 🚧 Planejado | Consumo de APIs REST que retornam JSON |
| 🔜 **Google Sheets** | 🚧 Planejado | Leitura de planilhas do Google como fonte de dados |
| 🔜 **Excel Local** | 🚧 Planejado | Upload e leitura de arquivos `.xlsx` locais |

> O sistema foi projetado para ser **extensível** — novos métodos de busca podem ser adicionados na pasta `funcoes/` seguindo o padrão existente.

---

## 📁 Estrutura do Projeto

```
visualizacao_de_dados/
├── app.py                          # Dashboard principal (Streamlit)
├── main.py                         # Script CLI para testes de conexão
├── .env                            # Variáveis de ambiente (NÃO versionado)
├── .gitignore                      # Regras de segurança do Git
├── requirements.txt                # Dependências do projeto
│
├── src/
│   └── css/
│       └── style.css               # CSS personalizado (layout, fontes, cores)
│
├── funcoes/
│   ├── __init__.py
│   └── api.py                      # Busca dados via CSV/URL (anfíbio)
│
├── db/
│   ├── __init__.py
│   ├── conexao_db.py               # Gerenciador de conexão com banco
│   └── teste_db.py                 # Testes de conexão com banco
│
└── venv/                           # Ambiente virtual (NÃO versionado)
```

### Separação de responsabilidades

- **`app.py`** — Interface visual do dashboard (Streamlit). Contém toda a lógica de renderização, filtros e gráficos.
- **`main.py`** — Script de linha de comando para testar conexões e fazer preview dos dados sem a interface visual.
- **`src/css/`** — CSS separado do Python para manutenção e organização.

---

---

## 🔒 Segurança com `.gitignore`

O arquivo `.gitignore` protege dados sensíveis de serem versionados acidentalmente:

```gitignore
venv/           # Ambiente virtual Python
__pycache__/    # Cache do Python
*.pyc           # Bytecode compilado
.env            # 🔐 Variáveis de ambiente (senhas, URLs, tokens)
```

> ⚠️ O arquivo `.env` contém credenciais de banco de dados e URLs de API. **Nunca** deve ser commitado no repositório.

---

## 🔐 Teste e Conexão com Banco de Dados

A conexão com o banco utiliza **variáveis de ambiente** via `.env` para segurança:

```env
API_URL=https://exemplo.com/dados.csv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=meu_banco
DB_USER=usuario
DB_PASSWORD=senha_segura
```

O script `main.py` permite testar a conexão antes de rodar o dashboard:

```bash
python main.py
```

---

## 🚀 Funcionalidades do Dashboard

| Funcionalidade | Descrição |
|---|---|
| 📊 **Visão Geral** | KPIs dinâmicos, ranking de cidades por faturamento e análise de status |
| 📦 **Visualização Dinâmica** | Alternância em tempo real entre gráficos de Barras, Pizza, Donut, Treemap e Funil |
| 📍 **Dispersão Geográfica** | Mapa de Calor de vendas utilizando as geolocalizações originais |
| 💡 **Insights Investigativos** | Avaliação analítica com cruzamento cruzado de KPIs diretos no MySQL (Recompra, NPS x Atraso, Cubagem vs Frete, Conversão por Imagens) |
| 📅 **Histórico Temporal** | Linha do tempo com opções de visualização (Área, Linhas ou Colunas) 100% cronológica |
| 📋 **Dados Brutos (Exportação)** | Painel massivo paginado com opção de renomear colunas dinamicamente |
| 🎛️ **Filtros Avançados** | Filtros globais por Status, Estado e filtro de Ano de análise |
| ⬇️ **Exportação Massiva** | Download otimizado e paginado para `.csv` ou scripts `.sql` gerados automaticamente |
| 🎨 **Design & UX** | Interface premium em português nativo (R$ e formato numérico) com *Glassmorphism*, gradientes vibrantes estilo moderno |

---

## 📦 Versionamento

O projeto utiliza **Git** para controle de versão, com repositório hospedado no **GitHub**.

```bash
# Clonar o repositório
git clone https://github.com/AlefTechKai/visualizacao_de_dados.git

# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
.\venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar o dashboard
streamlit run app.py
```

---

## 👨‍💻 Desenvolvido por

**Alef Barbosa** — com auxílio do Opus 4.6 (Thinking)

Feito com ❤️ e matplotly
