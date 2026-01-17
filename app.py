import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Macro Planner TACO", layout="centered")

@st.cache_data
def carregar_dados():
    # Carrega o CSV e ignora nomes de colunas problemáticos na leitura inicial
    df = pd.read_csv('taco.csv', sep=';', encoding='utf-8', skipinitialspace=True)
    
    # Forçamos a renomeação baseada na POSIÇÃO das colunas para evitar o KeyError
    # Coluna 0 = Nome, Coluna 2 = Energia, Coluna 3 = Proteína, Coluna 4 = Lipídeos, Coluna 5 = Carboidrato
    novas_colunas = {
        df.columns[0]: 'nome',
        df.columns[2]: 'kcal',
        df.columns[3]: 'prot',
        df.columns[4]: 'gord',
        df.columns[5]: 'carb'
    }
    df = df.rename(columns=novas_colunas)
    
    # Função para limpar os números (vírgula para ponto)
    def limpar(v):
        if pd.isna(v) or str(v).strip() in ["", "-", "tr"]: return 0.0
        try:
            return float(str(v).replace(',', '.'))
        except:
            return 0.0

    for c in ['kcal', 'prot', 'gord', 'carb']:
        df[c] = df[c].apply(limpar)
        
    return df[['nome', 'kcal', 'prot', 'gord', 'carb']]

try:
    taco = carregar_dados()
except Exception as e:
    st.error(f"Erro ao ler as colunas. Verifique se o CSV está correto: {e}")
    st.stop()

# --- INTERFACE ---
if 'diario' not in st.session_state:
    st.session_state['diario'] = []

st.title("🥗 Meu Diário de Macros")

aba1, aba2 = st.tabs(["🍽 Diário", "➕ Manual"])

with aba1:
    busca = st.text_input("Buscar Alimento (ex: Arroz, Ovo...)")
    
    if busca:
        # Filtra alimentos que contenham o que foi digitado
        filtro = taco[taco['nome'].str.contains(busca, case=False, na=False)]
        
        if not filtro.empty:
            item_nome = st.selectbox("Selecione:", filtro['nome'].unique())
            c1, c2 = st.columns(2)
            qtd = c1.number_input("Gramas (g)", min_value=1.0, value=100.0)
            hr = c2.time_input("Hora", datetime.now())
            
            if st.button("Adicionar"):
                row = taco[taco['nome'] == item_nome].iloc[0]
                mult = qtd / 100
                st.session_state['diario'].append({
                    "Hora": hr.strftime("%H:%M"),
                    "Alimento": item_nome,
                    "Kcal": row['kcal'] * mult,
                    "Carb": row['carb'] * mult,
                    "Prot": row['prot'] * mult,
                    "Gord": row['gord'] * mult
                })
                st.rerun()

    st.divider()

    if st.session_state['diario']:
        df_d = pd.DataFrame(st.session_state['diario'])
        
        # Dashboard de Totais
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🔥 Kcal", f"{df_d['Kcal'].sum():.0f}")
        m2.metric("🍞 Carb", f"{df_d['Carb'].sum():.1f}g")
        m3.metric("🍗 Prot", f"{df_d['Prot'].sum():.1f}g")
        m4.metric("🥑 Gord", f"{df_d['Gord'].sum():.1f}g")
        
        st.dataframe(df_d, use_container_width=True)
        if st.button("Limpar Diário"):
            st.session_state['diario'] = []
            st.rerun()

with aba2:
    st.subheader("Adicionar Alimento Personalizado")
    with st.form("f1"):
        n = st.text_input("Nome")
        c1, c2, c3, c4 = st.columns(4)
        k = c1.number_input("Kcal")
        cb = c2.number_input("Carb")
        p = c3.number_input("Prot")
        g = c4.number_input("Gord")
        if st.form_submit_button("Salvar"):
            st.session_state['diario'].append({
                "Hora": datetime.now().strftime("%H:%M"),
                "Alimento": n, "Kcal": k, "Carb": cb, "Prot": p, "Gord": g
            })
            st.rerun()
