import streamlit as st

st.set_page_config(page_title="GeraMargem - Cadastro", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
        body { background-color: #FFE992 !important; }
        .block-container { background-color: #FFE992; }
        .cad-box {
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
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='cad-box'>", unsafe_allow_html=True)

# ESQUERDA
st.markdown("""
<div class='left'>
    <div class='logo'>GeraMargem</div>
    <h2>Cadastro</h2>
    <p>Solicite seu acesso.<br>Será liberado somente pela supervisão.</p>
</div>
""", unsafe_allow_html=True)

# DIREITA
st.markdown("<div class='right'>", unsafe_allow_html=True)

st.markdown("### Criar solicitação de acesso")
nome = st.text_input("Nome completo")
email = st.text_input("E-mail corporativo")

if st.button("Solicitar Acesso", use_container_width=True):
    if nome.strip() == "" or email.strip() == "":
        st.error("Preencha todos os campos.")
    else:
        with open("solicitacoes.txt", "a") as f:
            f.write(f"{nome} - {email}\n")
        st.success("Solicitação enviada! Aguarde liberação da supervisão.")

st.markdown("</div></div>", unsafe_allow_html=True)
