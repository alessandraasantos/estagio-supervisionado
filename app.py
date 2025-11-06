import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from docx import Document
from io import BytesIO
from datetime import datetime

# --- Configuração da página ---
st.set_page_config(page_title="Gerador de Declaração de Margem", page_icon="💼", layout="centered")

st.title("💼 Sistema de Geração de Declaração de Margem Consignável")
st.write("Preencha as informações abaixo ou selecione um nome para gerar automaticamente a declaração.")

# --- Conectar ao Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Link da planilha
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1jRpDiEc9kaEDNAGjjE-afu1pS9S9xk31L5kzxMoTxo4/edit?gid=0#gid=0").sheet1

# 👇 Importante: o cabeçalho começa na linha 2 da planilha
data = sheet.get_all_records(head=2)

# --- Interface amigável ---
nomes = [linha["NOME"] for linha in data]
nome_selecionado = st.selectbox("Selecione o nome do(a) aposentado(a)/pensionista:", nomes)

if nome_selecionado:
    pessoa = next((linha for linha in data if linha["NOME"] == nome_selecionado), None)
    if pessoa:
        # Conversão de valores numéricos (garantindo que vírgulas sejam tratadas)
        try:
            salario = float(str(pessoa["SALÁRIO"]).replace(".", "").replace(",", "."))
        except:
            salario = 0.0

        margem_total = salario * 0.3  # 30% do salário

        # Pegar valores dos consignados e somar apenas os que tiverem número > 0
        consignados = [
            pessoa.get("CONSIGNADO 1", 0),
            pessoa.get("CONSIGNADO 2", 0),
            pessoa.get("CONSIGNADO 3", 0),
            pessoa.get("CONSIGNADO 4", 0),
            pessoa.get("CONSIGNADO 5", 0),
        ]

        total_consignado = 0
        for c in consignados:
            try:
                valor = float(str(c).replace(".", "").replace(",", "."))
                total_consignado += valor
            except:
                continue

        # Se tiver empréstimo, subtrai; se não tiver, mantém o valor de 30%
        if total_consignado > 0:
            margem_livre = margem_total - total_consignado
            possui_emprestimo = True
        else:
            margem_livre = margem_total
            possui_emprestimo = False

        # --- Exibição dos resultados ---
        st.subheader("📊 Resumo dos Dados")
        st.write(f"**Matrícula:** {pessoa['MATRÍCULA']}")
        st.write(f"**CPF:** {pessoa['CPF']}")
        st.write(f"**Salário:** R$ {salario:,.2f}")
        st.write(f"**Margem Total (30%):** R$ {margem_total:,.2f}")

        if possui_emprestimo:
            st.warning("💰 Este(a) aposentado(a)/pensionista possui empréstimo(s) ativo(s).")
            st.write(f"**Total de Empréstimos:** R$ {total_consignado:,.2f}")
            st.write(f"**Margem Livre (após empréstimos):** R$ {margem_livre:,.2f}")
        else:
            st.info("✅ Este(a) aposentado(a)/pensionista **não possui empréstimos ativos.**")
            st.write(f"**Margem Livre:** R$ {margem_livre:,.2f}")

        # --- Geração do documento ---
        if st.button("📄 Gerar Declaração"):
            doc = Document("DECLARAÇÃO_DE_MARGEM_MODELO.docx")

            for p in doc.paragraphs:
                if "XXXX" in p.text:
                    p.text = p.text.replace("XXXX", pessoa["NOME"])
                if "CPF. N° XXXX" in p.text:
                    p.text = p.text.replace("CPF. N° XXXX", f"CPF Nº {pessoa['CPF']}")
                if "R$ XXXX" in p.text:
                    p.text = p.text.replace("R$ XXXX", f"R$ {salario:,.2f}")
                if "R$ XXXXX" in p.text:
                    p.text = p.text.replace("R$ XXXXX", f"R$ {total_consignado:,.2f}")
                if "R$ XXX" in p.text:
                    p.text = p.text.replace("R$ XXX", f"R$ {margem_livre:,.2f}")

                data_atual = datetime.now().strftime("%d de %B de %Y")
                if "DATA de MÊS de ANO" in p.text:
                    p.text = p.text.replace("DATA de MÊS de ANO", data_atual)

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.success("✅ Declaração gerada com sucesso!")
            st.download_button(
                label="⬇️ Baixar Declaração",
                data=buffer,
                file_name=f"Declaracao_{pessoa['NOME']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
