import sqlite3
from database.connection import conectar_banco

def buscar_configuracoes_pontos():
    """Busca a tabela de pontuação atual configurada pelo Admin."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM configuracoes ORDER BY id DESC LIMIT 1;")
    config = cursor.fetchone()
    conexao.close()
    return config


def calcular_pontos_jogos(usuario_id, config):
    """
    Calcula o total de pontos que um usuário fez baseando-se nos jogos encerrados.
    Regra: Placar Exato = X pontos | Apenas Resultado = Y pontos.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    pontos_totais = 0

    cursor.execute("""
        SELECT p.gols_a AS palpite_a, p.gols_b AS palpite_b,
               j.gols_a_real, j.gols_b_real
        FROM palpites_jogos p
        JOIN jogos j ON p.jogo_id = j.id
        WHERE p.usuario_id = ? AND j.gols_a_real IS NOT NULL AND j.gols_b_real IS NOT NULL;
    """, (usuario_id,))
    
    palpites = cursor.fetchall()
    conexao.close()

    pts_exato = config['pontos_placar_exato']
    pts_resultado = config['pontos_resultado_jogo']

    # CORREÇÃO AQUI: Mudado de 'palvel' para 'palpites'
    for jogo in palpites:
        pa, pb = jogo['palpite_a'], jogo['palpite_b']
        ra, rb = jogo['gols_a_real'], jogo['gols_b_real']

        if pa == ra and pb == rb:
            pontos_totais += pts_exato
        elif (pa > pb and ra > rb) or (pa < pb and ra < rb) or (pa == pb and ra == rb):
            pontos_totais += pts_resultado

    return pontos_totais


def calcular_pontos_iniciais(usuario_id, config):
    """
    Calcula os pontos dos palpites de longo prazo (Artilheiro, Campeão, Grupos, Semifinais).
    Cruza o palpite do usuário com o gabarito oficial salvo pelo Admin.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    pontos_totais = 0

    # 1. Busca os palpites que o jogador enviou
    cursor.execute("SELECT * FROM palpites_iniciais WHERE usuario_id = ?;", (usuario_id,))
    p = cursor.fetchone()

    # 2. Busca o gabarito real inserido pelo Admin
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='gabarito_premios';")
    if cursor.fetchone()[0] == 0:
        conexao.close()
        return 0

    cursor.execute("SELECT * FROM gabarito_premios LIMIT 1;")
    g = cursor.fetchone()
    conexao.close()

    if not p or not g:
        return 0

    def comparar_texto(txt1, txt2):
        if not txt1 or not txt2: return False
        return txt1.strip().lower() == txt2.strip().lower()

    # --- A. ACERTOS DE PRÊMIOS INDIVIDUAIS ---
    if comparar_texto(p['campeao'], g['campeao']): pontos_totais += config['pontos_campeao']
    if comparar_texto(p['artilheiro'], g['artilheiro']): pontos_totais += config['pontos_artilheiro']
    if comparar_texto(p['melhor_jogador'], g['melhor_jogador']): pontos_totais += config['pontos_melhor_jogador']
    if comparar_texto(p['luva_ouro'], g['luva_ouro']): pontos_totais += config['pontos_luva_ouro']
    if comparar_texto(p['assistencias'], g['assistencias']): pontos_totais += config['pontos_assistencia']

    # --- B. ACERTOS DE GRUPOS ---
    grupos = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for letra in grupos:
        campo = f'grupo_{letra}'
        if comparar_texto(p[campo], g[campo]):
            pontos_totais += config['pontos_grupo_exato']

    # --- C. ACERTOS DE SEMIFINALISTAS (SETs) ---
    if p['semifinalistas'] and g['semifinalistas']:
        set_palpite = set(item.strip().lower() for item in p['semifinalistas'].split(",") if item)
        set_gabarito = set(item.strip().lower() for item in g['semifinalistas'].split(",") if item)
        
        selecoes_acertadas = set_palpite.intersection(set_gabarito)
        pontos_totais += len(selecoes_acertadas) * config['pontos_semifinalista']

    return pontos_totais


def gerar_ranking_geral():
    """Lê todos os usuários, processa as pontuações e gera a tabela organizada."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT id, nome, email FROM usuarios WHERE eh_admin = 0;")
    jogadores = cursor.fetchall()
    conexao.close()

    config = buscar_configuracoes_pontos()
    if not config:
        return []

    ranking = []

    for jogador in jogadores:
        pts_jogos = calcular_pontos_jogos(jogador['id'], config)
        pts_iniciais = calcular_pontos_iniciais(jogador['id'], config)
        
        total = pts_jogos + pts_iniciais
        
        ranking.append({
            'nome': jogador['nome'],
            'email': jogador['email'],
            'pontos': total
        })

    ranking_ordenado = sorted(ranking, key=lambda k: k['pontos'], reverse=True)
    return ranking_ordenado