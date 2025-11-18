import streamlit as st 
import pandas as pd
import os

st.set_page_config(page_title="GeraMargem - Login", page_icon="🔐")

# ---------- ESTILO ----------
page_bg = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap');

/* REMOVE HEADER PADRÃO */
header, .stApp > header {
    display: none !important;
}

/* REMOVE CONTAINERS PADRÕES */
.block-container {
    background: transparent !important;
    box-shadow: none !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* FUNDO IGUAL AO CADASTRO */
html, body, .main, .block-container {
    background-color: #FFE135 !important;
}

/* TÍTULO PADRONIZADO */
.geramargem-title {
    font-family: 'Poppins', sans-serif !important;
    font-size: 43px !important;
    font-weight: 700 !important;
    color: #3D3D00 !important;
}

/* TEXTOS */
h2, h3, h4 {
    color: #3D3D00 !important;
    font-weight: bold;
}

p {
    color: #5A5A00 !important;
}

/* INPUT IGUAL AO CADASTRO */
.stTextInput>div>div>input {
    background-color: #FBEC5D !important;
    border-radius: 12px !important;
    border: 1px solid #E1D676 !important;
    padding: 10px !important;
}

/* BOTÃO IGUAL AO CADASTRO */
.stButton>button {
    background-color: #FBEC5D !important;
    color: white !important;
    padding: 10px 30px !important;
    border-radius: 20px !important;
    font-weight: bold !important;
    border: none !important;
    transition: 0.2s !important;
}

.stButton>button:hover {
    background-color: #1F1F00 !important;
}

/* LINK DE RECUPERAÇÃO */
.recuperar {
    font-size: 14px !important;
    color: #1F1F00 !important;
    text-decoration: underline !important;
    cursor: pointer !important;
}

</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------- BANCO ----------
df = pd.read_csv("users.csv")

# ---------- UI ----------
st.markdown("<h2 class='geramargem-title'>GeraMargem</h2>", unsafe_allow_html=True)

st.write("### Acesse sua conta")

email = st.text_input("E-mail")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):
    if email in df["email"].values:
        linha = df[df["email"] == email].iloc[0]

        if linha["autorizado"] != "sim":
            st.error("Seu acesso ainda não foi autorizado.")
        elif senha != linha["senha"]:
            st.error("Senha incorreta.")
        else:
            st.success("Login realizado!")
            st.switch_page("app.py")
    else:
        st.warning("E-mail não encontrado.")

# LINK PARA RECUPERAÇÃO
st.markdown("<br><a href='recuperar_senha.py' class='recuperar'>Esqueci minha senha</a>", unsafe_allow_html=True)
