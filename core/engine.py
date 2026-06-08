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
    Compara o palpite do usuário com o gabarito oficial usando Sets para as Semifinais.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    pontos_totais = 0

    # 1. PEGA OS PALPITES DO USUÁRIO
    cursor.execute("SELECT * FROM palpites_iniciais WHERE usuario_id = ?;", (usuario_id,))
    p = cursor.fetchone()

    # 2. PEGA O GABARITO OFICIAL (Salvo pelo Admin)
    # Checa primeiro se a tabela existe
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='gabarito_premios';")
    if cursor.fetchone()[0] == 0:
        conexao.close()
        return 0 # Gabarito ainda não foi criado pelo Admin

    cursor.execute("SELECT * FROM gabarito_premios LIMIT 1;")
    g = cursor.fetchone()
    conexao.close()

    # Se o usuário não enviou palpites ou o admin não salvou o gabarito, retorna 0
    if not p or not g:
        return 0

    # --- FUNÇÃO AUXILIAR DE COMPARAÇÃO LIMPA ---
    def comparar_texto(txt1, txt2):
        if not txt1 or not txt2: return False
        return txt1.strip().lower() == txt2.strip().lower()

    # --- 1. PONTUAÇÃO DE PRÊMIOS INDIVIDUAIS (Comparação Exata) ---
    if comparar_texto(p['campeao'], g['campeao']): pontos_totais += config['pontos_campeao']
    if comparar_texto(p['artilheiro'], g['artilheiro']): pontos_totais += config['pontos_artilheiro']
    if comparar_texto(p['melhor_jogador'], g['melhor_jogador']): pontos_totais += config['pontos_melhor_jogador']
    if comparar_texto(p['luva_ouro'], g['luva_ouro']): pontos_totais += config['pontos_luva_ouro']
    if comparar_texto(p['assistencias'], g['assistencias']): pontos_totais += config['pontos_assistencia']

    # --- 2. PONTUAÇÃO DOS GRUPOS (Comparação Exata da Ordem) ---
    grupos = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for letra in grupos:
        campo = f'grupo_{letra}'
        if comparar_texto(p[campo], g[campo]):
            pontos_totais += config['pontos_grupo_exato']

    # --- 3. PONTUAÇÃO DOS SEMIFINALISTAS (A MÁGICA DO SET 🧙‍♂️) ---
    if p['semifinalistas'] and g['semifinalistas']:
        # Transforma o palpite e o gabarito em conjuntos de itens limpos e minúsculos
        set_palpite = set(item.strip().lower() for item in p['semifinalistas'].split(",") if item)
        set_gabarito = set(item.strip().lower() for item in g['semifinalistas'].split(",") if item)
        
        # Pega a interseção (quais seleções estão em ambos os conjuntos, ignorando a ordem)
        acertos_semifinalistas = set_palpite.intersection(set_gabarito)
        
        # Cada semifinalista correto dá a pontuação configurada multiplicada pela quantidade
        pontos_totais += len(acertos_semifinalistas) * config['pontos_semifinalista']

    return pontos_totais


def gerar_ranking_geral():
    """Lê todos os usuários, calcula (jogos + iniciais) e retorna o ranking ordenado."""
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
            'email': grandmother = jogador['email'],
            'pontos': total
        })

    ranking_ordenado = sorted(ranking, key=lambda k: k['pontos'], reverse=True)
    return ranking_ordenado