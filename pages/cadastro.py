import streamlit as st
import pandas as pd
import re
import os

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="GeraMargem - Cadastro",
    page_icon="📝",
    layout="centered"
)

# ---------------- ESTILO INSTITUCIONAL ----------------
page_bg = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap');

/* FUNDO GERAL */
html, body, .stApp {
    background-color: #FFE992 !important;
}

/* REMOVE HEADER PADRÃO */
header, .stApp > header {
    display: none !important;
}

/* ÁREA DE CONTEÚDO */
.content-area {
    max-width: 520px;
    margin: 0 auto;
    padding-top: 90px;
    padding-bottom: 40px;
}

/* TÍTULO PRINCIPAL */
.geramargem-title {
    font-family: 'Poppins', sans-serif !important;
    font-size: 42px !important;
    font-weight: 700 !important;
    color: #3D3D00 !important;
    margin-bottom: 12px;
}

/* TEXTOS */
p {
    color: #5A5A00;
}

/* INPUTS */
.stTextInput > div > div > input {
    background-color: #FFFFFF !important;
    color: #4C4C00 !important;
    border-radius: 6px !important;
    border: 1px solid #D6C97A !important;
    padding: 10px !important;
}

/* PLACEHOLDER */
.stTextInput > div > div > input::placeholder {
    color: #9E9E9E !important;
}

/* BOTÃO – AÇÃO PRINCIPAL */
.stButton > button {
    background-color:  #FFFFFF !important;  
    color: #4C4C00 !important;            
    padding: 12px 36px;
    border-radius: 6px;
    font-weight: 700;
    border: none;
    cursor: pointer;
}

/* HOVER */
.stButton > button:hover {
    background-color: #1F1F00 !important;
}

}

</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# ---------------- BANCO DE DADOS ----------------
if not os.path.exists("users.csv"):
    df = pd.DataFrame(columns=["nome", "email", "senha", "autorizado"])
    df.to_csv("users.csv", index=False)

df = pd.read_csv("users.csv")

# ---------------- FUNÇÃO DE VALIDAÇÃO DE SENHA ----------------
def senha_valida(senha):
    if len(senha) != 8:
        return False
    if not re.search(r"[A-Z]", senha):
        return False
    if not re.search(r"[a-z]", senha):
        return False
    if not re.search(r"[0-9]", senha):
        return False
    if not re.search(r"[^\w]", senha):
        return False
    return True

# ---------------- INTERFACE ----------------
st.markdown("<div class='content-area'>", unsafe_allow_html=True)

st.markdown("<h2 class='geramargem-title'>GeraMargem</h2>", unsafe_allow_html=True)
st.write("### Crie sua conta")
st.write("Preencha os dados e aguarde autorização do responsável.")

nome = st.text_input("Nome completo")
email = st.text_input("E-mail")
senha = st.text_input(
    "Senha (8 caracteres, incluindo maiúscula, minúscula, número e símbolo)",
    type="password"
)

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
