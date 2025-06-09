import streamlit as st
from blockchain_core import Wallet, Blockchain, Transaction, TransactionInput, TransactionOutput, Miner
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Blockchain Educativa", page_icon="🧱", layout="centered")

# Estilo visual adaptado a modo oscuro
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #1e1e1e;
        color: #f0f0f0;
    }
    .stApp {
        background-color: #1e1e1e;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
    }
    .stSidebar {
        background-color: #2c2c2c;
    }
    .stMetric {
        color: white;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
    st.session_state.miner = Miner(st.session_state.blockchain)
    st.session_state.wallets = {}
    st.session_state.tx_pool = []
    st.session_state.wallet_counter = 0
    st.session_state.genesis_created = False
    st.session_state.genesis_wallet = None

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
import streamlit as st
from blockchain_core import Wallet, Blockchain, Transaction, TransactionInput, TransactionOutput, Miner
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Blockchain Educativa", page_icon="🧱", layout="centered")

# Estilo visual adaptado a modo oscuro
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #1e1e1e;
        color: #f0f0f0;
    }
    .stApp {
        background-color: #1e1e1e;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
    }
    .stSidebar {
        background-color: #2c2c2c;
    }
    .stMetric {
        color: white;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
    st.session_state.miner = Miner(st.session_state.blockchain)
    st.session_state.wallets = {}
    st.session_state.tx_pool = []
    st.session_state.wallet_counter = 0
    st.session_state.genesis_created = False
    st.session_state.genesis_wallet = None

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

    if st.session_state.genesis_wallet:
        st.markdown("""
        ### 🔐 Credenciales del Usuario Génesis
        Este usuario fue creado automáticamente para iniciar la blockchain. Puedes usarlo para hacer tus primeras transacciones:
        """)
        keys = st.session_state.genesis_wallet.get_keys()
        st.markdown("🔐 **Clave privada**")
        st.code(keys['clave_privada'], language='text')
        st.markdown("🔓 **Clave pública**")
        st.code(keys['clave_publica'], language='text')
        st.markdown("🏷️ **Dirección**")
        st.code(keys['direccion'], language='text')

# --- Usuarios ---
elif opcion == "👤 Usuarios":
    st.subheader("🔐 Gestión de Wallets")

    if st.button("➕ Crear nuevo usuario"):
        st.session_state.wallet_counter += 1
        name = f"Usuario {st.session_state.wallet_counter}"
        wallet = Wallet(name=name)
        st.session_state.wallets[wallet.address] = wallet
        st.success(f"✅ {name} creado correctamente.")

        # Crear bloque génesis automáticamente con el primer usuario
        if not st.session_state.genesis_created:
            st.session_state.miner.create_genesis_block(wallet.address)
            st.session_state.genesis_created = True
            st.session_state.genesis_wallet = wallet
            st.info(f"🚀 Bloque génesis creado automáticamente para {name} con 1000 monedas.")

    if st.session_state.wallets:
        balances = {}
        for utxo in st.session_state.blockchain.utxo_pool.values():
            balances[utxo.direccion] = balances.get(utxo.direccion, 0) + utxo.cantidad

        for addr, wallet in list(st.session_state.wallets.items()):
            keys = wallet.get_keys()
            saldo = balances.get(addr, 0)
            with st.expander(f"🧾 {wallet.name} | Saldo: {saldo} monedas"):
                st.markdown("🔐 **Clave privada**")
                st.code(keys['clave_privada'], language='text')
                st.markdown("🔓 **Clave pública**")
                st.code(keys['clave_publica'], language='text')
                st.markdown("🏷️ **Dirección**")
                st.code(keys['direccion'], language='text')
                if st.button(f"🗑️ Eliminar {wallet.name}", key=f"delete_{addr}"):
                    del st.session_state.wallets[addr]
                    st.success(f"{wallet.name} eliminado.")
                    st.rerun()
    else:
        st.info("👈 Usa el botón para crear un usuario.")