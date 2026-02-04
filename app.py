import streamlit as st
import pandas as pd
import sqlite3
from fpdf import FPDF
import os

# --- INICIALIZAÇÃO DO BANCO DE DATAS ---
def conectar():
    return sqlite3.connect('jms_controle.db', check_same_thread=False)

def init_db():
    conn = conectar()
    c = conn.cursor()
    # Tabela de Clientes
    c.execute('''CREATE TABLE IF NOT EXISTS clientes 
                 (id INTEGER PRIMARY KEY, nome TEXT, whatsapp TEXT, endereco TEXT)''')
    # Tabela de Materiais/Preços (Substitui o antigo CSV)
    c.execute('''CREATE TABLE IF NOT EXISTS materiais 
                 (id INTEGER PRIMARY KEY, item TEXT, preco REAL, unidade TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- INTERFACE ---
st.set_page_config(page_title="JMS ERP", layout="wide")
st.title("👷‍♂️ JMS - Gestão de Obras Pro")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

tab_orc, tab_med, tab_cad, tab_rel = st.tabs(["📄 Orçamentos", "📏 Medição", "👥 Cadastros", "📊 Relatórios"])

# --- ABA: CADASTROS ---
with tab_cad:
    st.header("Cadastros")
    col_c, col_m = st.columns(2)
    
    with col_c:
        st.subheader("Novo Cliente")
        with st.form("cad_cliente", clear_on_submit=True):
            n = st.text_input("Nome")
            w = st.text_input("WhatsApp")
            e = st.text_input("Endereço")
            if st.form_submit_button("Salvar Cliente"):
                conn = conectar()
                conn.execute("INSERT INTO clientes (nome, whatsapp, endereco) VALUES (?,?,?)", (n, w, e))
                conn.commit()
                st.success("Cliente salvo!")

    with col_m:
        st.subheader("Tabela de Preços")
        with st.form("cad_material", clear_on_submit=True):
            item = st.text_input("Nome do Material/Serviço")
            pre = st.number_input("Preço Unitário (R$)", min_value=0.0)
            uni = st.selectbox("Unidade", ["m²", "m³", "Saco", "Milheiro", "Unid.", "Dia"])
            if st.form_submit_button("Atualizar Preço"):
                conn = conectar()
                conn.execute("INSERT INTO materiais (item, preco, unidade) VALUES (?,?,?)", (item, pre, uni))
                conn.commit()
                st.success("Preço atualizado!")

# --- ABA: MEDIÇÃO ---
with tab_med:
    st.header("Calculadora de Medição")
    st.write("Calcule a área e adicione diretamente ao orçamento.")
    
    c1, c2, c3 = st.columns(3)
    alt = c1.number_input("Altura (m)", min_value=0.0, step=0.01)
    larg = c2.number_input("Largura (m)", min_value=0.0, step=0.01)
    area = alt * larg
    c3.metric("Área Calculada", f"{area:.2f} m²")
    
    conn = conectar()
    lista_mat = pd.read_sql_query("SELECT * FROM materiais WHERE unidade = 'm²'", conn)
    
    if not lista_mat.empty:
        servico = st.selectbox("Aplicar qual serviço nesta área?", lista_mat['item'])
        if st.button("➕ Adicionar Medição ao Orçamento"):
            preco_un = lista_mat[lista_mat['item'] == servico]['preco'].values[0]
            st.session_state.carrinho.append({
                'item': f"{servico} (Medição: {alt}x{larg})",
                'qtd': area,
                'total': area * preco_un
            })
            st.success("Medição enviada para a aba de Orçamentos!")
    else:
        st.warning("Cadastre serviços com unidade 'm²' para usar a calculadora.")

# --- ABA: ORÇAMENTOS ---
with tab_orc:
    st.header("Novo Orçamento")
    conn = conectar()
    clientes = pd.read_sql_query("SELECT nome FROM clientes", conn)
    
    if not clientes.empty:
        cliente_sel = st.selectbox("Selecione o Cliente", clientes['nome'])
        
        # Seleção manual de itens (fora a medição)
        st.divider()
        todos_mat = pd.read_sql_query("SELECT * FROM materiais", conn)
        item_avulso = st.selectbox("Adicionar outro item manual", todos_mat['item'])
        qtd_avulsa = st.number_input("Quantidade", min_value=0.1)
        
        if st.button("➕ Adicionar Item Manual"):
            pre_avulso = todos_mat[todos_mat['item'] == item_avulso]['preco'].values[0]
            st.session_state.carrinho.append({
                'item': item_avulso, 'qtd': qtd_avulsa, 'total': qtd_avulsa * pre_avulso
            })

        # Resumo e PDF
        if st.session_state.carrinho:
            st.subheader("Itens do Orçamento")
            df_car = pd.DataFrame(st.session_state.carrinho)
            st.table(df_car)
            total_geral = df_car['total'].sum()
            st.write(f"### TOTAL: R$ {total_geral:.2f}")
            
            if st.button("🗑️ Limpar"):
                st.session_state.carrinho = []; st.rerun()
                
            if st.button("📄 Gerar PDF"):
                # (Aqui entra a sua função de PDF que já criamos antes)
                st.info("PDF Gerado com sucesso (Simulação)")
    else:
        st.error("Por favor, cadastre um cliente primeiro.")
