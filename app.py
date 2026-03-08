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

# Filtro de escola dinâmico (só mostra escolas dos filtros selecionados)
df_temp = df_raw[df_raw["exam_year"].isin(ano_sel)]
if est_sel:
    df_temp = df_temp[df_temp["school_state"].isin(est_sel)]
if cid_sel:
    df_temp = df_temp[df_temp["school_city_name"].isin(cid_sel)]
if tipo_sel:
    df_temp = df_temp[df_temp["school_type"].isin(tipo_sel)]
escolas_ops = sorted(df_temp["school_name"].unique())
esc_sel = st.sidebar.multiselect("Escola", options=escolas_ops)

# Aplicação dos Filtros
df = df_raw[df_raw["exam_year"].isin(ano_sel)]
if est_sel:
    df = df[df["school_state"].isin(est_sel)]
if cid_sel:
    df = df[df["school_city_name"].isin(cid_sel)]
if tipo_sel:
    df = df[df["school_type"].isin(tipo_sel)]
if esc_sel:
    df = df[df["school_name"].isin(esc_sel)]

# 4. Cabeçalho e KPIs
st.title("💡 Diagnóstico Enem")
st.subheader("KPIs de Resumo")

c1, c2, c3 = st.columns([1, 2, 1])
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

# 6. Ranking das Escolas com Ranks
st.markdown("---")
st.subheader("🏆 Ranking de Escolas")

# Preparando dataframe de ranking com informações completas
ranking_df = df[[
    'school_name', 'school_city_name', 'school_state', 'school_type',
    'school_general_average', 'general_rank', 'general_state_rank', 
    'general_city_rank', 'general_type_rank',
    'facility_score', 'tech_score', 'total_students'
]].sort_values("school_general_average", ascending=False).reset_index(drop=True)

# Exibindo tabela formatada com ranks
st.dataframe(
    ranking_df,
    column_config={
        "school_name": "Nome da Escola",
        "school_city_name": "Cidade",
        "school_state": "UF",
        "school_type": "Tipo",
        "school_general_average": st.column_config.NumberColumn("Média Geral", format="%.2f"),
        "general_rank": st.column_config.NumberColumn("Rank Global", format="%d"),
        "general_state_rank": st.column_config.NumberColumn("Rank Estado", format="%d"),
        "general_city_rank": st.column_config.NumberColumn("Rank Cidade", format="%d"),
        "general_type_rank": st.column_config.NumberColumn("Rank Tipo", format="%d"),
        "facility_score": st.column_config.ProgressColumn("Infraestrutura", min_value=0, max_value=3, format=""),
        "tech_score": st.column_config.ProgressColumn("Tecnologia", min_value=0, max_value=3, format=""),
        "total_students": st.column_config.NumberColumn("Estudantes", format="%d"),
    },
    use_container_width=True,
    hide_index=True
)

# 6.1 - Análise por Estado
st.markdown("---")
st.subheader("📍 Análise Comparativa por Estado")

# Estatísticas por estado
state_analysis = df.groupby("school_state").agg({
    "school_name": "count",
    "school_general_average": ["mean", "std"],
    "total_students": "sum",
    "facility_score": "mean",
    "tech_score": "mean",
    "general_state_rank": "mean"
}).round(2)

state_analysis.columns = ["Escolas", "Média Geral", "Desvio Padrão", "Total Estudantes", "Infraestrutura Média", "Tecnologia Média", "Rank Médio"]
state_analysis.index.name = "Estado"
state_analysis = state_analysis.sort_values("Média Geral", ascending=False)

st.dataframe(
    state_analysis,
    column_config={
        "Escolas": st.column_config.NumberColumn("Escolas", format="%d"),
        "Média Geral": st.column_config.NumberColumn("Média Geral", format="%.2f"),
        "Desvio Padrão": st.column_config.NumberColumn("Desvio Padrão", format="%.2f"),
        "Total Estudantes": st.column_config.NumberColumn("Total Estudantes", format="%d"),
        "Infraestrutura Média": st.column_config.NumberColumn("Infraestrutura Média", format="%.2f"),
        "Tecnologia Média": st.column_config.NumberColumn("Tecnologia Média", format="%.2f"),
        "Rank Médio": st.column_config.NumberColumn("Rank Médio", format="%.0f"),
    },
    use_container_width=True
)

