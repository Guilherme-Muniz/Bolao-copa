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

    # Busca apenas os jogos que já possuem resultado cadastrado pelo Admin
    cursor.execute("""
        SELECT p.gols_a AS palpite_a, p.gols_b AS palpite_b,
               j.gols_a_real, j.gols_b_real
        FROM palpites_jogos p
        JOIN jogos j ON p.jogo_id = j.id
        WHERE p.usuario_id = ? AND j.gols_a_real IS NOT NULL AND j.gols_b_real IS NOT NULL;
    """, (usuario_id,))
    
    palpites = cursor.fetchall()
    conexao.close()

    # Valores de pontos dinâmicos vindos do banco
    pts_exato = config['pontos_placar_exato']
    pts_resultado = config['pontos_resultado_jogo']

    for jogo in palpites:
        pa, pb = jogo['palpite_a'], jogo['palpite_b']
        ra, rb = jogo['gols_a_real'], jogo['gols_b_real']

        # ACERTOU O PLACAR EXATO (5 pontos padrão)
        if pa == ra and pb == rb:
            pontos_totais += pts_exato
        
        # ACERTOU APENAS O RESULTADO (2 pontos padrão)
        # Vitória do Time A, Vitória do Time B ou Empate
        elif (pa > pb and ra > rb) or (pa < pb and ra < rb) or (pa == pb and ra == rb):
            pontos_totais += pts_resultado

    return pontos_totais


def calcular_pontos_iniciais(usuario_id, config):
    """
    Calcula os pontos dos palpites de longo prazo (Artilheiro, Campeão, Grupos).
    Compara o palpite do usuário com o 'gabarito' inserido nas tabelas oficiais.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    pontos_totais = 0

    #  PEGA OS PALPITES DO USUÁRIO
    cursor.execute("SELECT * FROM palpites_iniciais WHERE usuario_id = ?;", (usuario_id,))
    palpite_ini = cursor.fetchone()

    # Se ele não mandou palpites iniciais, retorna zero nesta parte
    if not palpite_ini:
        conexao.close()
        return 0

    
    conexao.close()
    return pontos_totais


def gerar_ranking_geral():
    """
    Lê todos os usuários do banco, calcula os pontos de cada um (jogos + iniciais)
    e retorna uma lista organizada do primeiro ao último colocado.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # Pega todos os jogadores cadastrados 
    cursor.execute("SELECT id, nome, email FROM usuarios WHERE eh_admin = 0;")
    jogadores = cursor.fetchall()
    conexao.close()

    config = buscar_configuracoes_pontos()
    if not config:
        return []

    ranking = []

    for jogador in jogadores:
        # Calcula cada parte da pontuação
        pts_jogos = calcular_pontos_jogos(jogador['id'], config)
        pts_iniciais = calcular_pontos_iniciais(jogador['id'], config)
        
        total = pts_jogos + pts_iniciais
        
        ranking.append({
            'nome': jogador['nome'],
            'email': jogador['email'],
            'pontos': total
        })

    # Ordena a lista de dicionários pelo campo 'pontos' de forma decrescente (Maior para o menor)
    ranking_ordenado = sorted(ranking, key=lambda k: k['pontos'], reverse=True)
    return ranking_ordenado