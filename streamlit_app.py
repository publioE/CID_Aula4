# Importando as bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Carregando os dados
dados = pd.read_excel('Vendas_Base_de_Dados.xlsx')
dados['Faturamento'] = dados['Quantidade'] * dados['Valor Unitário']


st.title("Dashboard de Vendas")
st.subheader("Mapa de calor de faturamento por estado:")

# Heatmap de faturamento por estado
nomes_para_siglas = {
    'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM',
    'Bahia': 'BA', 'Ceará': 'CE', 'Distrito Federal': 'DF', 'Espírito Santo': 'ES',
    'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT', 'Mato Grosso do Sul': 'MS',
    'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
    'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN',
    'Rio Grande do Sul': 'RS', 'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC',
    'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'
}

dados['Sigla'] = dados['Loja'].map(nomes_para_siglas)

faturamento_estados = (
    dados.groupby(['Sigla', 'Loja'])['Faturamento']
    .sum()
    .reset_index()
)

# Carregar o GeoJSON com os estados do Brasil
geojson_url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
geojson_data = requests.get(geojson_url).json()

# Criar o mapa
mapa = px.choropleth(
    faturamento_estados,
    geojson=geojson_data,
    featureidkey='properties.sigla',
    locations='Sigla',
    color='Faturamento',
    color_continuous_scale='YlOrRd',
    scope='south america',
    title='Faturamento por Estado',
    custom_data=[ 'Loja', 'Faturamento']
)

mapa.update_traces(
    hovertemplate='<b>%{customdata[0]}</b><br>Faturamento: R$ %{customdata[1]:,.2f}<extra></extra>'
)

# Ajustes do mapa
mapa.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(38,39,48,255)")
mapa.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    coloraxis_colorbar=dict(title='Faturamento (R$)'),
    height=600,
    width=800,
    paper_bgcolor="rgba(38,39,48,255)",
    plot_bgcolor="rgba(38,39,48,255)" 
)

# Exibir no Streamlit
st.plotly_chart(mapa, use_container_width=True)



st.title("Análise de Vendas por Loja e Produto:")
lojas = sorted(dados['Loja'].unique())
loja_escolhida = st.sidebar.selectbox('Escolha a loja:', lojas)

produtos_loja = dados[dados['Loja'] == loja_escolhida]['Produto'].unique()
produtos_opcoes = ['Todos'] + sorted(produtos_loja.tolist())
produtos_selecionados = st.sidebar.multiselect('Escolha os produtos:', options=produtos_opcoes, default=['Todos'])

if 'Todos' not in produtos_selecionados and produtos_selecionados:
    dados_loja = dados[(dados['Loja'] == loja_escolhida) & (dados['Produto'].isin(produtos_selecionados))]
else:
    dados_loja = dados[dados['Loja'] == loja_escolhida]
    
# Exibir os dados filtrados da loja escolhida
st.header(f'Loja: {loja_escolhida}')
st.subheader(f'Produtos selecionados: {", ".join(produtos_selecionados)}')
st.subheader(f'Faturamento Total: R$ {dados_loja["Faturamento"].sum():,.2f}')
st.dataframe(dados_loja)

# Grafico de torta
faturamento_produtos = (
    dados_loja.groupby('Produto')['Faturamento']
    .sum()
    .reset_index()
)
grafico_pizza = px.pie(
    faturamento_produtos,
    names='Produto',
    values='Faturamento',
    title=f'Participação dos Produtos no Faturamento da Loja {loja_escolhida}'
)
st.plotly_chart(grafico_pizza, use_container_width=True)