# app.py - Gerador de Declaração de Margem (versão final com detalhes de consignados)
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from docx import Document
from io import BytesIO
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from num2words import num2words
import unicodedata
import re

# --- Configuração da página ---
st.set_page_config(page_title="Gerador de Declaração de Margem", page_icon="💼", layout="centered")
st.title("💼 Sistema de Geração de Declaração de Margem Consignável")
st.write("Selecione um nome para gerar automaticamente a declaração.")

# --- Helpers ---
def normalize_header(s: str) -> str:
    """Normaliza cabeçalhos: remove acento, espaços extras e deixa em maiúsculas."""
    if s is None:
        return ""
    s = str(s).strip().upper()
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    s = " ".join(s.split())
    return s

def parse_decimal(value) -> Decimal:
    """
    Converte várias formas de entrada em Decimal:
    - números (int/float/Decimal)
    - strings '1.973,46', '1973,46', '1,973.46', 'R$ 1.973,46', ''
    Retorna Decimal com 2 casas (quantize).
    """
    if value is None:
        return Decimal("0.00")
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if isinstance(value, int):
        return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if isinstance(value, float):
        # converte float para string para evitar problemas binários
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    s = str(value).strip()
    if s == "":
        return Decimal("0.00")

    # remove símbolo R$, espaços e NBSP
    s = s.replace("R$", "").replace("r$", "")
    s = s.replace("\u00A0", "").replace(" ", "")

    if "." in s and "," in s:
        last_dot = s.rfind(".")
        last_comma = s.rfind(",")
        if last_comma > last_dot:
            # BR format: 1.973,46
            s = s.replace(".", "")
            s = s.replace(",", ".")
        else:
            # US format: 1,973.46 -> remove commas
            s = s.replace(",", "")
    else:
        if "," in s and "." not in s:
            s = s.replace(",", ".")
        # else: keep

    filtered = "".join(ch for ch in s if ch.isdigit() or ch in ".-+")
    if filtered in ("", ".", "-", "+"):
        return Decimal("0.00")
    try:
        d = Decimal(filtered)
    except InvalidOperation:
        return Decimal("0.00")
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def extenso_brl(valor: Decimal) -> str:
    """Converte Decimal para extenso em pt_BR."""
    valor = Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sinal = ""
    if valor < 0:
        sinal = "menos "
        valor = abs(valor)
    inteiro = int(valor)
    centavos = int((valor - Decimal(inteiro)) * 100)
    if inteiro == 0 and centavos == 0:
        return "zero reais"
    if centavos:
        texto = f"{num2words(inteiro, lang='pt_BR')} reais e {num2words(centavos, lang='pt_BR')} centavos"
    else:
        texto = f"{num2words(inteiro, lang='pt_BR')} reais"
    texto = re.sub(r"\s+", " ", texto).strip()
    return f"{sinal}{texto}"

def format_brl(valor: Decimal) -> str:
    """Formata Decimal para 'R$ 1.234,56'."""
    q = Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    s = f"{q:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

def _create_runs_with_bold_tags(paragraph, text_with_tags: str):
    """
    Insere no parágrafo texto interpretando tags <b>...</b> para runs em negrito.
    """
    parts = re.split(r'(<b>.*?<\/b>)', text_with_tags)
    for part in parts:
        if not part:
            continue
        m = re.match(r'^<b>(.*?)</b>$', part)
        if m:
            paragraph.add_run(m.group(1)).bold = True
        else:
            paragraph.add_run(part)

