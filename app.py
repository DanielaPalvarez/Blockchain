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

# --- Usuarios ---
elif opcion == "👤 Usuarios":
    st.subheader("🔐 Gestión de Wallets")
    if "wallet_counter" not in st.session_state:
        st.session_state.wallet_counter = 0

    if st.button("➕ Crear nuevo usuario"):
        st.session_state.wallet_counter += 1
        name = f"Usuario {st.session_state.wallet_counter}"
        wallet = Wallet(name=name)
        st.session_state.wallets[wallet.address] = wallet
        st.success(f"✅ {name} creado correctamente.")

    if st.session_state.wallets:
        for addr, wallet in list(st.session_state.wallets.items()):
            keys = wallet.get_keys()
            with st.expander(f"🧾 {wallet.name}"):
                st.code(keys['clave_privada'], language='text')
                st.code(keys['clave_publica'], language='text')
                st.code(keys['direccion'], language='text')
                if st.button(f"🗑️ Eliminar {wallet.name}", key=f"delete_{addr}"):
                    del st.session_state.wallets[addr]
                    st.success(f"{wallet.name} eliminado.")
                    st.rerun()
    else:
        st.info("👈 Usa el botón para crear un usuario.")

# --- Transacciones ---
elif opcion == "💳 Transacciones":
    st.subheader("📨 Crear Transacción")
    if len(st.session_state.wallets) < 2:
        st.warning("⚠️ Necesitas al menos 2 usuarios para transaccionar.")
    else:
        sender = st.selectbox("📤 Remitente", list(st.session_state.wallets.keys()), key="sender")
        receiver = st.selectbox("📥 Receptor", list(st.session_state.wallets.keys()), key="receiver")
        amount = st.number_input("💵 Cantidad a enviar", min_value=1.0, value=1.0)
        fee = st.number_input("🪙 Fee (comisión de minería)", min_value=0.0, value=1.0)

        if st.button("✅ Enviar transacción"):
            utxos = st.session_state.blockchain.utxo_pool
            inputs, total = [], 0
            for key, utxo in utxos.items():
                if utxo.direccion == sender:
                    txid, idx = key.split(":")
                    inputs.append(TransactionInput(txid, int(idx)))
                    total += utxo.cantidad
                    if total >= amount + fee:
                        break

            if total < amount + fee:
                st.error("🚫 Fondos insuficientes.")
            else:
                outputs = [TransactionOutput(amount, receiver)]
                if total > amount + fee:
                    outputs.append(TransactionOutput(total - amount - fee, sender))
                tx = Transaction(inputs, outputs, fee)
                tx.sign_inputs(st.session_state.wallets[sender])
                st.session_state.tx_pool.append(tx)
                st.success("📩 Transacción añadida al pool.")

# --- Minería ---
elif opcion == "⛏️ Minería":
    st.subheader("⚒️ Proceso de Minería")
    if not st.session_state.blockchain.chain:
        st.info("⚠️ No hay bloque génesis. Crea uno primero.")
        minero_addr = st.selectbox("Selecciona minero para génesis", list(st.session_state.wallets.keys()))
        if st.button("🧱 Crear bloque génesis"):
            st.session_state.miner.create_genesis_block(minero_addr)
            st.success("🚀 Bloque génesis creado con 1000 monedas.")
    else:
        minero = st.selectbox("Selecciona minero", list(st.session_state.wallets.keys()), key="miner")
        if st.button("⛏️ Ejecutar minería"):
            bloque = st.session_state.miner.mine_new_block(st.session_state.tx_pool, minero)
            st.session_state.tx_pool = []
            st.success(f"✅ Bloque minado con hash: {bloque.hash[:20]}...")

# --- Blockchain ---
elif opcion == "📦 Blockchain":
    st.subheader("🧱 Cadena de Bloques")
    for i, b in enumerate(st.session_state.blockchain.chain):
        with st.expander(f"🔗 Bloque {i}"):
            st.json(b.to_dict())

# --- Balances ---
elif opcion == "💰 Balances":
    st.subheader("💹 Saldos por Usuario")
    balances = {}
    for utxo in st.session_state.blockchain.utxo_pool.values():
        balances[utxo.direccion] = balances.get(utxo.direccion, 0) + utxo.cantidad
s
    data = []
    for addr, monto in balances.items():
        nombre = st.session_state.wallets[addr].name if addr in st.session_state.wallets else "Desconocido"
        data.append({"Usuario": nombre, "Dirección": addr[:10] + "...", "Saldo": monto})

    df = pd.DataFrame(data)
    st.table(df)

# --- UTXO Pool ---
elif opcion == "📂 UTXO Pool":
    st.subheader("🔎 Estado del UTXO Pool")
    utxos = st.session_state.blockchain.utxo_pool
    if utxos:
        for k, utxo in utxos.items():
            st.code(f"{k} => {utxo.direccion[:10]}... | {utxo.cantidad} monedas")
    else:
        st.info("🚫 No hay UTXOs disponibles.")
s