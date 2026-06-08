import sqlite3
from database.connection import conectar_banco

# ==========================================
# GESTÃO DE USUÁRIOS & AUTENTICAÇÃO
# ==========================================

def criar_usuario_admin_padrao(nome, email):
    """
    Cadastra o administrador do sistema caso ele ainda não exista no banco.
    O campo 'eh_admin' é definido como 1.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        # INSERT OR IGNORE evita erros caso você rode o sistema mais de uma vez,
        # pois o e-mail tem a restrição UNIQUE no banco de dados.
        cursor.execute("""
            INSERT OR IGNORE INTO usuarios (nome, email, eh_admin)
            VALUES (?, ?, 1);
        """, (nome, email))
        conexao.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar admin padrão: {e}")
    finally:
        conexao.close()


def cadastrar_jogador(nome, email):
    """
    Cadastra um novo amigo (jogador comum) no sistema.
    Retorna True se cadastrado com sucesso ou False se o e-mail já existir.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    sucesso = False
    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, eh_admin)
            VALUES (?, ?, 0);
        """, (nome, email))
        conexao.commit()
        sucesso = True
    except sqlite3.IntegrityError:
        # Cai aqui se o e-mail já estiver cadastrado (violando o UNIQUE)
        print(f"Erro: O e-mail {email} já está cadastrado.")
        sucesso = False
    except sqlite3.Error as e:
        print(f"Erro ao cadastrar jogador: {e}")
        sucesso = False
    finally:
        conexao.close()
    return sucesso


def buscar_usuario_por_email(email):
    """
    Busca os dados de um usuário no banco através do e-mail.
    Útil para validar o login e checar se é Admin ou Jogador.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    usuario = None
    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = ?;", (email,))
        usuario = cursor.fetchone() # Retorna a linha encontrada ou None
    except sqlite3.Error as e:
        print(f"Erro ao buscar usuário por e-mail: {e}")
    finally:
        conexao.close()
    return usuario


# ==========================================
# GESTÃO DE JOGOS & RESULTADOS (ADMIN)
# ==========================================

def cadastrar_jogo_oficial(time_a, time_b, data_hora_str):
    """Insere uma nova partida no cronograma oficial da Copa."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            INSERT INTO jogos (time_a, time_b, data_hora)
            VALUES (?, ?, ?);
        """, (time_a, time_b, data_hora_str))
        conexao.commit()
    except sqlite3.Error as e:
        print(f"Erro ao cadastrar jogo: {e}")
    finally:
        conexao.close()


def listar_jogos():
    """Retorna todos os jogos cadastrados no sistema ordenados por data."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT * FROM jogos ORDER BY data_hora ASC;")
        jogos = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao listar jogos: {e}")
        jogos = []
    finally:
        conexao.close()
    return jogos


def atualizar_placar_real(jogo_id, gols_a, gols_b):
    """Insere o resultado oficial de uma partida para computar os pontos."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            UPDATE jogos 
            SET gols_a_real = ?, gols_b_real = ?
            WHERE id = ?;
        """, (gols_a, gols_b, jogo_id))
        conexao.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar placar real: {e}")
    finally:
        conexao.close()


# ==========================================
# GESTÃO DO GABARITO OFICIAL DA COPA (ADMIN)
# ==========================================

def salvar_gabarito_premios(campeao, artilheiro, melhor_jogado, luva_ouro, assistencias, grupos_dict, semifinalistas_str):
    """Cria a tabela e atualiza o gabarito oficial de prêmios, ordem dos grupos e semifinalistas."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        # Garante a existência da tabela com todos os campos necessários estruturados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gabarito_premios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campeao TEXT,
                artilheiro TEXT,
                melhor_jogador TEXT,
                luva_ouro TEXT,
                assistencias TEXT,
                grupo_a TEXT, grupo_b TEXT, grupo_c TEXT, grupo_d TEXT,
                grupo_e TEXT, grupo_f TEXT, grupo_g TEXT, grupo_h TEXT,
                semifinalistas TEXT
            );
        """)
        
        # Limpa o registro anterior para manter sempre apenas 1 linha ativa de gabarito global
        cursor.execute("DELETE FROM gabarito_premios;")
        
        cursor.execute("""
            INSERT INTO gabarito_premios (
                campeao, artilheiro, melhor_jogador, luva_ouro, assistencias,
                grupo_a, grupo_b, grupo_c, grupo_d, grupo_e, grupo_f, grupo_g, grupo_h,
                semifinalistas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            campeao, artilheiro, melhor_jogado, luva_ouro, assistencias,
            grupos_dict.get('A', ''), grupos_dict.get('B', ''), grupos_dict.get('C', ''), grupos_dict.get('D', ''),
            grupos_dict.get('E', ''), grupos_dict.get('F', ''), grupos_dict.get('G', ''), grupos_dict.get('H', ''),
            semifinalistas_str
        ))
        
        conexao.commit()
    except sqlite3.Error as e:
        print(f"Erro ao salvar gabarito completo: {e}")
    finally:
        conexao.close()


