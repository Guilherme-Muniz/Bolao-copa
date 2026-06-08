import streamlit as st
from config import ADMIN_EMAIL
from database.connection import inicializar_banco
from database.queries import buscar_usuario_por_email, criar_usuario_admin_padrao
from views.jogador.cadastro import exibir_tela_cadastro

# Garante que o banco e o admin padrão existam assim que o site ligar
inicializar_banco()
criar_usuario_admin_padrao("Guilherme Admin", ADMIN_EMAIL)

# Configuração da página web
st.set_page_config(page_title="Fantasy Copa", page_icon="⚽", layout="centered")

# Inicializa variáveis de controle na memória do navegador (Session State)
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = None

# FLUXO PRINCIPAL DO SITE

if not st.session_state.logado:
    st.title("⚽ Bem-vindo ao Fantasy da Copa!")
    
    # Cria duas abas na tela inicial: uma para Entrar e outra para se Cadastrar
    aba_login, aba_cadastrar = st.tabs(["Entrar no Jogo", "Criar Conta"])
    
    with aba_login:
        st.subheader("Login")
        email_login = st.text_input("Digite seu e-mail cadastrado:", key="input_login").strip().lower()
        botao_entrar = st.button("Acessar Sistema")
        
        if botao_entrar:
            if not email_login:
                st.error("Por favor, digite seu e-mail.")
            else:
                usuario = buscar_usuario_por_email(email_login)
                if usuario:
                    st.session_state.logado = True
                    st.session_state.usuario_atual = {
                        "id": usuario["id"],
                        "nome": usuario["nome"],
                        "email": usuario["email"],
                        "is_admin": usuario["eh_admin"] == 1
                    }
                    # Recarrega a página já logado
                    st.rerun()
                else:
                    st.error("❌ E-mail não encontrado. Crie uma conta na aba ao lado!")
                    
    with aba_cadastrar:
        exibir_tela_cadastro()

else:
    # SE O USUÁRIO JÁ ESTIVER LOGADO
    user = st.session_state.usuario_atual
    
    # Barra lateral com informações do usuário e botão de Sair
    st.sidebar.write(f"Olá, **{user['nome']}**!")
    if st.sidebar.button("Sair / Logout"):
        st.session_state.logado = False
        st.session_state.usuario_atual = None
        st.rerun()

    # DIRECIONAMENTO DE INTERFACE (Admin vs Jogador)
    if user["is_admin"]:
        st.title("🛡️ Painel do Administrador")
        st.write("Aqui ficarão suas telas de controle de prazos e resultados.")
        # Futuramente importaremos as views do admin aqui
    else:
        st.title("🏆 Área do Jogador")
        st.write("Aqui ficarão os palpites e o ranking dos seus amigos.")
        # Futuramente importaremos as views do jogador aqui