def replace_in_doc(doc: Document, subs: dict):
    """Substitui placeholders no docx (parágrafos + tabelas). Mantém quebras de linha '\n'.
       Interpreta tags <b>...</b> dentro dos valores para aplicar negrito apenas a partes específicas.
       Correção: sempre recria o parágrafo/célula inteiro quando houver substituição, evitando que
       placeholders divididos entre runs fiquem sem ser substituídos.
    """
    # parágrafos
    for p in doc.paragraphs:
        if not p.text:
            continue
        p_text = p.text
        replaced_any = False
        for chave, valor in subs.items():
            if chave in p_text:
                p_text = p_text.replace(chave, str(valor))
                replaced_any = True
        if replaced_any and p_text != p.text:
            # Limpa todos os runs e recria o parágrafo a partir do p_text,
            # interpretando tags <b>...</b> para aplicar negrito onde indicado.
            for _ in range(len(p.runs)):
                p.runs[0]._element.getparent().remove(p.runs[0]._element)
            _create_runs_with_bold_tags(p, p_text)

    # tabelas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                cell_text = cell.text
                replaced_any = False
                for chave, valor in subs.items():
                    if chave in cell_text:
                        cell_text = cell_text.replace(chave, str(valor))
                        replaced_any = True
                if replaced_any and cell_text != cell.text:
                    # limpar e inserir novo parágrafo(s) (irá inserir o texto com eventuais '\n')
                    cell._tc.clear_content()
                    # se houver quebras de linha, criar vários parágrafos dentro da célula
                    if "\n" in cell_text:
                        for line in cell_text.split("\n"):
                            p_new = cell.add_paragraph()
                            if "<b>" in line and "</b>" in line:
                                _create_runs_with_bold_tags(p_new, line)
                            else:
                                p_new.add_run(line)
                    else:
                        p_new = cell.add_paragraph()
                        if "<b>" in cell_text and "</b>" in cell_text:
                            _create_runs_with_bold_tags(p_new, cell_text)
                        else:
                            p_new.add_run(cell_text)


def remove_comprometida_clause_if_no_consignados(doc: Document):
    """
    Remove a cláusula fixa do template quando não houver consignados:
    ', com margem comprometida no valor de R$ {{CONSIGNADOS_LISTA}}, restando uma margem livre de R$ {{MARGEM_LIVRE_NUM}} ({{MARGEM_LIVRE_EXT}})'
    Será substituída por '.' (ponto), preservando o restante.
    """
    target = ", com margem comprometida no valor de R$ {{CONSIGNADOS_LISTA}}, restando uma margem livre de R$ {{MARGEM_LIVRE_NUM}} ({{MARGEM_LIVRE_EXT}})"
    # parágrafos
    for p in doc.paragraphs:
        if target in p.text:
            new_text = p.text.replace(target, ".")
            # recriar runs com novo texto (sem tags de negrito neste caso)
            for _ in range(len(p.runs)):
                p.runs[0]._element.getparent().remove(p.runs[0]._element)
            p.add_run(new_text)
    # tabelas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if target in cell.text:
                    new_text = cell.text.replace(target, ".")
                    cell._tc.clear_content()
                    cell.add_paragraph(new_text)

# --- Conexão com Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1jRpDiEc9kaEDNAGjjE-afu1pS9S9xk31L5kzxMoTxo4/edit?gid=0"
).sheet1

# Cabeçalho está na linha 2 (conforme sua planilha)
raw_records = sheet.get_all_records(head=2)

if not raw_records:
    st.error("A planilha não retornou registros. Verifique o head/linha de cabeçalho.")
    st.stop()

# --- Mapear cabeçalhos normalizados para nomes originais ---
header_map = {}
header_row = sheet.row_values(2)
for h in header_row:
    header_map[normalize_header(h)] = h

def get_field(record, desired_name):
    """Puxa campo do registro por nome desejado (flexível com acentos/variações)."""
    key = header_map.get(normalize_header(desired_name))
    if key and key in record:
        return record.get(key)
    for k in record.keys():
        if normalize_header(k) == normalize_header(desired_name):
            return record.get(k)
    return None

# --- Lista de nomes para o selectbox ---
nomes = [get_field(r, "NOME") for r in raw_records]
nomes = [n for n in nomes if n is not None and str(n).strip() != ""]

nome_selecionado = st.selectbox("Selecione o nome:", nomes)

