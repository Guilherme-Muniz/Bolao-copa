import sqlite3
from database.connection import conectar_banco

# ==========================================
# GESTÃO DE USUÁRIOS & AUTENTICAÇÃO
# ==========================================

def criar_usuario_admin_padrao(nome, email):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
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
        sucesso = False
    except sqlite3.Error as e:
        sucesso = False
    finally:
        conexao.close()
    return sucesso


def buscar_usuario_por_email(email):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    usuario = None
    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = ?;", (email,))
        usuario = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao buscar usuário por e-mail: {e}")
    finally:
        conexao.close()
    return usuario


# ==========================================
# GESTÃO DE JOGOS & RESULTADOS (ADMIN)
# ==========================================

def cadastrar_jogo_oficial(time_a, time_b, data_hora_str):
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
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        # Criando a tabela com suporte de A até L
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gabarito_premios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campeao TEXT, artilheiro TEXT, melhor_jogador TEXT, luva_ouro TEXT, assistencias TEXT,
                grupo_a TEXT, grupo_b TEXT, grupo_c TEXT, grupo_d TEXT, grupo_e TEXT, grupo_f TEXT,
                grupo_g TEXT, grupo_h TEXT, grupo_i TEXT, grupo_j TEXT, grupo_k TEXT, grupo_l TEXT,
                semifinalistas TEXT
            );
        """)
        
        cursor.execute("DELETE FROM gabarito_premios;")
        
        cursor.execute("""
            INSERT INTO gabarito_premios (
                campeao, artilheiro, melhor_jogador, luva_ouro, assistencias,
                grupo_a, grupo_b, grupo_c, grupo_d, grupo_e, grupo_f,
                grupo_g, grupo_h, grupo_i, grupo_j, grupo_k, grupo_l,
                semifinalistas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            campeao, artilheiro, melhor_jogado, luva_ouro, assistencias,
            grupos_dict.get('A',''), grupos_dict.get('B',''), grupos_dict.get('C',''), grupos_dict.get('D',''),
            grupos_dict.get('E',''), grupos_dict.get('F',''), grupos_dict.get('G',''), grupos_dict.get('H',''),
            grupos_dict.get('I',''), grupos_dict.get('J',''), grupos_dict.get('K',''), grupos_dict.get('L',''),
            semifinalistas_str
        ))
        conexao.commit()
    except sqlite3.Error as e:
        print(f"Erro ao salvar gabarito completo: {e}")
    finally:
        conexao.close()


def buscar_gabarito_premios():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    gabarito = None
    try:
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='gabarito_premios';")
        if cursor.fetchone()[0] == 1:
            cursor.execute("SELECT * FROM gabarito_premios LIMIT 1;")
            gabarito = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao buscar gabarito de prêmios: {e}")
    finally:
        conexao.close()
    return gabarito


# ==========================================
# SALVAMENTO DE PALPITES DOS JOGADORES
# ==========================================

def salvar_palpites_iniciais(usuario_id, campeao, artilheiro, melhor_jogador, luva_ouro, assistencias, grupos_dict, semifinalistas):
    conexao = conectar_banco()
    cursor =连接 = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id FROM palpites_iniciais WHERE usuario_id = ?;", (usuario_id,))
        existe = cursor.fetchone()
        
        if existe:
            cursor.execute("""
                UPDATE palpites_iniciais SET
                    campeao = ?, artilheiro = ?, melhor_jogador = ?, luva_ouro = ?, assistencias = ?,
                    grupo_a = ?, grupo_b = ?, grupo_c = ?, grupo_d = ?, grupo_e = ?, grupo_f = ?,
                    grupo_g = ?, grupo_h = ?, grupo_i = ?, grupo_j = ?, grupo_k = ?, grupo_l = ?,
                    semifinalistas = ?
                WHERE usuario_id = ?;
            """, (campeao, artilheiro, melhor_jogador, luva_ouro, assistencias,
                  grupos_dict.get('A',''), grupos_dict.get('B',''), grupos_dict.get('C',''), grupos_dict.get('D',''),
                  grupos_dict.get('E',''), grupos_dict.get('F',''), grupos_dict.get('G',''), grupos_dict.get('H',''),
                  grupos_dict.get('I',''), grupos_dict.get('J',''), grupos_dict.get('K',''), grupos_dict.get('L',''),
                  semifinalistas, usuario_id))
        else:
            cursor.execute("""
                INSERT INTO palpites_iniciais (
                    usuario_id, campeao, artilheiro, melhor_jogador, luva_ouro, assistencias,
                    grupo_a, grupo_b, grupo_c, grupo_d, grupo_e, grupo_f,
                    grupo_g, grupo_h, grupo_i, grupo_j, grupo_k, grupo_l,
                    semifinalistas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (usuario_id, campeao, artilheiro, melhor_jogador, luva_ouro, assistencias,
                  grupos_dict.get('A',''), grupos_dict.get('B',''), grupos_dict.get('C',''), grupos_dict.get('D',''),
                  grupos_dict.get('E',''), grupos_dict.get('F',''), grupos_dict.get('G',''), grupos_dict.get('H',''),
                  grupos_dict.get('I',''), grupos_dict.get('J',''), grupos_dict.get('K',''), grupos_dict.get('L',''),
                  semifinalistas))
        conexao.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao salvar palpites iniciais: {e}")
        return False
    finally:
        conexao.close()


def salvar_palpite_jogo(usuario_id, jogo_id, gols_a, gols_b):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id FROM palpites_jogos WHERE usuario_id = ? AND jogo_id = ?;", (usuario_id, jogo_id))
        existe = cursor.fetchone()
        
        if existe:
            cursor.execute("UPDATE palpites_jogos SET gols_a = ?, gols_b = ? WHERE usuario_id = ? AND jogo_id = ?;", (gols_a, gols_b, usuario_id, jogo_id))
        else:
            cursor.execute("INSERT INTO palpites_jogos (usuario_id, jogo_id, gols_a, gols_b) VALUES (?, ?, ?, ?);", (usuario_id, jogo_id, gols_a, gols_b))
        conexao.commit()
        return True
    except sqlite3.Error as e:
        return False
    finally:
        conexao.close()


def buscar_palpites_iniciais_usuario(usuario_id):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM palpites_iniciais WHERE usuario_id = ?;", (usuario_id,))
    resultado = cursor.fetchone()
    conexao.close()
    return resultado


def buscar_palpites_jogos_usuario(usuario_id):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT jogo_id, gols_a, gols_b FROM palpites_jogos WHERE usuario_id = ?;", (usuario_id,))
    resultados = cursor.fetchall()
    conexao.close()
    return {r['jogo_id']: (r['gols_a'], r['gols_b']) for r in resultados}