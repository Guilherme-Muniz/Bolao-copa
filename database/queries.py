import sqlite3
from database.connection import conectar_banco


def criar_usuario_admin_padrao(nome, email):
    """
    Cadastra o administrador do sistema caso ele ainda não exista no banco.
    O campo 'eh_admin' é definido como 1.
    """
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
    """
    Cadastra um novo jogador comum no sistema.
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