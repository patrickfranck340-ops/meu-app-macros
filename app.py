import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Macro Minimal", page_icon="🥗", layout="centered")

# --- ESTILO CSS PARA MINIMALISMO ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'diario' not in st.session_state:
    st.session_state['diario'] = []
if 'custom_alimentos' not in st.session_state:
    st.session_state['custom_alimentos'] = pd.DataFrame(columns=['nome', 'kcal', 'carb', 'prot', 'gord'])

# --- TELA PRINCIPAL ---
st.title("🥗 Macro Planner")

aba = st.sidebar.radio("Navegação", ["Diário", "Adicionar Alimento", "Configurações"])

if aba == "Diário":
    st.subheader("Refeições de Hoje")
    
    # Form para adicionar refeição
    with st.expander("➕ Registrar Alimento"):
        col1, col2 = st.columns(2)
        hora = col1.time_input("Horário")
        nome = col2.text_input("Alimento")
        
        c1, c2, c3, c4 = st.columns(4)
        kcal = c1.number_input("Kcal", min_value=0.0)
        carb = c2.number_input("Carb (g)", min_value=0.0)
        prot = c3.number_input("Prot (g)", min_value=0.0)
        gord = c4.number_input("Gord (g)", min_value=0.0)
        
        if st.button("Salvar no Diário"):
            st.session_state['diario'].append({
                "Horário": hora.strftime("%H:%M"),
                "Alimento": nome,
                "Kcal": kcal,
                "Carb": carb,
                "Prot": prot,
                "Gord": gord
            })
            st.rerun()

    # Exibição dos Totais
    if st.session_state['diario']:
        df = pd.DataFrame(st.session_state['diario'])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Kcal", f"{df['Kcal'].sum():.0f}")
        m2.metric("Carbs", f"{df['Carb'].sum():.1f}g")
        m3.metric("Prot", f"{df['Prot'].sum():.1f}g")
        m4.metric("Gord", f"{df['Gord'].sum():.1f}g")
        
        st.divider()
        st.dataframe(df, use_container_width=True)
        if st.button("Limpar Diário"):
            st.session_state['diario'] = []
            st.rerun()
    else:
        st.info("Nenhum alimento registrado hoje.")

elif aba == "Adicionar Alimento":
    st.subheader("Cadastrar Novo Alimento (Base Pessoal)")
    # Aqui você pode expandir para ler o CSV da TACO
    st.write("Em breve: Integração direta com busca na TACO.")