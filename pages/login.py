import streamlit as st
import pandas as pd
import os

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="GeraMargem - Login",
    page_icon="🔐",
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
    background-color: #4C4C00 !important; /* MUDANÇA AQUI: de #2E2E00 para #4C4C00 */
    color: #FFFFFF !important;
    padding: 12px 36px;
    border-radius: 6px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    
}

.stButton > button:hover {
    background-color: #1F1F00 !important;
}

/* LINK AUXILIAR */
.recuperar {
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

# ---------------- INTERFACE ----------------
st.markdown("<div class='content-area'>", unsafe_allow_html=True)

st.markdown("<h2 class='geramargem-title'>GeraMargem</h2>", unsafe_allow_html=True)
st.write("### Acesse sua conta")
st.write("Informe seus dados para acessar o sistema.")

email = st.text_input("E-mail")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):
    if not email or not senha:
        st.error("Preencha todos os campos.")
    elif email not in df["email"].values:
        st.warning("E-mail não encontrado.")
    else:
        linha = df[df["email"] == email].iloc[0]

        if linha["autorizado"] != "sim":
            st.error("Seu acesso ainda não foi autorizado.")
        elif senha != linha["senha"]:
            st.error("Senha incorreta.")
        else:
            st.success("Login realizado com sucesso.")
            st.switch_page("app")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<a href='recuperar_senha.py' class='recuperar'>Esqueci minha senha</a>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
