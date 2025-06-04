
import streamlit as st
from blockchain_core import Wallet, Blockchain, Transaction, TransactionInput, TransactionOutput

# Inicialización
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
    st.session_state.wallets = {}
    st.session_state.tx_pool = []

st.title("🪙 Simulador de Blockchain con Minería y UTXO")

st.header("1. Crear Wallet")
if st.button("Crear nueva wallet"):
    wallet = Wallet()
    st.session_state.wallets[wallet.address] = wallet
    st.success(f"Wallet creada: {wallet.address[:15]}...")

st.subheader("Wallets disponibles")
for addr, w in st.session_state.wallets.items():
    st.code(f"{addr[:60]}...")

st.header("2. Crear Bloque Génesis")
minero_addr = st.selectbox("Selecciona minero para el bloque génesis", list(st.session_state.wallets.keys()), key="genesis")
if st.button("Crear bloque génesis"):
    st.session_state.blockchain.create_genesis_block(minero_addr)
    st.success("Bloque génesis creado y minado con 1000 monedas.")

st.header("3. Crear Transacción")
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

st.header("4. Minar Bloque")
minero = st.selectbox("Selecciona minero", list(st.session_state.wallets.keys()), key="miner")
if st.button("Minar bloque"):
    bloque = st.session_state.blockchain.mine_block(st.session_state.tx_pool, minero)
    st.session_state.tx_pool = []
    st.success(f"Bloque minado con hash: {bloque.hash[:20]}...")

st.header("5. Blockchain")
for i, b in enumerate(st.session_state.blockchain.chain):
    st.write(f"Bloque {i}")
    st.json({
        "hash": b.hash,
        "prev": b.previous_hash,
        "txs": [tx.to_dict() if hasattr(tx, "to_dict") else vars(tx) for tx in b.transactions]
    })
