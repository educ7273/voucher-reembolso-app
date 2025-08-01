#Streamlit é um frame do py para conversar com GitHub, pd para ler os arquivos em pdf e data para registrar o documento
#Para funcionar o codigo precisa abrir o prompt é colocar o endereço onde foi criado: cd"C:XX\XXX\XXX\XX" e depois streamlit run app.py 
#FPDF serve para gerar o arquivo em pdf e o 'os' para atuar em diversos sistemas operacionais, smtblib é a biblioteca para o e-mail

import streamlit as st
from fpdf import FPDF
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Defini o campo para Título usando streamlit
st.set_page_config(page_title="Formulário de Reembolso", layout="centered")
st.title("Voucher - Reembolso de Despesas")
 # Definindo as linhas tracejadas para divisão de assuntos
st.markdown(
    """
    <style>.dashed-line{

        border-top:2px dashed #aaa;
        margin-top: 10px;
        margin-bottom: 10px;
        }
    <style>
    """,
    unsafe_allow_html=True,
    )
    
 #Campo para definir os Dados do Solicitante
st.subheader("Dados do Polo")
razao_social = st.text_input("Razão Social")
cnpj = st.text_input("CNPJ")
banco = st.text_input("Banco")
numero_banco = st.text_input("Numero_Banco")
agencia = st.text_input("Agência")
conta = st.text_input("Conta")

# Esse campo é para informar o Módulo que se refere a prestação de serviços
st.subheader("Informações do Evento")
evento = st.text_input("Nome do evento")
data_evento = st.date_input("Data do evento")
local = st.text_input("Local")

# Criei a variável para armazenar Despesas (várias linhas) em uma lista, sendo possivel utilizar 6 linhas, 
#se houver a necessidade de mais linhas alterar o range (1, 10)
st.subheader("Despesas Reembolsáveis")
linhas_despesas = []
for i in range(1, 6):
    st.markdown(f"**Despesa {i}**")
    descricao = st.text_input(f"Descrição da despesa {i}", key=f"desc_{i}")
    valor = st.number_input(f"Valor da despesa {i}", min_value=0.0, format="%.2f", key=f"valor_{i}")
    linhas_despesas.append((descricao, valor))

#Defini o campo para anexar os comprovantes, sendo aceitavel apenas 4 extensão
st.subheader("Comprovantes (PDF ou Imagem)")
comprovantes = st.file_uploader("Envie seus comprovantes (PDF, PNG ou JPG)", accept_multiple_files=True, type=["pdf", "png", "jpg", "jpeg"])

# Defini o campo para o botão de  Enviar
enviar = st.button("Enviar Solicitação")
# Campo obrigatorio para o CPF
if enviar:
    if not razao_social or not cnpj or not evento:
        st.error("Por favor, preencha todos os campos obrigatórios (nome, CPF e evento).")
    else:
        # Aqui foi criado para o arquivo em PDF, porém agora preciso alterar para o excel, pois o layout precisa ficar igual o usual
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Aqui você faz a definição do cabeçalho do seu PDF
        pdf.cell(200, 10, txt="Solicitação de Reembolso", ln=True, align="C")
        pdf.ln(10),
        st.markdown("---") # Definindo as linhas tracejadas para divisão de assuntos

        # Dados Pessoais
        pdf.cell(200, 10, txt=f"Razao_social: {razao_social}", ln=True)
        pdf.cell(200, 10, txt=f"CNPJ: {cnpj}", ln=True)
        pdf.cell(200, 10, txt=f"Banco: {banco} Numero_Banco: {numero_banco} Agência: {agencia}  Conta: {conta}", ln=True)
        pdf.ln(6)
        st.markdown("---") # Definindo as linhas tracejadas para divisão de assuntos

        # Evento
        pdf.cell(200, 10, txt=f"Evento: {evento}", ln=True)
        pdf.cell(200, 10, txt=f"Data: {data_evento.strftime('%d/%m/%Y')}", ln=True)
        pdf.cell(200, 10, txt=f"Local: {local}", ln=True)
        pdf.ln(5)
        st.markdown("---") # Definindo as linhas tracejadas para divisão de assuntos

        # Despesas
        pdf.cell(200, 10, txt="Despesas:", ln=True)
        total = 0
        for i, (desc, val) in enumerate(linhas_despesas, start=1):
            if desc and val > 0:
                pdf.cell(200, 10, txt=f"{i}. {desc} - R$ {val:.2f}", ln=True)
                total += val
        pdf.cell(200, 10, txt=f"Total: R$ {total:.2f}", ln=True)
        st.markdown("---") # Definindo as linhas tracejadas para divisão de assuntos

        # Nesse argumento serve para salvar PDF
        pasta_saida = "envios"
        os.makedirs(pasta_saida, exist_ok=True)
        data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{pasta_saida}/reembolso_{razao_social.replace(' ', '_')}_{data_str}.pdf"
        pdf.output(nome_arquivo)
         # Aqui você vai definir o e-mail que receberá o formulario para preencher
        try:
            remetente = "eduardo.cruzsilva1972@gmail.com"
            destinatario = "lucasneves@unimar.br"  

            msg = EmailMessage()
            msg["Subject"] = "Nova Solicitação de Reembolso"
            msg["From"] = remetente
            msg["To"] = destinatario
            msg.set_content(f"Olá,\n\nUma nova solicitação de reembolso foi enviada por {razao_social}.\n\nTotal: R$ {total:.2f}\n\nEm anexo, o PDF com os dados e comprovantes.\n")

            with open(nome_arquivo, "rb") as f:
                pdf_data = f.read()
                msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename=os.path.basename(nome_arquivo))

            # Defini o campo para incluir os comprovantes adicionais Drag and Drop
            for comp in comprovantes:
                comp_data = comp.read()
                tipo = comp.type.split("/")[-1]
                msg.add_attachment(comp_data, maintype="application", subtype=tipo, filename=comp.name)

            # Classificação Login e envio
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(remetente, "dahp bvrh xlvc yhyl")
                smtp.send_message(msg)

            st.success("Solicitação enviada com sucesso!")

        except Exception as e:
            st.error(f"Erro ao enviar e-mail: {e}")