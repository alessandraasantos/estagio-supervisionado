import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="GeraMargem - Login", page_icon="🔐")

# ---------- ESTILO DA PÁGINA ----------
page_bg = """
<style>
body {
    background-color: #FFE992 !important;
}

/* CONTAINER PRINCIPAL */
.login-card {
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
    color: #3D3D00;
}

p {
    color: #5A5A00;
}

/* INPUT */
.stTextInput>div>div>input {
    background-color: #FFF4BC !important;
    border-radius: 12px !important;
    border: 1px solid #E1D676 !important;
    padding: 10px !important;
}

/* BOTÃO */
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
    df = pd.DataFrame(columns=["email", "nome", "autorizado"])
    df.to_csv("users.csv", index=False)

df = pd.read_csv("users.csv")

# ---------- INTERFACE ----------
st.markdown("<div class='login-card'>", unsafe_allow_html=True)

st.markdown("## 🔸 GeraMargem")
st.write("### Seja bem-vindo!")
st.write("Insira seu e-mail autorizado para entrar:")

email = st.text_input("E-mail")

if st.button("Entrar"):
    if email in df["email"].values:
        autorizado = df.loc[df["email"] == email, "autorizado"].values[0]

        if autorizado == "sim":
            st.success("Acesso permitido! Redirecionando...")
            st.switch_page("app.py")

        else:
            st.error("Seu acesso ainda não foi autorizado pelo responsável.")

    else:
        st.warning("E-mail não encontrado! Vá para a página de cadastro.")

st.markdown("</div>", unsafe_allow_html=True)
