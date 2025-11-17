import streamlit as st
import os

st.set_page_config(page_title="GeraMargem - Login", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
        body { background-color: #FFE992 !important; }
        .block-container { background-color: #FFE992; }
        .login-box {
            width: 850px;
            margin: auto;
            margin-top: 60px;
            background-color: #FFF4BC;
            border-radius: 15px;
            padding: 0;
            display: flex;
            box-shadow: 1px 3px 12px rgba(0,0,0,0.2);
        }
        .left {
            background-color: #232306;
            color: white;
            width: 40%;
            padding: 50px 30px;
            border-radius: 15px 0 0 15px;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 30px;
        }
        .right {
            width: 60%;
            padding: 50px;
        }
        input {
            border-radius: 12px !important;
            background-color: #DFBE2D !important;
            color: black !important;
        }
        .enter-btn {
            border-radius: 12px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# ---- LAYOUT ----
st.markdown("<div class='login-box'>", unsafe_allow_html=True)

# ESQUERDA
st.markdown("""
<div class='left'>
    <div class='logo'>GeraMargem</div>
    <h2>Seja bem vindo!</h2>
    <p>Acesse sua conta autorizada.</p>
</div>
""", unsafe_allow_html=True)

# DIREITA
st.markdown("<div class='right'>", unsafe_allow_html=True)

st.markdown("### Login")
st.markdown("Digite seu e-mail autorizado:")

email = st.text_input("E-mail")

# --- VALIDAR ACESSO ---
if st.button("Entrar", use_container_width=True):
    if os.path.exists("authorized_emails.txt"):
        with open("authorized_emails.txt", "r") as file:
            authorized = [line.strip() for line in file.readlines()]

        if email in authorized:
            st.success("Acesso autorizado! Redirecionando...")
            st.switch_page("app.py")     # 👉 vai para sua tela principal
        else:
            st.error("E-mail não autorizado. Solicite liberação ao responsável.")
    else:
        st.error("Arquivo de autorização não encontrado.")

st.markdown("</div></div>", unsafe_allow_html=True)
