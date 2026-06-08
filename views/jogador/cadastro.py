import streamlit as st
from database.queries import cadastrar_jogador

def exibir_tela_cadastro():
    st.header("📝 Cadastro de Novo Jogador")
    st.write("Insira seus dados abaixo para entrar no Fantasy Game da Copa!")

    # Formulário visual do Streamlit
    with st.form("form_cadastro"):
        nome = st.text_input("Nome Completo:")
        email = st.text_input("Seu melhor E-mail:").strip().lower()
        
        botao_enviar = st.form_submit_button("Cadastrar e Jogar")
        
        if botao_enviar:
            if not nome or not email:
                st.error("⚠️ Por favor, preencha todos os campos!")
            elif "@" not in email:
                st.error("⚠️ Digite um e-mail válido!")
            else:
                sucesso = cadastrar_jogador(nome, email)
                if sucesso:
                    st.success("🎉 Cadastro realizado com sucesso! Agora você já pode fazer o Login.")
                else:
                    st.error("❌ Este e-mail já está cadastrado no sistema.")