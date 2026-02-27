# 📊 Dashboard Interativo - Microdados ENEM

Este projeto é uma aplicação interativa desenvolvida com **Streamlit** para visualização e análise dos microdados do Exame Nacional do Ensino Médio (ENEM). O objetivo é facilitar a exploração de tendências educacionais, perfis socioeconômicos e desempenho dos candidatos através de uma interface intuitiva.

## 🚀 Funcionalidades

- **Análise de Desempenho:** Visualização das médias por competências (Matemática, Linguagens, Ciências Humanas, Ciências da Natureza e Redação).
- **Perfil Socioeconômico:** Filtros por renda familiar, escolaridade dos pais e tipo de escola (Pública vs. Privada).
- **Distribuição Geográfica:** Gráficos comparativos entre diferentes estados (UF) e regiões.
- **Filtros Dinâmicos:** Explore os dados selecionando variáveis específicas para gerar insights em tempo real.

## 🛠️ Tecnologias Utilizadas

* **Python:** Linguagem base para processamento de dados.
* **Streamlit:** Framework para a criação da interface web.
* **Pandas:** Biblioteca essencial para manipulação e limpeza de dados.
* **Plotly/Matplotlib:** Bibliotecas para geração de gráficos interativos e estáticos.

## 📂 Estrutura do Projeto

```text
├── app.py             # Arquivo principal para execução do Streamlit
├── requirements.txt   # Lista de dependências do Python
└── README.md          # Documentação do projeto
```

## 🔧 Como Executar Localmente

Siga os passos abaixo para configurar o ambiente e rodar o dashboard em sua máquina.

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.8 ou superior** instalado. Você pode verificar a versão instalada rodando:
```bash
python --version
```

### 2. Clonar o Repositório
Abra o terminal e execute o comando abaixo para baixar o projeto:

```Bash
git clone [https://github.com/VictorSturnichCapel/Dashboard_Enem_Streamlit.git](https://github.com/VictorSturnichCapel/Dashboard_Enem_Streamlit.git)
cd Dashboard_Enem_Streamlit
```

### 3. Configurar Ambiente Virtual (Recomendado)
Para manter as dependências organizadas, crie e ative um ambiente virtual:

Windows:

```Bash
python -m venv venv
.\venv\Scripts\activate
```

Linux/Mac:

```Bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependências
Instale todas as bibliotecas necessárias listadas no arquivo requirements.txt:

```Bash
uv sync
```

### 5. Executar a Aplicação
Com tudo configurado, inicie o servidor do Streamlit:

```Bash
streamlit run app.py
```

Após o comando, o dashboard será aberto automaticamente no seu navegador padrão (geralmente no endereço http://localhost:8501).

### 📊 Base de Dados
O projeto utiliza os Microdados do ENEM disponibilizados pelo INEP.

Nota: Devido ao grande volume de dados originais, recomenda-se trabalhar com amostras em formato .csv ou arquivos compactados .parquet para garantir a fluidez da navegação no Streamlit.
