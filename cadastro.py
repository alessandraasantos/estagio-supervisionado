import streamlit as st
import pandas as pd
import re
import os

st.set_page_config(
    page_title="GeraMargem - Cadastro",
    page_icon="📝",
    layout="centered"
)

# ---------------- ESTILO DA PÁGINA ----------------
page_bg = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap');

/* REMOVE O RETÂNGULO AUTOMÁTICO DO STREAMLIT */
.block-container {
    background: transparent !important;
    box-shadow: none !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* APLICAR FONTE PERSONALIZADA SOMENTE NO TÍTULO */
.geramargem-title {
    font-family: 'Poppins', sans-serif !important;
    font-size: 43px !important;
    font-weight: 700 !important;
    color: #3D3D00 !important;
}

html, body, .main, .block-container {
    background-color: #FFE135  !important;
}

/* REMOVE HEADERS E PADDING AUTOMÁTICO DO STREAMLIT */
header, .stApp > header {
    display: none !important;
}

.css-18e3th9, .css-1d391kg, .stMainBlockContainer {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* Remove qualquer container que Streamlit coloca acima */
.stApp {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* TÍTULOS */
h2, h3, h4 {
    color: #3D3D00 !important;
    font-weight: bold;
}

p {
    color: #5A5A00;
}

/* INPUTS */
.stTextInput>div>div>input {
    background-color: #FBEC5D !important;
    border-radius: 12px !important;
    border: 1px solid #E1D676 !important;
    padding: 10px !important;
}

/* BOTÃO */
.stButton>button {
    background-color: #FBEC5D !important;
    color: white !important;
    padding: 10px 30px;
    border-radius: 20px;
    font-weight: bold;
    border: none;
    transition: 0.2s;
}

.stButton>button:hover {
    background-color: #1F1F00 !important;
    
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------------- BANCO DE DADOS ----------------
if not os.path.exists("users.csv"):
    df = pd.DataFrame(columns=["nome", "email", "senha", "autorizado"])
    df.to_csv("users.csv", index=False)

df = pd.read_csv("users.csv")

# ---------------- INTERFACE ----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

# TÍTULO COM FONTE PERSONALIZADA
st.markdown("<h2 class='geramargem-title'>GeraMargem</h2>", unsafe_allow_html=True)

st.write("### Crie sua conta")
st.write("Preencha os dados e aguarde autorização do responsável.")

nome = st.text_input("Nome completo")
email = st.text_input("E-mail")
senha = st.text_input("Senha (8 caracteres, incluindo maiúscula, minúscula, número e símbolo)", type="password")

# ---------------- VALIDAÇÃO DE SENHA ----------------
def senha_valida(senha):
    if len(senha) != 8:
        return False
    if not re.search(r"[A-Z]", senha):
        return False
    if not re.search(r"[a-z]", senha):
        return False
    if not re.search(r"[0-9]", senha):
        return False
    if not re.search(r"[\\W_]", senha):
        return False
    return True

# ---------------- BOTÃO DE CADASTRO ----------------
if st.button("Cadastrar"):
    if not nome or not email or not senha:
        st.error("Preencha todos os campos.")
    elif not senha_valida(senha):
        st.error("A senha deve ter 8 caracteres e incluir maiúsculas, minúsculas, números e símbolos.")
    elif email in df["email"].values:
        st.warning("E-mail já cadastrado! Aguarde autorização do responsável.")
    else:
        novo = pd.DataFrame([[nome, email, senha, "nao"]],
                            columns=["nome", "email", "senha", "autorizado"])
        df = pd.concat([df, novo], ignore_index=True)
        df.to_csv("users.csv", index=False)
        st.success("Cadastro realizado! Aguarde autorização para acessar o sistema.")

st.markdown("</div>", unsafe_allow_html=True)