def buscar_gabarito_premios():
    """Busca o gabarito oficial completo contendo prêmios, grupos e semifinalistas."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    gabarito = None
    try:
        # Checa primeiro se a tabela existe na estrutura do arquivo SQLite para evitar falhas silenciosas
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='gabarito_premios';")
        if cursor.fetchone()[0] == 1:
            cursor.execute("SELECT * FROM gabarito_premios LIMIT 1;")
            gabarito = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao buscar gabarito de prêmios: {e}")
    finally:
        conexao.close()
    return gabarito


def salvar_palpites_iniciais(usuario_id, campeao, artilheiro, melhor_jogador, luva_ouro, assistencias, grupos_dict, semifinalistas):
    """Salva ou atualiza os palpites de longo prazo do jogador."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        # Verifica se o jogador já tem um palpite inicial salvo
        cursor.execute("SELECT id FROM palpites_iniciais WHERE usuario_id = ?;", (usuario_id,))
        existe = cursor.fetchone()
        
        if existe:
            cursor.execute("""
                UPDATE palpites_iniciais SET
                    campeao = ?, artilheiro = ?, melhor_jogador = ?, luva_ouro = ?, assistencias = ?,
                    grupo_a = ?, grupo_b = ?, grupo_c = ?, grupo_d = ?,
                    grupo_e = ?, grupo_f = ?, grupo_g = ?, grupo_h = ?,
                    semifinalistas = ?
                WHERE usuario_id = ?;
            """, (campeao, artilheiro, melhor_jogador, luva_ouro, assistencias,
                  grupos_dict.get('A',''), grupos_dict.get('B',''), grupos_dict.get('C',''), grupos_dict.get('D',''),
                  grupos_dict.get('E',''), grupos_dict.get('F',''), grupos_dict.get('G',''), grupos_dict.get('H',''),
                  semifinalistas, usuario_id))
        else:
            cursor.execute("""
                INSERT INTO palpites_iniciais (
                    usuario_id, campeao, artilheiro, melhor_jogador, luva_ouro, assistencias,
                    grupo_a, grupo_b, grupo_c, grupo_d, grupo_e, grupo_f, grupo_g, grupo_h,
                    semifinalistas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (usuario_id, campeao, artilheiro, melhor_jogador, luva_ouro, assistencias,
                  grupos_dict.get('A',''), grupos_dict.get('B',''), grupos_dict.get('C',''), grupos_dict.get('D',''),
                  grupos_dict.get('E',''), grupos_dict.get('F',''), grupos_dict.get('G',''), grupos_dict.get('H',''),
                  semifinalistas))
        conexao.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao salvar palpites iniciais: {e}")
        return False
    finally:
        conexao.close()


def salvar_palpite_jogo(usuario_id, jogo_id, gols_a, gols_b):
    """Salva ou atualiza o palpite do jogador para uma partida específica."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id FROM palpites_jogos WHERE usuario_id = ? AND jogo_id = ?;", (usuario_id, jogo_id))
        existe = cursor.fetchone()
        
        if existe:
            cursor.execute("""
                UPDATE palpites_jogos SET gols_a = ?, gols_b = ?
                WHERE usuario_id = ? AND jogo_id = ?;
            """, (gols_a, gols_b, usuario_id, jogo_id))
        else:
            cursor.execute("""
                INSERT INTO palpites_jogos (usuario_id, jogo_id, gols_a, gols_b)
                VALUES (?, ?, ?, ?);
            """, (usuario_id, jogo_id, gols_a, gols_b))
        conexao.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao salvar palpite do jogo: {e}")
        return False
    finally:
        conexao.close()


def buscar_palpites_iniciais_usuario(usuario_id):
    """Busca as respostas salvas do jogador para preencher os campos da tela."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM palpites_iniciais WHERE usuario_id = ?;", (usuario_id,))
    resultado = cursor.fetchone()
    conexao.close()
    return resultado


def buscar_palpites_jogos_usuario(usuario_id):
    """Busca todos os palpites de partidas que o jogador já enviou."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT jogo_id, gols_a, gols_b FROM palpites_jogos WHERE usuario_id = ?;", (usuario_id,))
    resultados = cursor.fetchall()
    conexao.close()
    # Transforma em dicionário {jogo_id: (gols_a, gols_b)} para facilitar a busca na tela
    return {r['jogo_id']: (r['gols_a'], r['gols_b']) for r in resultados}