import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Autenticação com Google Sheets via secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(credentials)

# Abre a planilha e a aba correta
spreadsheet = client.open_by_key("1RKk3kn8hkhjAQswgyhoMIlwVyHDSZAD72mF4BsRYAHs")
worksheet = spreadsheet.worksheet("Maio")

# Interface do app
st.title("Formulário de Campanha")

campanha = st.text_input("Campanha")
parts = campanha.split("_")
convenio = parts[0] if len(parts) > 0 else ""
produto = parts[2] if len(parts) > 2 else ""

plataforma = st.selectbox("Plataforma", ["Hyperflow", "Pontal", "Zenvia"])
ferramenta = st.selectbox("Ferramenta", ["RCS", "SMS", "Outro"])
quantidade = st.number_input("Quantidade", min_value=0, step=1)

# Define valor unitário
valor_unitario = 0.0
if ferramenta == 'RCS':
    valor_unitario = 0.105
elif ferramenta == 'SMS':
    if plataforma == 'Hyperflow':
        valor_unitario = 0.05
    elif plataforma in ['Zenvia', 'Pontal']:
        valor_unitario = 0.047

gasto = round(quantidade * valor_unitario, 2)

# Exibição
st.write(f"**Convênio detectado:** `{convenio}`")
st.write(f"**Produto detectado:** `{produto}`")
st.write(f"**Gasto calculado:** R$ {gasto}")

# Enviar
if st.button("Enviar para Google Sheets"):
    if campanha and ferramenta and plataforma:
        linha = [campanha, convenio, produto, plataforma, ferramenta, quantidade, gasto]
        worksheet.append_row(linha)
        st.success("Dados enviados com sucesso!")
    else:
        st.error("Preencha todos os campos obrigatórios.")
