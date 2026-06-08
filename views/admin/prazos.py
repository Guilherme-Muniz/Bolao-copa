import streamlit as st
from datetime import datetime
import sqlite3
from database.connection import conectar_banco

def exibir_tela_prazos():
    st.subheader("⚙️ Configurações de Pontos e Prazos Globais")
    st.write("Defina as regras do seu bolão abaixo. O sistema se adaptará automaticamente.")

    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # Busca a configuração mais recente para preencher os campos por padrão
    cursor.execute("SELECT * FROM configuracoes ORDER BY id DESC LIMIT 1;")
    config_atual = cursor.fetchone()
    conexao.close()

    # Valores padrão caso o banco esteja vazio
    valores_padrao = {
        'pts_artilheiro': config_atual['pontos_artilheiro'] if config_atual else 10,
        'pts_assistencia': config_atual['pontos_assistencia'] if config_atual else 7,
        'pts_melhor_jogador': config_atual['pontos_melhor_jogador'] if config_atual else 10,
        'pts_luva_ouro': config_atual['pontos_luva_ouro'] if config_atual else 7,
        'pts_campeao': config_atual['pontos_campeao'] if config_atual else 15,
        'pts_grupo_exato': config_atual['pontos_grupo_exato'] if config_atual else 5,
        'pts_semifinalista': config_atual['pontos_semifinalista'] if config_atual else 5,
        'pts_placar_exato': config_atual['pontos_placar_exato'] if config_atual else 5,
        'pts_resultado_jogo': config_atual['pontos_resultado_jogo'] if config_atual else 2,
    }

    with st.form("form_configuracoes"):
        st.write("### 📌 Valores dos Pontos")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pa = st.number_input("Artilheiro", value=valores_padrao['pts_artilheiro'])
            la = st.number_input("Líder Assistência", value=valores_padrao['pts_assistencia'])
            mj = st.number_input("Melhor Jogador", value=valores_padrao['pts_melhor_jogador'])
        with col2:
            lo = st.number_input("Luva de Ouro", value=valores_padrao['pts_luva_ouro'])
            ca = st.number_input("Seleção Campeã", value=valores_padrao['pts_campeao'])
            ge = st.number_input("Ordem Grupo Exata", value=valores_padrao['pts_grupo_exato'])
        with col3:
            sf = st.number_input("Semifinalista (Cada)", value=valores_padrao['pts_semifinalista'])
            pe = st.number_input("Placar Exato Jogo", value=valores_padrao['pts_placar_exato'])
            rj = st.number_input("Resultado Jogo (V/E/D)", value=valores_padrao['pts_resultado_jogo'])

        st.write("### ⏳ Prazos")
        # Seleção de data e hora para o encerramento do formulário de longo prazo
        data_limite = st.date_input("Data Limite para Palpites Iniciais:")
        hora_limite = st.time_input("Horário Limite para Palpites Iniciais:")
        
        # Junta data e hora em um único texto no padrão do banco
        prazo_final_dt = datetime.combine(data_limite, hora_limite)
        prazo_final_str = prazo_final_dt.strftime("%Y-%m-%d %H:%M:%S")

        botao_salvar = st.form_submit_button("Salvar Configurações")

        if botao_salvar:
            conexao = conectar_banco()
            cursor = conexao.cursor()
            try:
                cursor.execute("""
                    INSERT INTO configuracoes (
                        pontos_artilheiro, pontos_assistencia, pontos_melhor_jogador,
                        pontos_luva_ouro, pontos_campeao, pontos_grupo_exato,
                        pontos_semifinalista, pontos_placar_exato, pontos_resultado_jogo,
                        prazo_palpites_iniciais
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (pa, la, mj, lo, ca, ge, sf, pe, rj, prazo_final_str))
                conexao.commit()
                st.success("💾 Configurações de pontos e prazos salvas com sucesso!")
            except sqlite3.Error as e:
                st.error(f"Erro ao salvar no banco: {e}")
            finally:
                conexao.close()