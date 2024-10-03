# importa as bibliotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# define o layout da página
st.set_page_config(layout = 'wide')

# formata valores numéricos
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# define o título da página
st.title('Painel de Vendas :shopping_trolley:')

# define local dos dados
url = 'https://labdados.com/produtos'

# filtro de região
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

# filtro de período
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = { 'regiao': regiao.lower(), 'ano': ano }

# carrega os dados
response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())

# filtro de vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# converte a data
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# receita por estado
receita_estados = pd.DataFrame(dados.groupby('Local da compra')[['Preço']].sum())

receita_estados = dados\
    .drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']]\
    .merge(receita_estados, left_on = 'Local da compra', right_index = True)\
    .sort_values('Preço', ascending = False)

# receita por ano/mês
receita_mensal = dados.set_index('Data da Compra')\
    .groupby(pd.Grouper(freq = 'ME'))['Preço'].sum().reset_index()

receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.strftime('%b')

# receita por produto
receita_categorias = dados\
    .groupby('Categoria do Produto')[['Preço']].sum()\
    .sort_values('Preço', ascending = True)

# vendas por estado
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')[['Preço']].count())

vendas_estados = dados\
    .drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']]\
    .merge(vendas_estados, left_on = 'Local da compra', right_index = True)\
    .sort_values('Preço', ascending = False)

# vendas por ano/mês
vendas_mensal = dados.set_index('Data da Compra')\
    .groupby(pd.Grouper(freq = 'ME'))['Preço'].count().reset_index()

vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.strftime('%b')

# vendas por produto
vendas_categorias = dados\
    .groupby('Categoria do Produto')['Preço'].count()\
    .sort_values(ascending = True)

# valores por vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# define a estrutura do dashboard
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

## receita
with aba1:
    coluna1, coluna2 = st.columns(2)

    with coluna1:
        # gráfico de mapa por estado
        fig_mapa_receita = px.scatter_geo(receita_estados,
            lat = 'lat',
            lon = 'lon',
            scope = 'south america',
            size = 'Preço',
            template = 'seaborn',
            hover_name = 'Local da compra',
            hover_data = {'lat': False, 'lon': False},
            title = 'Receita por Estado')
        
        # gráfico de colunas por estado
        fig_receita_estados = px.bar(receita_estados.head(),
            x = 'Local da compra',
            y = 'Preço',
            text_auto = True,
            title = 'Top estados (receita)')
        fig_receita_estados.update_layout(yaxis_title = 'Receita')
        
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)

    with coluna2:
        # gráfico de linha por ano/mês
        fig_receita_mensal = px.line(receita_mensal,
            x = 'Mês',
            y = 'Preço',
            markers = True,
            range_y = (0, receita_mensal.max()),
            color = 'Ano',
            line_dash = 'Ano',
            title = 'Receita mensal')
        fig_receita_mensal.update_layout(yaxis_title = 'Receita')
        
        # gráfico de barras por produto
        fig_receita_categorias = px.bar(receita_categorias,
            text_auto = True,
            orientation = 'h',
            title = 'Receita por categoria')
        fig_receita_categorias.update_layout(xaxis_title = 'Receita', showlegend = False, xaxis = dict(showticklabels = False))

        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

## vendas
with aba2:
    coluna1, coluna2 = st.columns(2)

    with coluna1:
        # gráfico de mapa por estado
        fig_mapa_vendas = px.scatter_geo(vendas_estados, 
            lat = 'lat', 
            lon = 'lon', 
            scope = 'south america', 
            #fitbounds = 'locations', 
            size = 'Preço', 
            template = 'seaborn', 
            hover_name = 'Local da compra', 
            hover_data = {'lat': False, 'lon': False},
            title = 'Vendas por estado')
        
        # gráfico de colunas por estado
        fig_vendas_estados = px.bar(vendas_estados.head(),
            x = 'Local da compra',
            y = 'Preço',
            text_auto = True,
            title = 'Top 5 estados')
        fig_vendas_estados.update_layout(yaxis_title = 'Quantidade de vendas')
        
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)

    with coluna2:
        # gráfico de linha por ano/mês
        fig_vendas_mensal = px.line(vendas_mensal, 
            x = 'Mês',
            y = 'Preço',
            markers = True, 
            range_y = (0, vendas_mensal.max()), 
            color = 'Ano', 
            line_dash = 'Ano',
            title = 'Quantidade de vendas mensal')
        fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de vendas')

        # gráfico de barras por produto
        fig_vendas_categorias = px.bar(vendas_categorias, 
            text_auto = True,
            orientation = 'h',
            title = 'Vendas por categoria')
        fig_vendas_categorias.update_layout(xaxis_title = 'Quantidade de vendas', showlegend = False, xaxis = dict(showticklabels = False))

        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)

## vendedores
with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)

    coluna1, coluna2 = st.columns(2)

    with coluna1:
        # gráfico de barras: receita por vendedores
        fig_receita_vendedores = px.bar(
            vendedores[['sum']].sort_values('sum', ascending = True).head(qtd_vendedores),
            x = 'sum',
            y = vendedores[['sum']].sort_values(['sum'], ascending = False).head(qtd_vendedores).index,
            text_auto = True,
            title = f'Top {qtd_vendedores} vendedores (receita)')
        fig_receita_vendedores.update_layout(yaxis_title = 'Receita')
        
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_receita_vendedores)

    with coluna2:
        # gráfico de barras: vendas por vendedores
        fig_vendas_vendedores = px.bar(
            vendedores[['count']].sort_values('count', ascending = True).head(qtd_vendedores),
            x = 'count',
            y = vendedores[['count']].sort_values(['count'], ascending = False).head(qtd_vendedores).index,
            text_auto = True,
            title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        fig_vendas_vendedores.update_layout(yaxis_title = 'Quantidade')
        
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_vendedores)