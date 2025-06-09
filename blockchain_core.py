import hashlib
import json
import time
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError

# --- WALLET ---
class Wallet:
    def __init__(self, name=""):
        self.name = name
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        self.address = hashlib.sha256(self.public_key.to_string()).hexdigest()

    def sign(self, message: bytes):
        return self.private_key.sign(message).hex()

    def get_keys(self):
        return {
            "nombre": self.name,
            "clave_privada": self.private_key.to_string().hex(),
            "clave_publica": self.public_key.to_string().hex(),
            "direccion": self.address
        }

# --- TRANSACCIONES Y UTXO ---
class TransactionInput:
    def __init__(self, txid, index, pubkey=None):
        self.txid = txid
        self.index = index
        self.signature = None
        self.pubkey = pubkey

    def to_dict(self):
        return {
            "txid": self.txid,
            "index": self.index,
            "firma": self.signature,
            "pubkey": self.pubkey
        }

class TransactionOutput:
    def __init__(self, cantidad, direccion):
        self.cantidad = cantidad
        self.direccion = direccion

    def to_dict(self):
        return {
            "cantidad": self.cantidad,
            "direccion": self.direccion
        }

class Transaction:
    def __init__(self, inputs, outputs, fee=0.0):
        self.inputs = inputs
        self.outputs = outputs
        self.fee = fee
        self.txid = self.generate_txid()

    def to_dict(self, include_signatures=True):
        return {
            "inputs": [i.to_dict() if include_signatures else {"txid": i.txid, "index": i.index} for i in self.inputs],
            "outputs": [o.to_dict() for o in self.outputs],
            "fee": self.fee
        }

    def generate_txid(self):
        data = json.dumps(self.to_dict(include_signatures=False), sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()

    def sign_inputs(self, wallet):
        pubkey = wallet.public_key.to_string().hex()
        for inp in self.inputs:
            message = f"{inp.txid}:{inp.index}".encode()
            inp.signature = wallet.sign(message)
            inp.pubkey = pubkey

    def verify_inputs(self, utxo_pool):
        for inp in self.inputs:
            key = f"{inp.txid}:{inp.index}"
            utxo = utxo_pool.get(key)
            if not utxo:
                return False
            try:
                pubkey_bytes = bytes.fromhex(inp.pubkey)
                pubkey = VerifyingKey.from_string(pubkey_bytes, curve=SECP256k1)
                message = f"{inp.txid}:{inp.index}".encode()
                if not pubkey.verify(bytes.fromhex(inp.signature), message):
                    return False
            except (BadSignatureError, ValueError):
                return False
        return True

# --- BLOQUES Y BLOCKCHAIN ---
class Block:
    def __init__(self, index, previous_hash, transactions, nonce=0):
        self.index = index
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        return hashlib.sha256(json.dumps(block_data, sort_keys=True).encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain = []
        self.utxo_pool = {}
        self.difficulty = 4

    def add_block(self, block):
        if block.previous_hash != self.chain[-1].hash:
            raise Exception("Hash del bloque anterior no coincide.")
        if not block.hash.startswith("0" * self.difficulty):
            raise Exception("No cumple con la dificultad requerida.")
        self.chain.append(block)

# --- GÉNESIS Y MINERÍA ---
class Miner:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def create_genesis_block(self, direccion_inicial):
        recompensa = Transaction([], [TransactionOutput(1000, direccion_inicial)])
        bloque_genesis = Block(
            index=0,
            previous_hash="0",
            transactions=[recompensa]
        )
        self.blockchain.utxo_pool[f"{recompensa.txid}:0"] = recompensa.outputs[0]
        self.blockchain.chain.append(bloque_genesis)
        return bloque_genesis

    def mine_new_block(self, transacciones, direccion_minero):
        utxo_pool = self.blockchain.utxo_pool
        validas = []
        for tx in transacciones:
            if tx.verify_inputs(utxo_pool):
                validas.append(tx)
                for inp in tx.inputs:
                    utxo_pool.pop(f"{inp.txid}:{inp.index}", None)
                for i, out in enumerate(tx.outputs):
                    utxo_pool[f"{tx.txid}:{i}"] = out

        fees = sum(tx.fee for tx in validas)
        recompensa = Transaction([], [TransactionOutput(3 + fees, direccion_minero)])

        nuevo_index = len(self.blockchain.chain)
        bloque = Block(nuevo_index, self.blockchain.chain[-1].hash, validas + [recompensa])

        while not bloque.hash.startswith("0000"):
            bloque.nonce += 1
            bloque.hash = bloque.calculate_hash()

        self.blockchain.add_block(bloque)
        return bloque
