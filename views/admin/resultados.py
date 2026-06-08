import streamlit as st
from datetime import datetime
from database.queries import (
    cadastrar_jogo_oficial, 
    listar_jogos, 
    atualizar_placar_real, 
    salvar_gabarito_premios, 
    buscar_gabarito_premios
)

def exibir_tela_resultados():
    st.subheader("⚙️ Painel de Controle da Copa")
    
    aba_cadastrar, aba_placar, aba_premios = st.tabs([
        "1. Cadastrar Novo Jogo", 
        "2. Inserir Placar Real", 
        "3. Gabarito Oficial da Copa"
    ])
    
    # --- ABA 1: CADASTRAR JOGO ---
    with aba_cadastrar:
        st.write("### Adicionar Partida ao Cronograma")
        with st.form("form_novo_jogo", clear_on_submit=True):
            time_a = st.text_input("Seleção A (Ex: Brasil):")
            time_b = st.text_input("Seleção B (Ex: França):")
            col1, col2 = st.columns(2)
            with col1: data_jogo = st.date_input("Data do Jogo:")
            with col2: hora_jogo = st.time_input("Horário do Jogo:")
            if st.form_submit_button("Salvar Jogo"):
                if not time_a or not time_b: st.error("⚠️ Digite o nome das duas seleções!")
                else:
                    dt_string = datetime.combine(data_jogo, hora_jogo).strftime("%Y-%m-%d %H:%M:%S")
                    cadastrar_jogo_oficial(time_a, time_b, dt_string)
                    st.success(f"🎉 Jogo {time_a} x {time_b} adicionado!")
                    st.rerun()

    # --- ABA 2: INSERIR PLACAR REAL ---
    with aba_placar:
        st.write("### Encerrar Partidas")
        jogos = listar_jogos()
        if not jogos: st.warning("Nenhum jogo cadastrado ainda.")
        else:
            opcoes_jogos = {}
            for j in jogos:
                dt_formatada = datetime.strptime(j['data_hora'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M")
                status = " ✅ (Encerrado)" if j['gols_a_real'] is not None else " ⏳ (Aberto)"
                opcoes_jogos[f"{dt_formatada} - {j['time_a']} x {j['time_b']}{status}"] = j['id']
            selecionado = st.selectbox("Escolha o jogo para atualizar:", list(opcoes_jogos.keys()))
            jogo_atual = [j for j in jogos if j['id'] == opcoes_jogos[selecionado]][0]
            with st.form("form_placar"):
                val_a = jogo_atual['gols_a_real'] if jogo_atual['gols_a_real'] is not None else 0
                val_b = jogo_atual['gols_b_real'] if jogo_atual['gols_b_real'] is not None else 0
                col_a, col_b = st.columns(2)
                with col_a: gols_a = st.number_input(f"Gols {jogo_atual['time_a']}", min_value=0, step=1, value=val_a)
                with col_b: gols_b = st.number_input(f"Gols {jogo_atual['time_b']}", min_value=0, step=1, value=val_b)
                if st.form_submit_button("Confirmar Placar Oficial"):
                    atualizar_placar_real(jogo_atual['id'], gols_a, gols_b)
                    st.success("💾 Placar actualizado!")
                    st.rerun()

    # --- ABA 3: GABARITO COMPLETO (12 GRUPOS) ---
    with aba_premios:
        st.write("### Definir Resultados Oficiais do Torneio")
        gab_atual = buscar_gabarito_premios()
        with st.form("form_gabarito_completo"):
            st.markdown("#### 🏆 Campeão e Prêmios Individuais")
            col1, col2 = st.columns(2)
            with col1:
                camp = st.text_input("Seleção Campeã:", value=gab_atual['campeao'] if gab_atual else "")
                art = st.text_input("Artilheiro da Copa:", value=gab_atual['artilheiro'] if gab_atual else "")
                melhor = st.text_input("Melhor Jogador:", value=gab_atual['melhor_jogador'] if gab_atual else "")
            with col2:
                luva = st.text_input("Melhor Goleiro:", value=gab_atual['luva_ouro'] if gab_atual else "")
                ass = st.text_input("Líder de Assistências:", value=gab_atual['assistencias'] if gab_atual else "")
            
            st.write("---")
            st.markdown("#### 📊 Ordem Exata dos Grupos (A até L)")
            
            g_letras = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
            grupos_inputs = {}
            col_g1, col_g2, col_g3, col_g4 = st.columns(4)
            
            # CORREÇÃO AQUI: Linhas quebradas e identadas corretamente para o 'with' funcionar
            for idx, letra in enumerate(g_letras):
                campo_banco = f'grupo_{letra.lower()}'
                valor_antigo = gab_atual[campo_banco] if gab_atual else ""
                
                if idx % 4 == 0:
                    with col_g1: 
                        grupos_inputs[letra] = st.text_input(f"Grupo {letra}:", value=valor_antigo)
                elif idx % 4 == 1:
                    with col_g2: 
                        grupos_inputs[letra] = st.text_input(f"Grupo {letra}:", value=valor_antigo)
                elif idx % 4 == 2:
                    with col_g3: 
                        grupos_inputs[letra] = st.text_input(f"Grupo {letra}:", value=valor_antigo)
                else:
                    with col_g4: 
                        grupos_inputs[letra] = st.text_input(f"Grupo {letra}:", value=valor_antigo)

            st.write("---")
            st.markdown("#### 🏅 As 4 Seleções Semifinalistas")
            semi = st.text_input("Semifinalistas oficiais:", value=gab_atual['semifinalistas'] if gab_atual else "")
            
            if st.form_submit_button("Salvar Gabarito Oficial"):
                grupos_limpos = {letra: texto.strip().replace(", ", ",") for letra, texto in grupos_inputs.items()}
                salvar_gabarito_premios(camp, art, melhor, luva, ass, grupos_limpos, semi.strip().replace(", ", ","))
                st.success("🏆 Gabarito oficial de 12 grupos salvo!")
                st.rerun()