# 6.2 - Análise por Cidade (Top por Estado)
st.markdown("---")
st.subheader("🏙️ Top Cidades por Estado")

# Seletor de estado para análise de cidades
states_available = sorted(df["school_state"].unique())
selected_state = st.selectbox("Selecione Estado", options=states_available, key="state_selector")

if selected_state:
    city_analysis = df[df["school_state"] == selected_state].groupby("school_city_name").agg({
        "school_name": "count",
        "school_general_average": "mean",
        "total_students": "sum",
        "facility_score": "mean",
        "tech_score": "mean",
    }).round(2)
    
    city_analysis.columns = ["Escolas", "Média Geral", "Total Estudantes", "Infraestrutura Média", "Tecnologia Média"]
    city_analysis.index.name = "Cidade"
    city_analysis = city_analysis.sort_values("Média Geral", ascending=False)
    
    st.dataframe(
        city_analysis,
        column_config={
            "Escolas": st.column_config.NumberColumn("Escolas", format="%d"),
            "Média Geral": st.column_config.NumberColumn("Média Geral", format="%.2f"),
            "Total Estudantes": st.column_config.NumberColumn("Total Estudantes", format="%d"),
            "Infraestrutura Média": st.column_config.NumberColumn("Infraestrutura Média", format="%.2f"),
            "Tecnologia Média": st.column_config.NumberColumn("Tecnologia Média", format="%.2f"),
        },
        use_container_width=True
    )

# 6.3 - Análise Comparativa: Público vs Privado
st.markdown("---")
st.subheader("🔄 Comparativo: Rede Pública vs Privada")

if len(df["school_type"].unique()) > 1:
    # Comparativo geral
    type_comparison = df.groupby("school_type").agg({
        "school_name": "count",
        "school_general_average": ["mean", "std"],
        "total_students": ["count", "sum"],
        "avg_score_math": "mean",
        "avg_score_languages": "mean",
        "avg_score_humanities": "mean",
        "avg_score_natural_sciences": "mean",
        "avg_score_essay": "mean",
        "facility_score": ["mean", "std"],
        "tech_score": ["mean", "std"],
        "students_per_classroom": "mean",
        "score_per_device_ratio": "mean",
    }).round(2)
    
    # Simplificando nomes
    type_comparison.columns = [
        "Escolas", "Média Geral", "Desvio Padrão", 
        "Qtd Escolas", "Total Estudantes",
        "Média Matemática", "Média Linguagens", "Média Humanas", "Média Naturais", "Média Redação",
        "Infraestrutura Média", "Infraestrutura D.P.",
        "Tecnologia Média", "Tecnologia D.P.",
        "Alunos por Sala", "Scores por Device"
    ]
    type_comparison.index.name = "Tipo da Escola"
    
    st.dataframe(
        type_comparison,
        use_container_width=True
    )
    
    # Discrepâncias calculadas
    if df["school_type"].nunique() == 2:
        st.subheader("📊 Discrepâncias Identificadas")
        
        types = sorted(df["school_type"].unique())
        type1_data = df[df["school_type"] == types[0]]
        type2_data = df[df["school_type"] == types[1]]
        
        discrepancias = {
            "Métrica": [],
            types[0]: [],
            types[1]: [],
            "Diferença": [],
            "Diferença %": []
        }
        
        metricas = {
            "Média Geral": "school_general_average",
            "Matemática": "avg_score_math",
            "Linguagens": "avg_score_languages",
            "Humanas": "avg_score_humanities",
            "Naturais": "avg_score_natural_sciences",
            "Redação": "avg_score_essay",
            "Infraestrutura": "facility_score",
            "Tecnologia": "tech_score",
            "Alunos/Sala": "students_per_classroom",
        }
        
        for metrica, coluna in metricas.items():
            val1 = type1_data[coluna].mean()
            val2 = type2_data[coluna].mean()
            diff = val2 - val1
            diff_pct = (diff / val1 * 100) if val1 != 0 else 0
            
            discrepancias["Métrica"].append(metrica)
            discrepancias[types[0]].append(f"{val1:.2f}")
            discrepancias[types[1]].append(f"{val2:.2f}")
            discrepancias["Diferença"].append(f"{diff:+.2f}")
            discrepancias["Diferença %"].append(f"{diff_pct:+.1f}%")
        
        disc_df = pd.DataFrame(discrepancias)
        st.dataframe(disc_df, use_container_width=True, hide_index=True)
