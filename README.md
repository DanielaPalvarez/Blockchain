# Blockchain
Este proyecto implementa una simulación funcional de un sistema blockchain completo con su propia criptomoneda

## 🚀 Funcionalidades Principales

- **Creación de wallets:** Con claves pública y privada generadas mediante criptografía `ecdsa`.
- **Bloque génesis:** Inicializa la cadena con una recompensa minera.
- **Transacciones UTXO:** Usa entradas y salidas no gastadas para simular un modelo como Bitcoin.
- **Minería de bloques:** Valida transacciones y agrega bloques al blockchain.
- **Interfaz intuitiva:** Todo el sistema es controlado visualmente desde una app web hecha con Streamlit.

## 📂 Estructura del Proyecto

```
blockchain_proyecto_con_entorno/
├── app.py                 # Interfaz Streamlit para interactuar con la blockchain
├── blockchain_core.py     # Lógica del sistema: Wallets, Transacciones, Bloques, Blockchain
├── requirements.txt       # Dependencias necesarias para correr el proyecto
```

## 💻 Tecnologías Utilizadas

- Python 3.10+
- [Streamlit](https://streamlit.io) para UI interactiva
- [ecdsa](https://pypi.org/project/ecdsa/) para criptografía de curva elíptica
- Hashing SHA-256 para direcciones de usuario y bloques

## 🧠 Conceptos Implementados

- Criptografía de clave pública (ECDSA)
- Firmado digital de transacciones
- Modelo de transacciones UTXO
- Encadenamiento y validación de bloques
- Persistencia en estado de sesión (`st.session_state`)

## ⚙️ Instalación y Ejecución

1. **Clona el repositorio**  
   ```bash
   git clone https://github.com/tu_usuario/blockchain-simulador.git
   cd blockchain-simulador
   ```

2. **Crea un entorno virtual y actívalo**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # En Linux/Mac
   venv\Scripts\activate    # En Windows
   ```

3. **Instala las dependencias**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta la app**  
   ```bash
   streamlit run app.py
   ```

## 🧪 Ejemplo de Uso

- Crea una nueva wallet con un clic.
- Selecciona una wallet para minar el bloque génesis y recibir 1000 monedas.
- Realiza transacciones entre wallets.
- Mina nuevos bloques y observa cómo se actualiza la cadena.

## 📘 Créditos

Proyecto desarrollado con fines educativos para comprender el funcionamiento interno de una blockchain y su sistema de transacciones descentralizadas.

---

