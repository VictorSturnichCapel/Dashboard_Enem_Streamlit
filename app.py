import streamlit as st
import pandas as pd
from google.oauth2 import service_account

st.title("Teste com Motor alternativo (Pandas-GBQ)")

# Função simplificada ao máximo
def get_data_alternative():
    info = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(info)
    project_id = info["project_id"]
    
    query = "SELECT * FROM `affable-envoy-482112-d9.business.fact_enem__infrastructure_impact` LIMIT 10"
    
    # O pandas-gbq gerencia a conexão de uma forma diferente do cliente padrão
    return pd.read_gbq(query, project_id=project_id, credentials=creds, dialect='standard')

if st.button("Tentar nova conexão"):
    with st.status("Conectando via Pandas-GBQ..."):
        try:
            df = get_data_alternative()
            st.success("Finalmente carregou!")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Erro no novo motor: {e}")