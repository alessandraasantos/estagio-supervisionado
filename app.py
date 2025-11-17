import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="GeraMargem - Cadastro", page_icon="📝")

# ---------- ESTILO ----------
page_bg = """
<style>
body {
    background-color: #FFE992 !important;
}

/* Card */
.cadastro-card {
    width: 520px;
    margin: auto;
    margin-top: 80px;
    background-color: #FFF4BC;
    padding: 40px 35px;
    border-radius: 18px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    text-align: center;
}

/* Títulos */
h2 {
    font-weight: 700;
    color: #3D3D00;
}

p {
    color: #5A5A00;
}

/* Inputs */
.stTextInput>div>div>input {
    background-color: #FFF4BC !important;
    border-radius: 12px !important;
    border: 1px solid #E1D676 !important;
    padding: 10px !important;
}

/* Botão */
.stButton>button {
    background-color: #3D3D00;
    color: white;
    padding: 10px 30px;
    border-radius: 20px;
    font-weight: bold;
    border: none;
    transition: 0.2s;
}

.stButton>button:hover {
    background-color: #1F1F00;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------- BANCO DE DADOS ----------
if not os.path.exists("users.csv"):
    df = pd.DataFrame(columns=["email", "nome", "senha", "autorizado"])
    df.to_csv("users.csv", index=False)

df = pd.read_csv("users.csv")

# ---------- INTERFACE ----------
st.markdown("<div class='cadastro-card'>", unsafe_allow_html=True)

st.markdown("## 🔸 GeraMargem – Cadastro")
st.write("Crie sua conta para solicitar autorização de acesso.")

nome = st.text_input("Nome completo")
email = st.text_input("E-mail")
senha = st.text_input("Senha (máx. 8 caracteres)", type="password")

# ---------- REGRAS DE SENHA ----------
def validar_senha(s):

    if len(s) > 8:
        return False

    regras = [
        r".*[A-Z].*",      # maiúscula
        r".*[a-z].*",      # minúscula
        r".*[0-9].*",      # número
        r".*[@$!%*#?&].*"  # caractere especial
    ]

    return all(re.match(regra, s) for regra in regras)


# ---------- BOTÃO ----------
if st.button("Cadastrar"):

    if nome.strip() == "" or email.strip() == "" or senha.strip() == "":
        st.error("Preencha todos os campos.")
    
    elif email in df["email"].values:
        st.warning("Este e-mail já está cadastrado! Aguarde autorização.")

    elif not validar_senha(senha):
        st.error("A senha deve ter no máximo 8 caracteres e conter: letra maiúscula, minúscula, número e caractere especial.")
    
    else:
        novo = pd.DataFrame([[email, nome, senha, "nao"]], 
                            columns=["email", "nome", "senha", "autorizado"])

        df = pd.concat([df, novo], ignore_index=True)
        df.to_csv("users.csv", index=False)

        st.success("Cadastro realizado! Aguarde autorização do responsável.")


st.markdown("</div>", unsafe_allow_html=True)