if nome_selecionado:
    # localizar o registro exato (comparação por string limpa)
    pessoa = next((r for r in raw_records if str(get_field(r, "NOME")).strip() == str(nome_selecionado).strip()), None)

    if not pessoa:
        st.error("Não foi possível localizar a pessoa selecionada.")
    else:
        # SALÁRIO (tenta variações)
        raw_salario = get_field(pessoa, "SALÁRIO") or get_field(pessoa, "REMUNERAÇÃO") or get_field(pessoa, "SALARIO")
        salario = parse_decimal(raw_salario)

        # Se a planilha já tem coluna 'MARGEM 30%' preenchida, usar; senão calcular 30% do salário
        raw_margem30 = get_field(pessoa, "MARGEM 30%") or get_field(pessoa, "MARGEM30%") or get_field(pessoa, "MARGEM30")
        if raw_margem30 not in (None, ""):
            margem_total = parse_decimal(raw_margem30)
        else:
            margem_total = (salario * Decimal("0.30")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Vínculo (normalizar para documento)
        vinculo_raw = get_field(pessoa, "VÍNCULO") or get_field(pessoa, "VINCULO") or ""
        vinculo = str(vinculo_raw).strip()
        vinculo_upper = vinculo.upper()
        if "APOSEN" in vinculo_upper or "APOSENT" in vinculo_upper:
            vinculo_doc = "APOSENTADA"
        elif "PENSION" in vinculo_upper or "PENSIONISTA" in vinculo_upper:
            vinculo_doc = "PENSIONISTA"
        else:
            vinculo_doc = vinculo if vinculo else "---"

        # Matrícula e CPF
        matricula = get_field(pessoa, "MATRÍCULA") or get_field(pessoa, "MATRICULA") or "---"
        cpf = get_field(pessoa, "CPF") or "---"

        # Ler consignados desta pessoa (somente colunas CONSIGNADO 1..5 conforme indicado)
        consignados_vals = []
        possiveis = ["CONSIGNADO 1", "CONSIGNADO1", "CONSIGNADO 2", "CONSIGNADO2",
                     "CONSIGNADO 3", "CONSIGNADO3", "CONSIGNADO 4", "CONSIGNADO4",
                     "CONSIGNADO 5", "CONSIGNADO5", "EMPRÉSTIMO 1", "EMPRESTIMO1",
                     "EMPRÉSTIMO 2", "EMPRESTIMO2", "EMPRÉSTIMO 3", "EMPRESTIMO3",
                     "EMPRÉSTIMO 4", "EMPRESTIMO4", "EMPRÉSTIMO 5", "EMPRESTIMO5"]
        for nome_col in possiveis:
            v = get_field(pessoa, nome_col)
            if v is None or (isinstance(v, str) and v.strip() == ""):
                continue
            d = parse_decimal(v)
            if d != Decimal("0.00"):
                consignados_vals.append(d)

        # Também tenta colunas genéricas 'CONSIGNADO' caso haja apenas uma
        if not consignados_vals:
            single = get_field(pessoa, "CONSIGNADO") or get_field(pessoa, "EMPRESTIMO")
            if single not in (None, ""):
                d = parse_decimal(single)
                if d != Decimal("0.00"):
                    consignados_vals.append(d)

        # Soma dos consignados (mantemos essa soma para cálculo da margem livre e aviso)
        margem_comprometida = sum(consignados_vals, Decimal("0.00")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        margem_livre = (margem_total - margem_comprometida).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Preparar placeholders individuais detalhados dos consignados:
        # - CONSIGNADO1_NUM ... CONSIGNADO5_EXT (esses podem ser usados no modelo se desejar)
        consignado_placeholders = {}
        for i in range(1, 6):
            if i <= len(consignados_vals):
                val = consignados_vals[i-1]
                # agora guardamos APENAS o número sem "R$ " porque o template já tem "R$ " antes do placeholder
                num_sem_rs = format_brl(val).replace("R$ ", "").strip()
                consignado_placeholders[f"{{{{CONSIGNADO{i}_NUM}}}}"] = num_sem_rs
                consignado_placeholders[f"{{{{CONSIGNADO{i}_EXT}}}}"] = extenso_brl(val)
            else:
                consignado_placeholders[f"{{{{CONSIGNADO{i}_NUM}}}}"] = ""
                consignado_placeholders[f"{{{{CONSIGNADO{i}_EXT}}}}"] = ""

        # --- TODOS OS EMPRÉSTIMOS NA MESMA LINHA (separados por vírgula) ---
        # Observação: o template já inclui 'R$ ' antes de {{CONSIGNADOS_LISTA}}, logo
        # aqui geramos apenas '150,00 (cento e cinquenta reais), 90,50 (noventa ...)'
        if consignados_vals:
            partes = []
            partes_num_sem_tag = []  # lista apenas numérica (sem tags) caso queira usar
            partes_extenso = []
            for v in consignados_vals:
                num_text_full = format_brl(v)     # ex: 'R$ 150,00'
                num_sem_rs = num_text_full.replace("R$ ", "").strip()  # '150,00'
                ext_text = extenso_brl(v)         # ex: 'cento e cinquenta reais'
                # marcamos o numérico para ser renderizado em negrito no replace_in_doc
                partes.append(f"<b>{num_sem_rs}</b> ({ext_text})")
                partes_num_sem_tag.append(num_sem_rs)
                partes_extenso.append(ext_text)
            consignados_lista_text = ", ".join(partes)  # contém tags <b>...</b> para o replace
            consignados_lista_num_only = ", ".join(partes_num_sem_tag)  # sem tags
            consignados_lista_ext_only = ", ".join(partes_extenso)
        else:
            consignados_lista_text = ""
            consignados_lista_num_only = ""
            consignados_lista_ext_only = ""

        # Mostrar resumo
        st.subheader("📊 Resumo (confira os valores)")
        st.write(f"**Nome:** {nome_selecionado}")
        st.write(f"**Vínculo:** {vinculo_doc}")
        st.write(f"**Matrícula:** {matricula}")
        st.write(f"**CPF:** {cpf}")
        st.write(f"**Salário (num):** {format_brl(salario)}")
        st.write(f"**Salário (extenso):** {extenso_brl(salario)}")
        st.write(f"**Margem Total (30%):** {format_brl(margem_total)} ({extenso_brl(margem_total)})")
        st.write(f"**Margem Comprometida (soma consignados):** {format_brl(margem_comprometida)} ({extenso_brl(margem_comprometida)})")
        st.write(f"**Margem Livre (total - comprometida):** {format_brl(margem_livre)} ({extenso_brl(margem_livre)})")

        if margem_comprometida > margem_total:
            st.warning("⚠️ A margem comprometida é maior que a margem total de 30% — o valor livre ficou negativo.")

        # Botão de gerar Documento
        if st.button("📄 Gerar Declaração"):
            modelo = "DECLARAÇÃO_DE_MARGEM_MODELO.docx"
            
            try:
                doc = Document(modelo)
            except Exception as e:
                st.error(f"Não foi possível abrir o modelo '{modelo}': {e}")
                st.stop()

            # Se não houver consignados, removemos do documento a cláusula inteira
            if not consignados_vals:
                remove_comprometida_clause_if_no_consignados(doc)

            # data em pt-BR curta no formato: '10 de novembro de 2025'
            meses_pt = {
                1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
                7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
            }
            hoje = datetime.now()
            data_pt = f"{hoje.day} de {meses_pt[hoje.month]} de {hoje.year}"

            # Preparar substituições — NOTA: NÃO incluí "R$ " nas strings numéricas porque o template já tem "R$ "
            substituicoes = {
                "{{NOME}}": str(nome_selecionado),
                "{{CPF}}": str(cpf),
                "{{MATRICULA}}": str(matricula),
                "{{VINCULO}}": str(vinculo_doc),
                # como o template contém 'R$ {{SALARIO_NUM}}', aqui colocamos apenas o número sem 'R$ '
                "{{SALARIO_NUM}}": f"<b>{format_brl(salario).replace('R$ ', '').strip()}</b>",
                "{{SALARIO_EXT}}": extenso_brl(salario),
                "{{MARGEM_TOTAL_NUM}}": f"<b>{format_brl(margem_total).replace('R$ ', '').strip()}</b>",
                "{{MARGEM_TOTAL_EXT}}": extenso_brl(margem_total),
                # consignados lista (note: template já possui 'R$ ' antes do placeholder)
                "{{CONSIGNADOS_LISTA}}": consignados_lista_text,
                "{{CONSIGNADOS_LISTA_NUM_ONLY}}": consignados_lista_num_only,
                "{{CONSIGNADOS_LISTA_EXT_ONLY}}": consignados_lista_ext_only,
                # margem livre (template já tem 'R$ ' antes do placeholder)
                "{{MARGEM_LIVRE_NUM}}": f"<b>{format_brl(margem_livre).replace('R$ ', '').strip()}</b>",
                "{{MARGEM_LIVRE_EXT}}": extenso_brl(margem_livre),
                "{{DATA}}": data_pt
            }

            # adicionar placeholders individuais CONSIGNADO1..5 (sem 'R$ ')
            substituicoes.update(consignado_placeholders)

            # Aplica substituições no documento
            replace_in_doc(doc, substituicoes)

            # salva em buffer e oferece download
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            safe_name = re.sub(r"[^A-Za-z0-9 _-]", "", str(nome_selecionado))
            file_name = f"Declaracao_{safe_name}.docx"

            st.success("✅ Declaração gerada com sucesso!")
            st.download_button(
                "⬇️ Baixar declaração",
                data=buffer,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
