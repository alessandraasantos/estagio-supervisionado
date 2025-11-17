import json
import os

arquivo = "autorizados.json"

def carregar():
    if not os.path.exists(arquivo):
        with open(arquivo, "w") as f:
            json.dump({"pendentes": [], "autorizados": []}, f)

    with open(arquivo, "r") as f:
        return json.load(f)

def salvar(dados):
    with open(arquivo, "w") as f:
        json.dump(dados, f, indent=4)

def adicionar_pendente(email):
    dados = carregar()
    if email not in dados["pendentes"]:
        dados["pendentes"].append(email)
        salvar(dados)

def aprovar_usuario(email):
    dados = carregar()
    if email in dados["pendentes"]:
        dados["pendentes"].remove(email)
        dados["autorizados"].append(email)
        salvar(dados)

def verificar_autorizado(email):
    dados = carregar()
    return email in dados["autorizados"]