else:
    st.info("❌ Apenas um tipo de escola nos filtros selecionados")

# Preparar dados para o gráfico de correlação com colunas em português
chart_data = df[['facility_score', 'school_general_average', 'school_type']].copy()
chart_data.columns = ['Infraestrutura', 'Média Geral', 'Tipo da Escola']

st.subheader("📈 Correlação: Infraestrutura vs. Notas")
st.scatter_chart(
    data=chart_data,
    x="Infraestrutura",
    y="Média Geral",
    color="Tipo da Escola"
)

# 7. Análises Adicionais
st.markdown("---")
st.subheader("📋 Análises Adicionais de Performance")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Notas por Disciplina (Média Geral)")
    disciplines = {
        "Matemática": df["avg_score_math"].mean(),
        "Linguagens": df["avg_score_languages"].mean(),
        "Humanas": df["avg_score_humanities"].mean(),
        "Naturais": df["avg_score_natural_sciences"].mean(),
        "Redação": df["avg_score_essay"].mean(),
    }
    disciplines_df = pd.DataFrame(list(disciplines.items()), columns=["Disciplina", "Nota"])
    st.bar_chart(data=disciplines_df.set_index("Disciplina"), use_container_width=True)

with col2:
    st.subheader("Índices Infraestruturais (Média Geral)")
    infra = {
        "Infraestrutura": df["facility_score"].mean(),
        "Tecnologia": df["tech_score"].mean(),
    }
    infra_df = pd.DataFrame(list(infra.items()), columns=["Índice", "Score"])
    st.bar_chart(data=infra_df.set_index("Índice"), use_container_width=True)

# 7.1 - Tabela detalhada de Ranks por tipo de escola
st.markdown("---")
st.subheader("🎯 Análise Detalhada: Ranks por Tipo de Escola")

rank_by_type = df[[
    'school_name', 'school_type', 'school_state', 'school_city_name',
    'school_general_average', 'general_rank', 'general_type_rank', 
    'general_type_state_rank', 'general_type_city_rank',
    'facility_score', 'tech_score'
]].sort_values("school_general_average", ascending=False).reset_index(drop=True)

st.dataframe(
    rank_by_type,
    column_config={
        "school_name": "Nome da Escola",
        "school_type": "Tipo",
        "school_state": "UF",
        "school_city_name": "Cidade",
        "school_general_average": st.column_config.NumberColumn("Média Geral", format="%.2f"),
        "general_rank": st.column_config.NumberColumn("Rank Global", format="%d"),
        "general_type_rank": st.column_config.NumberColumn("Rank Tipo", format="%d"),
        "general_type_state_rank": st.column_config.NumberColumn("Rank Tipo/Estado", format="%d"),
        "general_type_city_rank": st.column_config.NumberColumn("Rank Tipo/Cidade", format="%d"),
        "facility_score": st.column_config.ProgressColumn("Infraestrutura", min_value=0, max_value=3, format=""),
        "tech_score": st.column_config.ProgressColumn("Tecnologia", min_value=0, max_value=3, format=""),
    },
    use_container_width=True,
    hide_index=True
)
