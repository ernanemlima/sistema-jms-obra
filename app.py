import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

st.set_page_config(page_title="JMS Orçamentos", layout="centered")

# --- FUNÇÃO DO PDF ---
def gerar_pdf_completo(cliente, lista_itens, valor_total):
    pdf = FPDF()
    pdf.add_page()
    
    # Adicionando o Logo da JMS
    if os.path.exists("logo.jpg"):
        pdf.image("logo.jpg", 10, 8, 35)
        pdf.ln(25)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "ORÇAMENTO DE SERVIÇOS", ln=True, align='R')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Cliente: {cliente}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Cabeçalho da Tabela
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Item", border=1)
    pdf.cell(30, 10, "Qtd", border=1, align='C')
    pdf.cell(30, 10, "Unit.", border=1, align='C')
    pdf.cell(30, 10, "Total", border=1, align='C', ln=True)

    # Itens
    pdf.set_font("Arial", size=10)
    for i in lista_itens:
        pdf.cell(90, 10, i['item'], border=1)
        pdf.cell(30, 10, str(i['qtd']), border=1, align='C')
        pdf.cell(30, 10, f"R$ {i['unit']:.2f}", border=1, align='C')
        pdf.cell(30, 10, f"R$ {i['total']:.2f}", border=1, align='C', ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"TOTAL DO ORÇAMENTO: R$ {valor_total:.2f}", align='R', ln=True)
    
    nome_arquivo = f"Orcamento_{cliente}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
st.title("👷‍♂️ JMS - Gestão de Obras")

# Criar a lista de itens na memória se não existir
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

try:
    df_precos = pd.read_csv('precos.csv')
    nome_cliente = st.text_input("Nome do Cliente", "Cliente Exemplo")

    with st.container(border=True):
        st.subheader("Adicionar Item ao Orçamento")
        escolha = st.selectbox("Selecione o Material/Serviço", df_precos['item'])
        dados = df_precos[df_precos['item'] == escolha].iloc[0]
        
        qtd = st.number_input(f"Quantidade ({dados['unidade']})", min_value=0.1, step=1.0)
        subtotal = qtd * dados['preco_unitario']
        
        if st.button("➕ Adicionar Item"):
            st.session_state.carrinho.append({
                'item': escolha,
                'qtd': qtd,
                'unit': dados['preco_unitario'],
                'total': subtotal
            })
            st.toast(f"{escolha} adicionado!")

    # Exibir a lista atual
    if st.session_state.carrinho:
        st.divider()
        st.subheader("Resumo do Orçamento")
        df_carrinho = pd.DataFrame(st.session_state.carrinho)
        st.table(df_carrinho)
        
        valor_final = df_carrinho['total'].sum()
        st.header(f"Total: R$ {valor_final:.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpar Tudo"):
                st.session_state.carrinho = []
                st.rerun()
        with col2:
            if st.button("📄 Gerar Orçamento PDF"):
                arquivo = gerar_pdf_completo(nome_cliente, st.session_state.carrinho, valor_final)
                with open(arquivo, "rb") as f:
                    st.download_button("⬇️ Baixar PDF", f, file_name=arquivo)

except Exception as e:
    st.error(f"Erro: {e}")