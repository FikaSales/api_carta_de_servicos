import json
import requests
import pandas as pd
import streamlit as st
from os import path
import math
from datetime import datetime, timedelta


# URL da API
url = "https://servicos.ba.gov.br/api/servicos"

# Requisição GET (Timeout e Tratamento)
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    servicos = pd.DataFrame(response.json())
    # df['sigla'] = df['secretaria'].apply(lambda x: json.loads(x)['sigla'])
    
except requests.RequestException as e:
    st.error(f"Erro ao acessar a API: {e}")
    servicos = pd.DataFrame()

# Extrair 'sigla' da coluna 'secretaria' (se existir)
def extrair_sigla(x):
    if pd.isna(x):
        return None
    if isinstance(x, dict):
        return x.get("sigla")
    if isinstance(x, str):
        try:
            obj = json.loads(x)
            if isinstance(obj, dict):
                return obj.get("sigla")
        except Exception:
            # se não for JSON, tentar buscar padrão simples
            return None
    return None

if "secretaria" in servicos.columns:
    servicos["sigla"] = servicos["secretaria"].apply(extrair_sigla)
else:
    servicos["sigla"] = None

# Converter coluna de data somente se existir
coluna_data = "data_publicacao"
if coluna_data in servicos.columns:
    servicos[coluna_data] = pd.to_datetime(servicos[coluna_data], errors="coerce")

# Sidebar: filtros
st.sidebar.header("Filtros")
# Sigla
siglas = sorted([s for s in servicos["sigla"].dropna().unique()]) if "sigla" in servicos.columns else []
sigla_selecionada = st.sidebar.selectbox("Filtrar por sigla (secretaria)", options=["Todas"] + siglas)

# Últimos N dias (padrão 120)
dias_default = 120
usar_ultimos = st.sidebar.checkbox(f"Últimos {dias_default} dias (data_publicacao)", value=True)
dias_filtro = st.sidebar.number_input("Dias (se marcar acima)", min_value=1, value=dias_default)

# Filtro texto em coluna selecionada
cols_texto = servicos.select_dtypes(include=["object"]).columns.tolist()
col_filtro = st.sidebar.selectbox("Coluna para filtro de texto", options=["(nenhum)"] + cols_texto)
texto_filtro = st.sidebar.text_input("Texto (contains, case-insensitive)")

# Aplica filtros ao DataFrame
df_filtrado = servicos.copy()

if sigla_selecionada and sigla_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["sigla"] == sigla_selecionada]

if usar_ultimos and coluna_data in df_filtrado.columns:
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    data_limite = hoje - timedelta(days=int(dias_filtro))
    df_filtrado = df_filtrado[df_filtrado[coluna_data] >= data_limite]

if col_filtro != "(nenhum)" and texto_filtro:
    df_filtrado = df_filtrado[df_filtrado[col_filtro].astype(str).str.contains(texto_filtro, case=False, na=False)]

# Paginação
if "page" not in st.session_state:
    st.session_state.page = 0

st.title("Serviços A Revisar")
st.write("Esta aplicação extrai dados da API de serviços da Bahia e os exibe em uma tabela interativa.")

itens_page = 50
total_items = len(df_filtrado)
total_page = max(1, math.ceil(total_items / itens_page))

start = st.session_state.page * itens_page
end = start + itens_page

st.write(f"{total_items} itens — mostrando {start + 1} a {min(end, total_items)}")
st.dataframe(df_filtrado.iloc[start:end])

# Botões de Navegação
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Anterior"):
        if st.session_state.page > 0:
            st.session_state.page -= 1
            st.experimental_rerun()

with col2:
    st.markdown(f"<p> Página {st.session_state.page + 1} de {total_page} </p>", unsafe_allow_html=True)

with col3:
    if st.button("Próximo"):
        if st.session_state.page < total_page - 1:
            st.session_state.page += 1
            st.experimental_rerun()

# --- resumo por sigla nos últimos 120 dias ---
dias_120 = 120
if coluna_data in servicos.columns and not servicos.empty:
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    limite_120 = hoje - timedelta(days=dias_120)
    df_120 = servicos[servicos[coluna_data] >= limite_120].copy()
    if not df_120.empty:
        resumo = (
            df_120.groupby("sigla")
            .size()
            .reset_index(name="contagem")
            .sort_values("contagem", ascending=False)
        )
    else:
        resumo = pd.DataFrame(columns=["sigla", "contagem"])
else:
    df_120 = pd.DataFrame()
    resumo = pd.DataFrame(columns=["sigla", "contagem"])

st.subheader(f"Contagem por sigla nos últimos {dias_120} dias")
st.write(f"Registros no período: {len(df_120)}")
st.dataframe(resumo.reset_index(drop=True))