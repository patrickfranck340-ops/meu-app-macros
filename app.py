import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Macro Planner TACO", layout="centered")

# --- CARREGAR DADOS ---
@st.cache_data
def carregar_dados():
    # Lê o arquivo que você subiu no GitHub
    df = pd.read_csv('taco.csv')
    # Garante que os nomes das colunas estejam limpos
    df.columns = df.columns.str.lower()
    return df

try:
    taco = carregar_dados()
except:
    st.error("Erro ao ler taco.csv. Verifique se o arquivo tem as colunas: nome, kcal, carb, prot, gord")
    st.stop()

# --- ESTADO DO APP ---
if 'diario' not in st.session_state:
    st.session_state['diario'] = []

st.title("🍎 Diário de Macros (TACO)")

# --- ABA DE ADIÇÃO ---
with st.expander("➕ Adicionar Alimento da TACO", expanded=True):
    # Busca por texto na tabela
    busca = st.text_input("Buscar alimento (ex: Arroz, Frango...)")
    
    if busca:
        sugestoes = taco[taco['nome'].str.contains(busca, case=False, na=False)]
        alimento_sel = st.selectbox("Selecione o item exato:", sugestoes['nome'])
        
        col1, col2 = st.columns(2)
        gramas = col1.number_input("Quantidade (g)", min_value=1, value=100)
        hora = col2.time_input("Horário")

        if st.button("Adicionar ao Diário"):
            dados_item = taco[taco['nome'] == alimento_sel].iloc[0]
            fator = gramas / 100
            
            st.session_state['diario'].append({
                "Hora": hora.strftime("%H:%M"),
                "Alimento": alimento_sel,
                "Qtd": gramas,
                "Kcal": dados_item['kcal'] * fator,
                "Carb": dados_item['carb'] * fator,
                "Prot": dados_item['prot'] * fator,
                "Gord": dados_item['gord'] * fator
            })
            st.success("Adicionado com sucesso!")

# --- EXIBIÇÃO ---
if st.session_state['diario']:
    df_hoje = pd.DataFrame(st.session_state['diario'])
    
    # Métricas de resumo
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kcal", f"{df_hoje['Kcal'].sum():.0f}")
    c2.metric("Carb", f"{df_hoje['Carb'].sum():.1f}g")
    c3.metric("Prot", f"{df_hoje['Prot'].sum():.1f}g")
    c4.metric("Gord", f"{df_hoje['Gord'].sum():.1f}g")
    
    st.divider()
    st.dataframe(df_hoje, use_container_width=True)
    
    if st.button("Limpar Diário"):
        st.session_state['diario'] = []
        st.rerun()
else:
    st.info("Sua lista de hoje está vazia.")
