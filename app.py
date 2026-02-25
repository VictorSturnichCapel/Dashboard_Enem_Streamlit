import streamlit as st
import pandas as pd
from google.oauth2 import service_account

# 1. Configuração da Página
st.set_page_config(page_title="Diagnóstico Enem", layout="wide")

# 2. Função de Conexão com Cache (Evita múltiplas cobranças no BigQuery)
@st.cache_data
def load_data():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    
    query = "SELECT * FROM `affable-envoy-482112-d9.business.fact_enem__infrastructure_impact`"
    # O projeto de faturamento (billing) vem do seu JSON
    return pd.read_gbq(query, project_id=creds_dict["project_id"], credentials=credentials)

# Carregamento inicial
df_raw = load_data()

# 3. Sidebar - Filtros Dinâmicos
st.sidebar.header("Filtros")

anos = sorted(df_raw["exam_year"].unique(), reverse=True)
ano_sel = st.sidebar.multiselect("Ano", options=anos, default=anos[0])

estados = sorted(df_raw["school_state"].unique())
est_sel = st.sidebar.multiselect("Estado", options=estados)

# Filtro de cidade dinâmico (só mostra cidades dos estados selecionados)
if est_sel:
    cidades_ops = sorted(df_raw[df_raw["school_state"].isin(est_sel)]["school_city_name"].unique())
else:
    cidades_ops = sorted(df_raw["school_city_name"].unique())
cid_sel = st.sidebar.multiselect("Cidade", options=cidades_ops)

tipo_esc_ops = df_raw["school_type"].unique()
tipo_sel = st.sidebar.multiselect("Tipo da escola", options=tipo_esc_ops)

# Aplicação dos Filtros
df = df_raw[df_raw["exam_year"].isin(ano_sel)]
if est_sel:
    df = df[df["school_state"].isin(est_sel)]
if cid_sel:
    df = df[df["school_city_name"].isin(cid_sel)]
if tipo_sel:
    df = df[df["school_type"].isin(tipo_sel)]

# 4. Cabeçalho e KPIs
st.title("💡 Diagnóstico Enem")
st.subheader("KPIs de Resumo")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total de Estudantes", f"{df['total_students'].sum():,.0f}".replace(",", "."))
with c2:
    if not df.empty:
        top_escola = df.sort_values("school_general_average", ascending=False).iloc[0]["school_name"]
        st.metric("Escola Top 1", top_escola)
with c3:
    st.metric("Média Geral Seleção", f"{df['school_general_average'].mean():.2f}")

# 5. Visão de Performance
st.markdown("---")
st.subheader("📊 Visão de Performance")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Média CH", f"{df['avg_score_humanities'].mean():.2f}")
m2.metric("Média CN", f"{df['avg_score_natural_sciences'].mean():.2f}")
m3.metric("Média LC", f"{df['avg_score_languages'].mean():.2f}")
m4.metric("Média MT", f"{df['avg_score_math'].mean():.2f}")
m5.metric("Média Redação", f"{df['avg_score_essay'].mean():.2f}")

# 6. Ranking das Escolas (Novo!)
st.markdown("---")
st.subheader("🏆 Ranking de Escolas")

# Preparando dataframe de ranking
ranking_df = df[[
    'school_name', 'school_city_name', 'school_state', 
    'school_general_average', 'facility_score', 'tech_score'
]].sort_values("school_general_average", ascending=False).reset_index(drop=True)

# Exibindo tabela formatada
st.dataframe(
    ranking_df,
    column_config={
        "school_name": "Nome da Escola",
        "school_city_name": "Cidade",
        "school_state": "UF",
        "school_general_average": st.column_config.NumberColumn("Média Geral", format="%.2f"),
        "facility_score": st.column_config.ProgressColumn("Infraestrutura", min_value=0, max_value=100),
        "tech_score": st.column_config.ProgressColumn("Tecnologia", min_value=0, max_value=100),
    },
    use_container_width=True,
    hide_index=True
)

# 7. Gráfico de Correlação
st.subheader("📈 Correlação: Infraestrutura vs. Notas")
st.scatter_chart(
    data=df,
    x="facility_score",
    y="school_general_average",
    color="school_type"
)