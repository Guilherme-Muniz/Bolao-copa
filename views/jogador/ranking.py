import streamlit as st

def exibir_ranking_turbinado(ranking):
    if not ranking:
        st.info("💡 Nenhum jogador pontuou ainda. Assim que os primeiros jogos forem encerrados, o placar vai ferver!")
        return

    st.write("### 🏃‍♂️ Corrida pelo Título")
    
    # Destaque para o Top 3 (Pódio)
    col1, col2, col3 = st.columns(3)
    
    # 1º Lugar
    with col1:
        if len(ranking) >= 1:
            st.markdown(
                f"""
                <div style="background-color:#FFD700;padding:15px;border-radius:10px;text-align:center;color:black">
                    <h3>🥇 1º Lugar</h3>
                    <p><b>{ranking[0]['nome']}</b></p>
                    <h2>{ranking[0]['pontos']} pts</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
    # 2º Lugar
    with col2:
        if len(ranking) >= 2:
            st.markdown(
                f"""
                <div style="background-color:#C0C0C0;padding:15px;border-radius:10px;text-align:center;color:black">
                    <h3>🥈 2º Lugar</h3>
                    <p><b>{ranking[1]['nome']}</b></p>
                    <h2>{ranking[1]['pontos']} pts</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
    # 3º Lugar
    with col3:
        if len(ranking) >= 3:
            st.markdown(
                f"""
                <div style="background-color:#CD7F32;padding:15px;border-radius:10px;text-align:center;color:black">
                    <h3>🥉 3º Lugar</h3>
                    <p><b>{ranking[2]['nome']}</b></p>
                    <h2>{ranking[2]['pontos']} pts</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )

    st.write(" ")
    st.write("### 📋 Restante da Tabela")
    
    # Mostra o resto dos jogadores em formato de lista limpa (do 4º em diante)
    for idx, jogador in enumerate(ranking[3:], start=4):
        st.markdown(f"**{idx}º** {jogador['nome']} — `{jogador['pontos']} pontos`")