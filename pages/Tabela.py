import streamlit as st
import requests
import pandas as pd
import time

# define o cache
@st.cache_data

# define formato do download
def converte_csv(df):
    return df.to_csv(index = False).encode('UTF-8')

# define mensagem de download
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = '✅')
    time.sleep(5)
    sucesso.empty()

# define o título da página
st.title('Dados Brutos')

# define local dos dados
url = 'https://labdados.com/produtos'

# carrega os dados
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())

# converte a data
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# colunas exibidas na tabela
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

# criando filtros laterais
st.sidebar.title('Filtros')

with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0, 5000))

with st.sidebar.expander('Frete da venda'):
    frete = st.slider('Frete', 0, 250, (0, 250))

with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())

with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação da compra', 1, 5, value = (1, 5))

with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1, 24))

# conectando os filtros aos dados
query = '''
    Produto in @produtos and \
    `Categoria do Produto` in @categoria and \
    @preco[0] <= Preço <= @preco[1] and \
    @frete[0] <= Frete <= @frete[1] and \
    @data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
    Vendedor in @vendedores and \
    `Local da compra` in @local_compra and \
    @avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
    `Tipo de pagamento` in @tipo_pagamento and \
    @qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''

# filtrando os dados
dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

# exibindo os dados
st.dataframe(dados_filtrados)

# informações sobre a tabela
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

# download da tabela
st.markdown('Escreva um nome para o arquivo')

coluna1, coluna2 = st.columns(2)

# nome do arquivo
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'

# botão de download
with coluna2:
    st.download_button('Fazer o download da tabela em csv', 
        data = converte_csv(dados_filtrados), 
        file_name = nome_arquivo, 
        mime = 'text/csv', 
        on_click = mensagem_sucesso)
