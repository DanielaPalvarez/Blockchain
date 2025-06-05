
import hashlib
import json
import time
from ecdsa import SigningKey, SECP256k1

# Wallet
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


# Transacciones
class TransactionInput:
    def __init__(self, txid, index):
        self.txid = txid
        self.index = index
        self.signature = None

    def to_dict(self):
        return {"txid": self.txid, "index": self.index, "firma": self.signature}

class TransactionOutput:
    def __init__(self, cantidad, direccion):
        self.cantidad = cantidad
        self.direccion = direccion

    def to_dict(self):
        return {"cantidad": self.cantidad, "direccion": self.direccion}

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
        for inp in self.inputs:
            message = f"{inp.txid}:{inp.index}".encode()
            inp.signature = wallet.sign(message)

# Bloques y Blockchain
class Block:
    def __init__(self, previous_hash, transactions, nonce=0):
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() if hasattr(tx, "to_dict") else vars(tx) for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        return hashlib.sha256(json.dumps(block_data, sort_keys=True).encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.utxo_pool = {}
        self.difficulty = 2

    def create_genesis_block(self, address):
        output = TransactionOutput(1000, address)
        tx = Transaction([], [output])
        self.utxo_pool[f"{tx.txid}:0"] = output
        genesis_block = Block("0", [tx])
        self.chain.append(genesis_block)

    def add_block(self, block):
        if block.previous_hash != self.chain[-1].hash:
            raise Exception("Hash anterior no coincide.")
        self.chain.append(block)

    def mine_block(self, transactions, minero):
        for tx in transactions:
            for inp in tx.inputs:
                key = f"{inp.txid}:{inp.index}"
                self.utxo_pool.pop(key, None)
            for i, out in enumerate(tx.outputs):
                self.utxo_pool[f"{tx.txid}:{i}"] = out

        fee = sum(tx.fee for tx in transactions)
        reward_tx = Transaction([], [TransactionOutput(3 + fee, minero)])
        block = Block(self.chain[-1].hash, transactions + [reward_tx])
        while not block.hash.startswith("0" * self.difficulty):
            block.nonce += 1
            block.hash = block.calculate_hash()
        self.add_block(block)
        return block
