import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Dashboard dbt + BigQuery", layout="wide")

# Autenticação
def get_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials, project=credentials.project_id)

client = get_client()

# Query - Aqui você aponta para a tabela final que o dbt gerou
# Geralmente no esquema/dataset 'analytics' ou 'prod'
QUERY = """
    SELECT * FROM `affable-envoy-482112-d9.business.fact_enem__infrastructure_impact` 
    LIMIT 1000
"""

@st.cache_data(ttl=600) # Cache de 10 minutos para não gastar BQ à toa
def load_data(query):
    query_job = client.query(query)
    return query_job.to_dataframe()

st.title("📊 dbt Analytics Dashboard")

data = load_data(QUERY)

# Exibindo os dados
if st.checkbox("Mostrar dados brutos"):
    st.write(data)

# Exemplo de gráfico simples
st.subheader("Visualização de Exemplo")
col1, col2 = st.columns(2)

with col1:
    # Supondo que você tenha uma coluna 'categoria' e 'valor'
    st.bar_chart(data.set_index('alguma_coluna_de_tempo')['valor'])

with col2:
    st.metric("Total de Linhas", len(data))