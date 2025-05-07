import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

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
ferramenta = st.selectbox("Ferramenta", ["RCS", "SMS", "Whatsapp"])
quantidade_total = st.number_input("Quantidade", min_value=0, step=1)

quantidade_sms = 0
quantidade_rcs = quantidade_total

# Se a ferramenta for RCS, permitir digitar a quantidade de SMS
if ferramenta == "RCS":
    quantidade_sms = st.number_input("Quantidade de SMS (inclusa no total)", min_value=0, max_value=quantidade_total, step=1)
    quantidade_rcs = quantidade_total - quantidade_sms

# Define valor unitário
valor_unitario_rcs = 0.105
valor_unitario_sms = 0.05 if plataforma == 'Hyperflow' else 0.047
valor_unitario_whatsapp = 0.046

gasto_rcs = round(quantidade_rcs * valor_unitario_rcs, 2) if ferramenta == "RCS" else 0.0
gasto_sms = round(quantidade_sms * valor_unitario_sms, 2) if ferramenta == "RCS" else 0.0
gasto = round(quantidade_total * {
    "RCS": valor_unitario_rcs,
    "SMS": valor_unitario_sms,
    "Whatsapp": valor_unitario_whatsapp
}[ferramenta], 2)

# Exibição
st.write(f"**Convênio detectado:** `{convenio}`")
st.write(f"**Produto detectado:** `{produto}`")
st.write(f"**Gasto total estimado:** R$ {gasto}")
if ferramenta == "RCS":
    st.write(f"→ RCS: {quantidade_rcs} unidades | Gasto: R$ {gasto_rcs}")
    st.write(f"→ SMS: {quantidade_sms} unidades | Gasto: R$ {gasto_sms}")

# Data de hoje
data_hoje = date.today().strftime("%d/%m/%Y")
# Campo editável com data
data_hoje = st.date_input("Data da campanha", value=date.today())

# Formata como string dd/mm/yyyy
data_hoje = data_hoje.strftime("%d/%m/%Y")  # NÃO usar apóstrofo



# Enviar
if st.button("Enviar para Google Sheets"):
    if campanha and ferramenta and plataforma:
        if ferramenta == "RCS":
            # Adiciona RCS (ajustada)
            if quantidade_rcs > 0:
                linha_rcs = [campanha, data_hoje, convenio, produto, plataforma, "RCS", quantidade_rcs, gasto_rcs]
                worksheet.append_row(linha_rcs)
            # Adiciona SMS
            if quantidade_sms > 0:
                linha_sms = [campanha, data_hoje, convenio, produto, plataforma, "SMS", quantidade_sms, gasto_sms]
                worksheet.append_row(linha_sms)
        else:
            # Caso SMS ou Whatsapp
            linha = [campanha, data_hoje, convenio, produto, plataforma, ferramenta, quantidade_total, gasto]
            worksheet.append_row(linha)

        st.success("Dados enviados com sucesso!")
    else:
        st.error("Preencha todos os campos obrigatórios.")
