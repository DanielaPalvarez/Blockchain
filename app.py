import streamlit as st
from blockchain_core import Wallet, Blockchain, Transaction, TransactionInput, TransactionOutput, Miner
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Blockchain Educativa", page_icon="🧱", layout="centered")

# Inicialización de la blockchain
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
    st.session_state.miner = Miner(st.session_state.blockchain)
    st.session_state.wallets = {}
    st.session_state.tx_pool = []

# Estilos CSS personalizados
st.markdown("""
    <style>
    body { background-color: #f4f4f4; }
    .stButton > button { background-color: #2c3e50; color: white; border-radius: 10px; }
    .stSidebar { background-color: #f8f9fa; }
    .stTextInput, .stSelectbox, .stNumberInput { border-radius: 10px; }
    .stHeader, .stSubheader { color: #2c3e50; }
    </style>
""", unsafe_allow_html=True)

st.title("🔐 Proyecto Blockchain Educativa")

st.sidebar.title("📌 Navegación")
opcion = st.sidebar.radio("Ir a sección:", [
    "🏠 Inicio", "👤 Usuarios", "💳 Transacciones", "⛏️ Minería", "📦 Blockchain", "💰 Balances", "📂 UTXO Pool"
])

# --- Inicio ---
if opcion == "🏠 Inicio":
    st.subheader("📚 ¿Cómo funciona esta Blockchain?")
    st.markdown("""
    Este proyecto simula el funcionamiento de una **Blockchain educativa**, ideal para comprender los principios clave de esta tecnología. Aquí aprenderás sobre:

    - **Wallets (billeteras):** Cada usuario tiene un par de llaves criptográficas y una dirección.
    - **Transacciones:** Son operaciones entre usuarios, firmadas digitalmente y basadas en el modelo UTXO (salidas no gastadas).
    - **Bloques:** Agrupan transacciones validadas y están encadenados criptográficamente.
    - **Minería:** Simula la prueba de trabajo (PoW), donde se recompensa al minero que resuelve un reto computacional.

    Esta aplicación está desarrollada con **Python + Streamlit** y permite una interacción directa con los conceptos clave de forma sencilla y visual.
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("🔗 Bloques", len(st.session_state.blockchain.chain))
    col2.metric("📝 Transacciones en pool", len(st.session_state.tx_pool))
    col3.metric("👤 Usuarios", len(st.session_state.wallets))

# Las demás secciones se mantienen igual (Usuarios, Transacciones, Minería, etc.)

