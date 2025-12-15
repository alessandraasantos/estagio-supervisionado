import streamlit as st
import pandas as pd
import re
import os

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="Recuperar senha",
    page_icon="🔑",
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
    padding-top: 100px;
    padding-bottom: 40px;
}

/* TÍTULO PRINCIPAL */
.page-title {
    font-family: 'Poppins', sans-serif !important;
    font-size: 34px !important;
    font-weight: 700 !important;
    color: #3D3D00 !important;
    margin-bottom: 10px;
}

/* DESCRIÇÃO */
.page-description {
    color: #5A5A00;
    font-size: 15px;
    margin-bottom: 28px;
}

/* INPUTS */
.stTextInput > div > div > input {
    background-color: #FFFDF5 !important;
    color: #3D3D00 !important;
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
    background-color: #FFFFFF !important;
    color: #4C4C00 !important;
    padding: 12px 36px;
    border-radius: 6px;
    font-weight: 700;
    border: none;
    cursor: pointer;
}

.stButton > button:hover {
    background-color: #1F1F00 !important;
    color: #FFFFFF !important;
}

/* LINK AUXILIAR */
.voltar {
    font-size: 14px;
    color: #1F1F00;
    text-decoration: underline;
    cursor: pointer;
}

</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------------- BANCO DE DADOS ----------------
if not os.path.exists("users.csv"):
    st.error("Base de usuários não encontrada.")
    st.stop()

df = pd.read_csv("users.csv")

# ---------------- FUNÇÃO DE VALIDAÇÃO ----------------
def senha_valida(s):
    return (
        len(s) == 8 and
        re.search(r"[A-Z]", s) and
        re.search(r"[a-z]", s) and
        re.search(r"[0-9]", s) and
        re.search(r"[\\W_]", s)
    )

# ---------------- INTERFACE ----------------
st.markdown("<div class='content-area'>", unsafe_allow_html=True)

st.markdown("<h2 class='page-title'>Recuperar senha</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='page-description'>Defina uma nova senha para continuar acessando o sistema.</p>",
    unsafe_allow_html=True
)

email = st.text_input("E-mail")
nova = st.text_input(
    "Nova senha (8 caracteres, incluindo letra maiúscula, minúscula, número e símbolo)",
    type="password"
)
confirmar = st.text_input("Confirmar nova senha", type="password")

if st.button("Redefinir senha"):
    if not email or not nova or not confirmar:
        st.error("Preencha todos os campos.")
    elif email not in df["email"].values:
        st.error("E-mail não encontrado.")
    elif nova != confirmar:
        st.error("As senhas não coincidem.")
    elif not senha_valida(nova):
        st.error("A senha não atende aos requisitos.")
    else:
        df.loc[df["email"] == email, "senha"] = nova
        df.to_csv("users.csv", index=False)
        st.success("Senha alterada com sucesso!")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<a href='login.py' class='voltar'>Voltar para o login</a>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
