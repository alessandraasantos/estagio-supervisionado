import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from docx import Document
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Gerador de Declaração de Margem", page_icon="💼", layout="centered")

st.title("Sistema de Geração de Declaração de Margem Consignável")
st.write("Preencha as informações abaixo ou selecione um nome para gerar automaticamente a declaração.")

# --- Conectar ao Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1jRpDiEc9kaEDNAGjjE-afu1pS9S9xk31L5kzxMoTxo4/edit?gid=0#gid=0").sheet1
data = sheet.get_all_records()

# --- Interface amigável ---
nomes = [linha["NOME"] for linha in data]
nome_selecionado = st.selectbox("Selecione o nome do(a) aposentado(a)/pensionista:", nomes)

if nome_selecionado:
    pessoa = next((linha for linha in data if linha["NOME"] == nome_selecionado), None)
    if pessoa:
        salario = float(pessoa["SALÁRIO"])
        margem_total = salario * 0.3
        margem_comprometida = float(pessoa["MARGEM COMPROMETIDA"])
        margem_livre = margem_total - margem_comprometida

        st.subheader("Resumo dos dados")
        st.write(f"**Matrícula:** {pessoa['MATRÍCULA']}")
        st.write(f"**CPF:** {pessoa['CPF']}")
        st.write(f"**Salário:** R$ {salario:,.2f}")
        st.write(f"**Margem Total (30%):** R$ {margem_total:,.2f}")
        st.write(f"**Margem Comprometida:** R$ {margem_comprometida:,.2f}")
        st.write(f"**Margem Livre:** R$ {margem_livre:,.2f}")

        if st.button("Gerar Declaração"):
            doc = Document("DECLARAÇÃO_DE_MARGEM_MODELO.docx")

            # Substituir os campos do modelo
            for p in doc.paragraphs:
                if "XXXX" in p.text:
                    p.text = p.text.replace("XXXX", pessoa["NOME"])
                if "CPF. N° XXXX" in p.text:
                    p.text = p.text.replace("CPF. N° XXXX", f"CPF Nº {pessoa['CPF']}")
                if "R$ XXXX" in p.text:
                    p.text = p.text.replace("R$ XXXX", f"R$ {salario:,.2f}")
                if "R$ XXXXX" in p.text:
                    p.text = p.text.replace("R$ XXXXX", f"R$ {margem_comprometida:,.2f}")
                if "R$ XXX" in p.text:
                    p.text = p.text.replace("R$ XXX", f"R$ {margem_livre:,.2f}")

            data_atual = datetime.now().strftime("%d de %B de %Y")
            for p in doc.paragraphs:
                if "DATA de MÊS de ANO" in p.text:
                    p.text = p.text.replace("DATA de MÊS de ANO", data_atual)

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.success("Declaração gerada com sucesso!")
            st.download_button(
                label="Baixar Declaração",
                data=buffer,
                file_name=f"Declaracao_{pessoa['NOME']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
