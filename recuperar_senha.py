import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Recuperar Senha", page_icon="🔑")

df = pd.read_csv("users.csv")

st.write("## Recuperação de Senha")

email = st.text_input("Digite seu e-mail")

nova = st.text_input("Nova senha (8 caracteres, incluindo letra maiúscula, minúscula, número e símbolo)", type="password")
confirmar = st.text_input("Confirmar nova senha", type="password")

def senha_valida(s):
    return (
        len(s) == 8 and
        re.search(r"[A-Z]", s) and
        re.search(r"[a-z]", s) and
        re.search(r"[0-9]", s) and
        re.search(r"[\\W_]", s)
    )

if st.button("Redefinir senha"):
    if email not in df["email"].values:
        st.error("E-mail não encontrado.")
    elif nova != confirmar:
        st.error("As senhas não coincidem.")
    elif not senha_valida(nova):
        st.error("A senha não atende aos requisitos.")
    else:
        df.loc[df["email"] == email, "senha"] = nova
        df.to_csv("users.csv", index=False)
        st.success("Senha alterada com sucesso!")
