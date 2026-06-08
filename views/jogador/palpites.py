import streamlit as st
from datetime import datetime
from database.queries import (
    listar_jogos, 
    salvar_palpites_iniciais, 
    buscar_palpites_iniciais_usuario,
    salvar_palpite_jogo,
    buscar_palpites_jogos_usuario
)
from core.validators import verificar_prazo_palpite_inicial, verificar_prazo_jogo

def exibir_tela_palpites(usuario_id):
    st.subheader("🎯 Seus Palpites")
    aba_iniciais, aba_jogos = st.tabs(["🏆 Prêmios e Grupos (Longo Prazo)", "⚽ Palpites dos Jogos"])
    
    # --- ABA 1: PALPITES DE LONGO PRAZO ---
    with aba_iniciais:
        prazo_inicial_valido = verificar_prazo_palpite_inicial()
        p_atual = buscar_palpites_iniciais_usuario(usuario_id)
        if not prazo_inicial_valido: st.warning("🔒 O prazo expirou!")
            
        with st.form("form_palpites_iniciais"):
            st.markdown("#### 🥇 Premiações")
            col1, col2 = st.columns(2)
            with col1:
                camp = st.text_input("Sua Seleção Campeã:", value=p_atual['campeao'] if p_atual else "", disabled=not prazo_inicial_valido)
                art = st.text_input("Seu Artilheiro:", value=p_atual['artilheiro'] if p_atual else "", disabled=not prazo_inicial_valido)
                melhor = st.text_input("Melhor Jogador:", value=p_atual['melhor_jogador'] if p_atual else "", disabled=not prazo_inicial_valido)
            with col2:
                luva = st.text_input("Melhor Goleiro:", value=p_atual['luva_ouro'] if p_atual else "", disabled=not prazo_inicial_valido)
                ass = st.text_input("Líder de Assistências:", value=p_atual['assistencias'] if p_atual else "", disabled=not prazo_inicial_valido)
                
            st.write("---")
            st.markdown("#### 📊 Ordem de Classificação dos Grupos (A até L)")
            
            g_letras = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
            grupos_inputs = {}
            col_g1, col_g2, col_g3 = st.columns(3)
            
            # CORREÇÃO AQUI: Linhas quebradas e identadas corretamente para os palpites dos jogadores
            for idx, letra in enumerate(g_letras):
                campo_banco = f'grupo_{letra.lower()}'
                val_grupo = p_atual[campo_banco] if p_atual else ""
                
                if idx % 3 == 0:
                    with col_g1: 
                        grupos_inputs[letra] = st.text_input(f"Grupo {letra}:", value=val_grupo, disabled=not prazo_inicial_valido)
                elif idx % 3 == 1:
                    with col_g2: 
                        grupos_inputs[letra] = st.text_input(f"Grupo {letra}:", value=val_grupo, disabled=not prazo_inicial_valido)
                else:
                    with col_g3: 
                        grupos_inputs[letra] = st.text_input(f"Grupo {letra}:", value=val_grupo, disabled=not prazo_inicial_valido)
                    
            st.write("---")
            st.markdown("#### 🏅 Os 4 Semifinalistas")
            semi = st.text_input("Seus Semifinalistas:", value=p_atual['semifinalistas'] if p_atual else "", disabled=not prazo_inicial_valido)
            
            if prazo_inicial_valido:
                if st.form_submit_button("Salvar Palpites Iniciais"):
                    grupos_limpos = {letra: texto.strip().replace(", ", ",") for letra, texto in grupos_inputs.items()}
                    salvar_palpites_iniciais(usuario_id, camp, art, melhor, luva, ass, grupos_limpos, semi.strip().replace(", ", ","))
                    st.success("💾 Palpites salvos!")
                    st.rerun()
            else: st.form_submit_button("Prazo Encerrado", disabled=True)

    # --- ABA 2: PALPITES DOS JOGOS ---
    with aba_jogos:
        jogos = listar_jogos()
        palpites_salvos = buscar_palpites_jogos_usuario(usuario_id)
        if not jogos: st.info("Nenhuma partida cadastrada.")
        else:
            for jogo in jogos:
                j_id = jogo['id']
                prazo_jogo_valido = verificar_prazo_jogo(j_id)
                gols_a_padrao, gols_b_padrao = palpites_salvos.get(j_id, (0, 0))
                with st.container():
                    st.markdown(f"**📅 {datetime.strptime(jogo['data_hora'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y às %H:%M')}**")
                    col_time_a, col_input_a, col_vs, col_input_b, col_time_b, col_btn = st.columns([3, 2, 1, 2, 3, 2])
                    with col_time_a: st.write(f"### {jogo['time_a']}")
                    with col_input_a: gols_a = st.number_input(f"Gols {jogo['time_a']}", min_value=0, step=1, value=gols_a_padrao, key=f"inj_a_{j_id}", label_visibility="collapsed", disabled=not prazo_jogo_valido)
                    with col_vs: st.write("### x")
                    with col_input_b: gols_b = st.number_input(f"Gols {jogo['time_b']}", min_value=0, step=1, value=gols_b_padrao, key=f"inj_b_{j_id}", label_visibility="collapsed", disabled=not prazo_jogo_valido)
                    with col_time_b: st.write(f"### {jogo['time_b']}")
                    with col_btn:
                        if prazo_jogo_valido:
                            if st.button("Salvar", key=f"btn_{j_id}"):
                                salvar_palpite_jogo(usuario_id, j_id, gols_a, gols_b)
                                st.success("Salvo!")
                                st.rerun()
                        else:
                            st.write("🔒 Bloqueado")
                            if jogo['gols_a_real'] is not None: st.caption(f"Real: {jogo['gols_a_real']}x{jogo['gols_b_real']}")
                st.markdown("---")