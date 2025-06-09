import streamlit as st
from blockchain_core import Wallet, Blockchain, Transaction, TransactionInput, TransactionOutput, Miner
import pandas as pd

# ✅ Esta línea debe ser la primera de Streamlit
st.set_page_config(page_title="Blockchain Educativa", layout="centered")

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

st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a sección:", [
    "🏠 Inicio", "👤 Usuarios", "💳 Transacciones", "⛏️ Minería", "📦 Blockchain", "💰 Balances", "📂 UTXO Pool"
])

# --- INICIO ---
if opcion == "🏠 Inicio":
    st.subheader("¿Cómo funciona esta Blockchain?")
    st.markdown("""
    Este proyecto simula el funcionamiento de una **Blockchain educativa**, ideal para comprender los principios clave de esta tecnología. Aquí aprenderás sobre:

    - **Wallets (billeteras):** Cada usuario tiene un par de llaves criptográficas y una dirección.
    - **Transacciones:** Operaciones entre usuarios, firmadas digitalmente, basadas en el modelo UTXO.
    - **Bloques:** Agrupan transacciones validadas y están encadenados mediante hashes.
    - **Minería:** Simula prueba de trabajo (PoW) con recompensa.

    Esta app está construida con **Python + Streamlit**.
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("🔗 Bloques", len(st.session_state.blockchain.chain))
    col2.metric("📝 Pool de transacciones", len(st.session_state.tx_pool))
    col3.metric("👤 Usuarios", len(st.session_state.wallets))

    if st.session_state.genesis_wallet:
        st.markdown("### 🔐 Credenciales del Usuario Génesis")
        keys = st.session_state.genesis_wallet.get_keys()
        st.markdown("**Clave privada**")
        st.code(keys['clave_privada'])
        st.markdown("**Clave pública**")
        st.code(keys['clave_publica'])
        st.markdown("**Dirección**")
        st.code(keys['direccion'])

# --- USUARIOS ---
elif opcion == "👤 Usuarios":
    st.subheader("👥 Gestión de Usuarios / Wallets")

    if st.button("Crear nuevo usuario"):
        st.session_state.wallet_counter += 1
        name = f"Usuario {st.session_state.wallet_counter}"
        wallet = Wallet(name=name)
        st.session_state.wallets[wallet.address] = wallet
        st.success(f"✅ {name} creado.")

        if not st.session_state.genesis_created:
            st.session_state.miner.create_genesis_block(wallet.address)
            st.session_state.genesis_created = True
            st.session_state.genesis_wallet = wallet
            st.info(f"🚀 Bloque génesis creado con 1000 monedas para {name}.")

    if st.session_state.wallets:
        balances = {}
        for utxo in st.session_state.blockchain.utxo_pool.values():
            balances[utxo.direccion] = balances.get(utxo.direccion, 0) + utxo.cantidad

        for addr, wallet in st.session_state.wallets.items():
            keys = wallet.get_keys()
            saldo = balances.get(addr, 0)
            with st.expander(f"🧾 {wallet.name} | Saldo: {saldo} monedas"):
                st.markdown("**Clave privada**")
                st.code(keys['clave_privada'])
                st.markdown("**Clave pública**")
                st.code(keys['clave_publica'])
                st.markdown("**Dirección**")
                st.code(keys['direccion'])
                if st.button(f"Eliminar {wallet.name}", key=f"del_{addr}"):
                    del st.session_state.wallets[addr]
                    st.success(f"{wallet.name} eliminado.")
                    st.rerun()
    else:
        st.info("👈 Usa el botón para crear usuarios.")

# --- TRANSACCIONES ---
elif opcion == "💳 Transacciones":
    st.subheader("📨 Crear Transacción")
    if len(st.session_state.wallets) < 2:
        st.warning("⚠️ Necesitas al menos 2 usuarios para transaccionar.")
    else:
        sender = st.selectbox("📤 Remitente", list(st.session_state.wallets.keys()), key="sender")
        receiver = st.selectbox("📥 Receptor", list(st.session_state.wallets.keys()), key="receiver")
        amount = st.number_input("💵 Cantidad a enviar", min_value=1.0, value=1.0)
        fee = st.number_input("🪙 Fee (comisión de minería)", min_value=0.0, value=1.0)

        saldo = sum(utxo.cantidad for k, utxo in st.session_state.blockchain.utxo_pool.items() if utxo.direccion == sender)
        if saldo < amount + fee:
            st.warning("💡 Este usuario no tiene suficientes fondos. Debes minar o usar otro remitente.")
        else:
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

                outputs = [TransactionOutput(amount, receiver)]
                if total > amount + fee:
                    outputs.append(TransactionOutput(total - amount - fee, sender))
                tx = Transaction(inputs, outputs, fee)
                tx.sign_inputs(st.session_state.wallets[sender])
                st.session_state.tx_pool.append(tx)
                st.success("📩 Transacción añadida al pool.")

# --- MINERÍA ---
elif opcion == "⛏️ Minería":
    st.subheader("⚒️ Minar transacciones")
    if not st.session_state.tx_pool:
        st.info("No hay transacciones en el pool para minar.")
    else:
        miner_address = st.selectbox("Selecciona un minero (dirección de wallet):", list(st.session_state.wallets.keys()))
        if st.button("🚀 Iniciar minería"):
            bloque = st.session_state.miner.mine_new_block(st.session_state.tx_pool, miner_address)
            st.session_state.tx_pool = []
            st.success(f"✅ Bloque minado con éxito. Hash: {bloque.hash[:15]}...")


# --- BLOCKCHAIN ---
elif opcion == "📦 Blockchain":
    st.subheader("📜 Visualización de la Blockchain")
    for bloque in st.session_state.blockchain.chain:
        with st.expander(f"🧱 Bloque {bloque.index} | Hash: {bloque.hash[:15]}..."):
            st.write(f"🔗 Anterior: {bloque.previous_hash}")
            st.write(f"🕒 Timestamp: {bloque.timestamp}")
            st.write(f"📄 Transacciones: {len(bloque.transactions)}")
            for tx in bloque.transactions:
                st.text(tx)

# --- BALANCES ---
elif opcion == "💰 Balances":
    st.subheader("📊 Saldos actuales por usuario")
    balances = {}
    for utxo in st.session_state.blockchain.utxo_pool.values():
        balances[utxo.direccion] = balances.get(utxo.direccion, 0) + utxo.cantidad

    df_bal = pd.DataFrame([
        {"Usuario": st.session_state.wallets[addr].name, "Dirección": addr, "Saldo": bal}
        for addr, bal in balances.items() if addr in st.session_state.wallets
    ])
    st.dataframe(df_bal)

# --- UTXO POOL ---
elif opcion == "📂 UTXO Pool":
    st.subheader("📄 UTXO Pool (salidas no gastadas)")
    data = []
    for k, utxo in st.session_state.blockchain.utxo_pool.items():
        data.append({
            "TxID:Index": k,
            "Dirección": utxo.direccion,
            "Cantidad": utxo.cantidad
        })
    df_utxo = pd.DataFrame(data)
    st.dataframe(df_utxo)