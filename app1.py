import streamlit as st
import yagmail
import os
import tempfile

# === Configuração inicial ===
st.set_page_config(page_title="Formulário de Reembolso", layout="wide")

st.title("Formulário de Reembolso de Despesas")
st.markdown("Preencha os dados abaixo e anexe os comprovantes (PDF).")

# === Campos do formulário ===
nome = st.text_input("Nome completo", max_chars=100)
email_solicitante = st.text_input("Seu e-mail")
descricao = st.text_area("Descrição das despesas", height=150, placeholder="Ex: Passagem, alimentação, hospedagem etc.")

comprovantes = st.file_uploader("Anexe os comprovantes (PDFs)", type="pdf", accept_multiple_files=True)

enviar = st.button("Enviar formulário")

# === Validação e envio ===
if enviar:
    if not nome or not email_solicitante or not descricao or not comprovantes:
        st.error("Preencha todos os campos e anexe pelo menos um comprovante.")
    else:
        with st.spinner("Enviando e-mail..."):

            # === Montar conteúdo do e-mail ===
            corpo_email = f"""
     Formulário de Reembolso enviado:

 ;Nome: {nome}
  E-mail: {email_solicitante}

    Descrição:
{descricao}
"""

            # === Configuração do yagmail (envio Gmail) ===
            remetente = "eduardo.cruzsilva1972@gmail.com"
            senha_app = "dahpbvrhxlvcyhyl"  # senha de app sem espaços
            destinatario = "laiscruzesilva510@gmail.com"

            # Criar cliente yagmail
            yag = yagmail.SMTP(user=remetente, password=senha_app)

            # Salvar os arquivos temporariamente para anexar
            arquivos_temp = []
            for arquivo in comprovantes:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(arquivo.read())
                    arquivos_temp.append(temp_file.name)

            try:
                # Enviar o e-mail
                yag.send(
                    to=destinatario,
                    subject="Novo formulário de reembolso recebido",
                    contents=corpo_email,
                    attachments=arquivos_temp
                )
                st.success("Formulário enviado com sucesso! Você receberá a confirmação por e-mail.")
            except Exception as e:
                st.error(f"Erro ao enviar o e-mail: {e}")
            finally:
                # Limpar os arquivos temporários
                for file_path in arquivos_temp:
                    os.remove(file_path)
