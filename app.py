import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Macro Planner TACO", layout="centered")

# --- ESTILO ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAR DADOS ---
@st.cache_data
def carregar_dados():
    # Carrega com separador ; conforme o seu arquivo
    df = pd.read_csv('taco.csv', sep=';', encoding='utf-8')
    
    # Limpeza básica: remove espaços e garante nomes consistentes
    df.columns = df.columns.str.strip()
    
    # Mapeamento para facilitar o código (Ajustado para as colunas do seu arquivo)
    # Colunas esperadas no seu CSV: "Nome do Alimento", "Energia (kcal)", "Proteína (g)", etc.
    df = df.rename(columns={
        'Nome do Alimento': 'nome',
        'Energia (kcal)': 'kcal',
        'Carboidrato (g)': 'carb',
        'Proteína (g)': 'prot',
        'Lipídeos (g)': 'gord'
    })
    
    # Converte colunas para numérico, tratando erros (vírgula por ponto)
    for col in ['kcal', 'carb', 'prot', 'gord']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].toString().replace(',', '.'), errors='coerce').fillna(0)
            
    return df

try:
    taco = carregar_dados()
except Exception as e:
    st.error(f"Erro ao ler taco.csv: {e}")
    st.stop()

# --- ESTADO DO APP ---
if 'diario' not in st.session_state:
    st.session_state['diario'] = []
if 'custom' not in st.session_state:
    st.session_state['custom'] = pd.DataFrame(columns=['nome', 'kcal', 'carb', 'prot', 'gord'])

# --- INTERFACE ---
st.title("🍎 Meu Diário de Macros")

aba1, aba2 = st.tabs(["🍽 Diário", "➕ Alimento Externo"])

# --- ABA 1: DIÁRIO ---
with aba1:
    with st.container():
        busca = st.text_input("Buscar alimento na TACO (ex: Frango, Arroz...)")
        
        if busca:
            sugestoes = taco[taco['nome'].str.contains(busca, case=False, na=False)]
            if not sugestoes.empty:
                alimento_sel = st.selectbox("Selecione o item:", sugestoes['nome'].unique())
                
                c1, c2 = st.columns(2)
                gramas = c1.number_input("Quantidade (g)", min_value=1.0, value=100.0, step=10.0)
                hora = c2.time_input("Horário da refeição")

                if st.button("Adicionar ao Diário"):
                    # Pega os dados do alimento selecionado
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
            else:
                st.warning("Nenhum alimento encontrado com esse nome.")

    st.divider()

    # Exibição dos Resultados
    if st.session_state['diario']:
        df_hoje = pd.DataFrame(st.session_state['diario'])
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("🔥 Kcal", f"{df_hoje['Kcal'].sum():.0f}")
        col_m2.metric("🍞 Carb", f"{df_hoje['Carb'].sum():.1f}g")
        col_m3.metric("🍗 Prot", f"{df_hoje['Prot'].sum():.1f}g")
        col_m4.metric("🥑 Gord", f"{df_hoje['Gord'].sum():.1f}g")
        
        st.table(df_hoje[["Hora", "Alimento", "Qtd", "Kcal"]])
        
        if st.button("Limpar Diário"):
            st.session_state['diario'] = []
            st.rerun()

# --- ABA 2: ADICIONAR FORA DA TACO ---
with aba2:
    st.subheader("Alimento que não está na lista")
    with st.form("add_custom"):
        nome_c = st.text_input("Nome do Alimento")
        col_a, col_b, col_c, col_d = st.columns(4)
        kc = col_a.number_input("Kcal (100g)")
        ca = col_b.number_input("Carb (100g)")
        pr = col_c.number_input("Prot (100g)")
        go = col_d.number_input("Gord (100g)")
        
        if st.form_submit_button("Salvar e Adicionar"):
            st.session_state['diario'].append({
                "Hora": datetime.now().strftime("%H:%M"),
                "Alimento": nome_c,
                "Qtd": "100g",
                "Kcal": kc, "Carb": ca, "Prot": pr, "Gord": go
            })
            st.success("Alimento personalizado adicionado ao diário!")
