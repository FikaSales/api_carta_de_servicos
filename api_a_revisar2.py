import requests
import openpyxl
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
    
coluna_data = 'data_publicacao'
if coluna_data in servicos.columns:
    servicos[coluna_data] = pd.to_datetime(servicos[coluna_data], errors='coerce')

# Sidebar: filtros
st.sidebar.header("Filtros")
# Sigla
siglas = sorted([s for s in servicos["sigla"].dropna().unique()]) if "sigla" in servicos.columns else []
sigla_selecionada = st.sidebar.selectbox("Filtrar por sigla (secretaria)", options=["Todas"] + siglas)


# 2. Calcular a data que foi exatamente 120 dias atrás
dias_filtro = 120
data_hoje = datetime.now().normalize() # Normalize para ignorar a hora
data_limite = data_hoje - timedelta(days=dias_filtro)

df_filtrado = df[df[coluna_data] >= data_limite]

print(f"Data de hoje: {data_hoje.strftime('%Y-%m-%d')}")
print(f"Data Limite (120 dias atrás): {data_limite.strftime('%Y-%m-%d')}")


# Inicia o estado de Sessão para a pg
if 'page' not in st.session_state:
    st.session_state.page = 0

st.title("Serviços A Revisar")
st.write("Esta aplicação extrai dados da API de serviços da Bahia e os exibe em uma tabela interativa.")

# Paginação
itens_page = 50
total_items = len(servicos)
total_page = max(1, math.ceil(total_items / itens_page))

start = st.session_state.page * itens_page
end = start + itens_page
st.dataframe(servicos.iloc[start:end])

# São 13 Colunas Preenchidas e 18 no total.
# Botões de Navegação
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Anterior"):
        if st.session_state.page > 0:
            st.session_state.page -= 1
            st.rerurn()
            
with col2:
    st.markdown(f"<p> Página {st.session_state.page + 1} de {total_page} </p>", unsafe_allow_html=True)

with col3:
    if st.button("Próximo"):
        if st.session_state.page < total_page - 1:
            st.session_state.page += 1
            st.rerurn()