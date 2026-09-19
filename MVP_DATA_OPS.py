import pandas as pd
import streamlit as st
import plotly.express as px

# CONFIG DA PÁGINA
st.set_page_config(
    page_title="Incidentes - Detecção de Padrões",
    layout="wide"
)


# CARREGAR DADOS
@st.cache_data
def load_data():
    df = pd.read_excel("LW-DATASET.xlsx")
    df['Aberto'] = pd.to_datetime(df['Aberto'])

    # Identificar Padrões de tempo
    df['hora'] = df['Aberto'].dt.hour

    # Mapeamento Dias em PT BR
    dias_pt = {
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    df['dia_semana'] = df['Aberto'].dt.day_name().map(dias_pt)

    # Ordenação dos dias da semana
    ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    df['dia_semana'] = pd.Categorical(df['dia_semana'], categories=ordem_dias, ordered=True)

    return df


df = load_data()

# SIDEBAR (FILTROS)
st.sidebar.header("Filtros")

# Filtro por Produto (Trata nulos para exibição)
produtos_disponiveis = df['Produto'].dropna().unique().tolist()
produtos_sel = st.sidebar.multiselect("Produto", options=produtos_disponiveis)

# Filtro por Equipe
times_disponiveis = df['Grupo designado'].unique().tolist()
times_sel = st.sidebar.multiselect("Equipe", options=times_disponiveis)

# Aplicação dos Filtros
df_filtered = df.copy()
if produtos_sel:
    df_filtered = df_filtered[df_filtered['Produto'].isin(produtos_sel)]
if times_sel:
    df_filtered = df_filtered[df_filtered['Grupo designado'].isin(times_sel)]

# TÍTULO E PROPÓSITO
st.title("Padrão de Incidentes Operacionais")
st.caption("MVP focado na identificação de padrões por horário, dia da semana, produtos e categorias.")

st.markdown("---")

# PAINEL 1: PADRÃO TEMPORAL (HEATMAP HORA X DIA DA SEMANA)
st.subheader("1. Janelas de Pico Operacional (Dia x Hora)")

# Agrupamento para o Heatmap
heatmap_data = df_filtered.groupby(['dia_semana', 'hora'], observed=False).size().reset_index(name='quantidade')

fig_heatmap = px.density_heatmap(
    heatmap_data,
    x='hora',
    y='dia_semana',
    z='quantidade',
    color_continuous_scale='Reds',
    title="Concentração de Incidentes por Hora e Dia da Semana",
    labels={'hora': 'Hora do Dia (0h-23h)', 'dia_semana': 'Dia da Semana', 'quantidade': 'Incidentes'},
    template="plotly_dark"
)
fig_heatmap.update_xaxes(dtick=1)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# PAINEL 2: PADRÃO DE ORIGEM (PRODUTOS X CATEGORIAS)
col1, col2 = st.columns(2)

with col1:
    st.subheader("2. Top 10 Produtos")
    top_produtos = df_filtered['Produto'].value_counts().head(10).reset_index()
    top_produtos.columns = ['Produto', 'Incidentes']

    fig_prod = px.bar(
        top_produtos,
        x='Incidentes',
        y='Produto',
        orientation='h',
        color='Incidentes',
        color_continuous_scale='Viridis',
        template="plotly_dark"
    )
    fig_prod.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_prod, use_container_width=True)

with col2:
    st.subheader("3. Top 10 Categorias")
    top_cat = df_filtered['Categoria'].value_counts().head(10).reset_index()
    top_cat.columns = ['Categoria', 'Incidentes']

    fig_cat = px.bar(
        top_cat,
        x='Incidentes',
        y='Categoria',
        orientation='h',
        color='Incidentes',
        color_continuous_scale='Cividis',
        template="plotly_dark"
    )
    fig_cat.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

# INSIGHTS AUTOMÁTICOS DO MVP
st.subheader("💡 Padrões Destacados")

if not df_filtered.empty:
    pico_hora = df_filtered['hora'].mode()[0]
    pico_dia = df_filtered['dia_semana'].mode()[0]
    prod_critico = df_filtered['Produto'].mode()[0] if not df_filtered['Produto'].dropna().empty else "N/A"
    cat_critica = df_filtered['Categoria'].mode()[0] if not df_filtered['Categoria'].dropna().empty else "N/A"

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Horário de Maior Risco", f"{pico_hora}:00h")
    col_b.metric("Dia Mais Crítico", f"{pico_dia}")
    col_c.metric("Par Crítico de Origem", f"{prod_critico} / {cat_critica}")