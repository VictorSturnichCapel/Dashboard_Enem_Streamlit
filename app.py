import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery

st.title("Diagnóstico de Conexão")

# 1. Tenta autenticar
try:
    credentials_info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    st.success("Autenticação OK!")
except Exception as e:
    st.error(f"Erro na Autenticação: {e}")
    st.stop()

# 2. Tenta a Query mais simples possível
if st.button("Executar Teste de Query"):
    try:
        query_job = client.query("SELECT 'Sucesso!' as resultado")
        df = query_job.to_dataframe()
        st.write(df)
    except Exception as e:
        st.error(f"Erro na Query: {e}")