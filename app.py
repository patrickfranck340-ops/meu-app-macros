import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Macro Planner TACO", layout="centered")

# --- CARREGAR DADOS ---
@st.cache_data
def carregar_dados():
    # Lê o arquivo com separador ; 
    df = pd.read_csv('taco.csv', sep=';', encoding='utf-8')
    
    # Limpa nomes de colunas (remove espaços e quebras de linha)
    df.columns = df.columns.str.strip()
    
    # Mapeamento exato baseado na sua planilha
    df = df.rename(columns={
        'Nome do Alimento': 'nome',
        'Energia (kcal)': 'kcal',
        'Carboidrato (g)': 'carb',
        'Proteína (g)': 'prot',
        'Lipídeos (g)': 'gord'
    })
    
    # Função para limpar números (troca vírgula por ponto e remove textos)
    def limpar_valor(valor):
        if pd.isna(valor) or valor == "" or valor == "-":
            return 0.0
        try:
            # Transforma em string, troca , por . e remove caracteres não numéricos
            s = str(valor).replace(',', '.').strip()
            return float(s)
        except:
            return 0.0

    # Aplica a limpeza nas colunas de macros
    for col in ['kcal', 'carb', 'prot', 'gord']:
        if col in df.columns:
            df[col] = df[col].apply(limpar_valor)
            
    return df

try:
    taco = carregar_dados()
except Exception as e:
    st.error(f"Erro ao processar a planilha: {e}")
    st.stop()

# --- ESTADO DO APP ---
if 'diario' not in st.session_state:
    st.session_state['diario'] = []

st.title("🍎 Meu Diário de Macros")

# --- INTERFACE ---
aba1, aba2 = st.tabs(["🍽 Diário", "➕ Alimento Externo"])

with aba1:
    busca = st.text_input("Buscar na TACO (ex: Frango, Arroz...)")
    
    if busca:
        sugestoes = taco[taco['nome'].str.contains(busca, case=False, na=False)]
        if not sugestoes.empty:
            alimento_sel = st.selectbox("Selecione o item:", sugestoes['nome'].unique())
            
            c1, c2 = st.columns(2)
            gramas = c1.number_input("Quantidade (g)", min_value=1.0, value=100.0)
            hora = c2.time_input("Horário")

            if st.button("Adicionar ao Diário"):
                dados = taco[taco['nome'] == alimento_sel].iloc[0]
                fator = gramas / 100
                
                st.session_state['diario'].append({
                    "Hora": hora.strftime("%H:%M"),
                    "Alimento": alimento_sel,
                    "Qtd": f"{gramas}g",
                    "Kcal": float(dados['kcal']) * fator,
                    "Carb": float(dados['carb']) * fator,
                    "Prot": float(dados['prot']) * fator,
                    "Gord": float(dados['gord']) * fator
                })
                st.success("Adicionado!")
                st.rerun()

    st.divider()

    if st.session_state['diario']:
        df_hoje = pd.DataFrame(st.session_state['diario'])
        
        # Dashboard Minimalista
        cols = st.columns(4)
        metrics = [
            ("🔥 Kcal", "Kcal", ".0f"),
            ("🍞 Carb", "Carb", ".1f"),
            ("🍗 Prot", "Prot", ".1f"),
            ("🥑 Gord", "Gord", ".1f")
        ]
        
        for col, (label, key, fmt) in zip(cols, metrics):
            total = df_hoje[key].sum()
            col.metric(label, f"{total:{fmt}}")
        
        st.dataframe(df_hoje, use_container_width=True)
        
        if st.button("Limpar Tudo"):
            st.session_state['diario'] = []
            st.rerun()

with aba2:
    st.subheader("Cadastrar Manual")
    with st.form("manual"):
        n = st.text_input("Nome")
        c1, c2, c3, c4 = st.columns(4)
        kcal = c1.number_input("Kcal")
        carb = c2.number_input("Carb")
        prot = c3.number_input("Prot")
        gord = c4.number_input("Gord")
        if st.form_submit_button("Adicionar"):
            st.session_state['diario'].append({
                "Hora": datetime.now().strftime("%H:%M"),
                "Alimento": n, "Qtd": "Personalizado",
                "Kcal": kcal, "Carb": carb, "Prot": prot, "Gord": gord
            })
            st.rerun()
