import streamlit as st
from blockchain_core import Wallet, Blockchain, Transaction, TransactionInput, TransactionOutput

# Inicialización de la blockchain
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
    st.session_state.wallets = {}
    st.session_state.tx_pool = []

st.title("Proyecto Integrador: Blockchain")

st.sidebar.title("Menú")
opcion = st.sidebar.radio("Ir a:", [
    "Inicio", "Usuarios", "Transacciones", "Minería", "Blockchain", "UTXO Pool"
])

# --- Inicio ---
if opcion == "Inicio":
    st.subheader("Resumen del Sistema")
    st.write(f"Bloques minados: {len(st.session_state.blockchain.chain)}")
    st.write(f"Transacciones en pool: {len(st.session_state.tx_pool)}")
    st.write(f"Usuarios registrados: {len(st.session_state.wallets)}")

# --- Usuarios ---
elif opcion == "Usuarios":
    st.subheader("1. Wallets y Claves")
    if "wallet_counter" not in st.session_state:
        st.session_state.wallet_counter = 0

    if st.button("Agregar nuevo usuario"):
        st.session_state.wallet_counter += 1
        name = f"Usuario {st.session_state.wallet_counter}"
        wallet = Wallet(name=name)
        st.session_state.wallets[wallet.address] = wallet
        st.success(f"{name} creado correctamente.")

    if st.session_state.wallets:
        for addr, wallet in list(st.session_state.wallets.items()):
            keys = wallet.get_keys()
            with st.expander(f"{wallet.name}"):
                st.text(f"🔐 Clave privada:\n{keys['clave_privada']}")
                st.text(f"🔓 Clave pública:\n{keys['clave_publica']}")
                st.text(f"🏷️ Dirección:\n{keys['direccion']}")
                if st.button(f"Eliminar {wallet.name}", key=f"delete_{addr}"):
                    del st.session_state.wallets[addr]
                    st.success(f"{wallet.name} eliminado.")
                    st.rerun()
    else:
        st.info("No se ha creado ningún usuario aún.")

# --- Transacciones ---
elif opcion == "Transacciones":
    st.subheader("2. Crear Transacción")
    if len(st.session_state.wallets) < 2:
        st.warning("⚠️ Necesitas al menos 2 usuarios para hacer transacciones.")
    else:
        sender = st.selectbox("Remitente", list(st.session_state.wallets.keys()), key="sender")
        receiver = st.selectbox("Receptor", list(st.session_state.wallets.keys()), key="receiver")
        amount = st.number_input("Cantidad", min_value=1.0, value=1.0)
        fee = st.number_input("Fee", min_value=0.0, value=1.0)

        if st.button("Crear transacción"):
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
                st.error("Fondos insuficientes.")
            else:
                outputs = [TransactionOutput(amount, receiver)]
                if total > amount + fee:
                    outputs.append(TransactionOutput(total - amount - fee, sender))
                tx = Transaction(inputs, outputs, fee)
                tx.sign_inputs(st.session_state.wallets[sender])
                st.session_state.tx_pool.append(tx)
                st.success("Transacción añadida al pool.")

# --- Minería ---
elif opcion == "Minería":
    st.subheader("3. Minar Bloque")
    if not st.session_state.blockchain.chain:
        st.info("No hay bloque génesis. Selecciona minero para crearlo.")
        minero_addr = st.selectbox("Selecciona minero para bloque génesis", list(st.session_state.wallets.keys()))
        if st.button("Crear bloque génesis"):
            st.session_state.blockchain.create_genesis_block(minero_addr)
            st.success("Bloque génesis creado con 1000 monedas.")
    else:
        minero = st.selectbox("Selecciona minero", list(st.session_state.wallets.keys()), key="miner")
        if st.button("Minar bloque"):
            bloque = st.session_state.blockchain.mine_block(st.session_state.tx_pool, minero)
            st.session_state.tx_pool = []
            st.success(f"Bloque minado con hash: {bloque.hash[:20]}...")

# --- Blockchain ---
elif opcion == "Blockchain":
    st.subheader("4. Cadena de Bloques")
    for i, b in enumerate(st.session_state.blockchain.chain):
        st.write(f"Bloque {i}")
        st.json({
            "hash": b.hash,
            "prev": b.previous_hash,
            "nonce": b.nonce,
            "timestamp": b.timestamp,
            "txs": [tx.to_dict() if hasattr(tx, "to_dict") else vars(tx) for tx in b.transactions]
        })

# --- UTXO Pool ---
elif opcion == "UTXO Pool":
    st.subheader("5. UTXO Pool")
    utxos = st.session_state.blockchain.utxo_pool
    if utxos:
        for k, utxo in utxos.items():
            st.text(f"{k} -> Dirección: {utxo.direccion} | Cantidad: {utxo.cantidad}")
    else:
        st.info("No hay UTXOs disponibles.")
