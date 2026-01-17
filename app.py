import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Macro Planner TACO", layout="centered")

@st.cache_data
def carregar_dados():
    # Lê o CSV com o separador correto (ponto e vírgula)
    df = pd.read_csv('taco.csv', sep=';', encoding='utf-8')
    
    # Mapeamento por posição (evita erro se o nome da coluna tiver espaço invisível)
    # 0: Nome, 2: Kcal, 3: Proteína, 4: Gordura, 5: Carboidrato
    df = df.rename(columns={
        df.columns[0]: 'nome',
        df.columns[2]: 'kcal',
        df.columns[3]: 'prot',
        df.columns[4]: 'gord',
        df.columns[5]: 'carb'
    })
    
    # Função para converter "12,5" em 12.5 e tratar erros
    def limpar_num(valor):
        try:
            return float(str(valor).replace(',', '.').strip())
        except:
            return 0.0

    for col in ['kcal', 'prot', 'gord', 'carb']:
        df[col] = df[col].apply(limpar_num)
        
    return df[['nome', 'kcal', 'prot', 'gord', 'carb']]

try:
    taco = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar os arquivos: {e}")
    st.stop()

# --- ESTADO DO APP ---
if 'diario' not in st.session_state:
    st.session_state['diario'] = []

st.title("🥗 Meu Diário de Macros")

aba1, aba2 = st.tabs(["🍽 Diário", "➕ Manual"])

with aba1:
    busca = st.text_input("Buscar Alimento (ex: Frango, Arroz...)")
    
    if busca:
        itens = taco[taco['nome'].str.contains(busca, case=False, na=False)]
        if not itens.empty:
            escolha = st.selectbox("Selecione:", itens['nome'].unique())
            c1, c2 = st.columns(2)
            gramas = c1.number_input("Gramas (g)", min_value=1.0, value=100.0)
            hora = c2.time_input("Hora", datetime.now())
            
            if st.button("Adicionar"):
                row = taco[taco['nome'] == escolha].iloc[0]
                f = gramas / 100
                st.session_state['diario'].append({
                    "Hora": hora.strftime("%H:%M"),
                    "Alimento": escolha,
                    "Kcal": row['kcal'] * f, "Carb": row['carb'] * f,
                    "Prot": row['prot'] * f, "Gord": row['gord'] * f
                })
                st.rerun()

    if st.session_state['diario']:
        df_d = pd.DataFrame(st.session_state['diario'])
        st.divider()
        # Dashboard
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🔥 Kcal", f"{df_d['Kcal'].sum():.0f}")
        m2.metric("🍞 Carb", f"{df_d['Carb'].sum():.1f}g")
        m3.metric("🍗 Prot", f"{df_d['Prot'].sum():.1f}g")
        m4.metric("🥑 Gord", f"{df_d['Gord'].sum():.1f}g")
        st.dataframe(df_d, use_container_width=True)
        if st.button("Limpar"):
            st.session_state['diario'] = []
            st.rerun()

with aba2:
    st.subheader("Adicionar Alimento Personalizado")
    with st.form("manual"):
        n = st.text_input("Nome")
        c1, c2, c3, c4 = st.columns(4)
        k, cb, p, g = c1.number_input("Kcal"), c2.number_input("Carb"), c3.number_input("Prot"), c4.number_input("Gord")
        if st.form_submit_button("Salvar"):
            st.session_state['diario'].append({
                "Hora": datetime.now().strftime("%H:%M"),
                "Alimento": n, "Kcal": k, "Carb": cb, "Prot": p, "Gord": g
            })
            st.rerun()
