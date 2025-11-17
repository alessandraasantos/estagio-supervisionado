import streamlit as st
import pandas as pd
import re
import os

st.set_page_config(page_title="GeraMargem - Cadastro", page_icon="📝")

# ---------------- ESTILO DA PÁGINA ----------------
page_bg = """
<style>
body {
    background-color: #FFE992 !important;
}

/* CARD */
.card {
    width: 520px;
    margin: auto;
    margin-top: 100px;
    background-color: #FFF4BC;
    padding: 40px 35px;
    border-radius: 18px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    text-align: center;
}

/* TÍTULOS */
h2 {
    font-weight: 700;
    color: #3D3D00 !important;
}

p {
    color: #5A5A00;
}

/* INPUTS */
.stTextInput>div>div>input, .stTextInput>div>div>textarea {
    background-color: #FFF4BC !important;
    border-radius: 12px !important;
    border: 1px solid #E1D676 !important;
    padding: 10px !important;
}

/* BOTÃO */
.stButton>button {
    background-color: #3D3D00 !important;
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

st.markdown("## 🔸 GeraMargem")
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
    if not re.search(r"[\W_]", senha):
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
