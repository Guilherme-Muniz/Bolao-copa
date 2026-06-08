import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'fantasy.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def conectar_banco():
    """Abre uma conexão com o banco de dados SQLite."""
    conexao = sqlite3.connect(DB_PATH)
    conexao.execute("PRAGMA foreign_keys = ON;")
    conexao.row_factory = sqlite3.Row
    return conexao

def inicializar_banco():
    """Lê o arquivo schema.sql e cria a estrutura de tabelas se não existirem."""
    if not os.path.exists(SCHEMA_PATH):
        print(f"Erro: Arquivo {SCHEMA_PATH} não foi encontrado.")
        return

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        # Lê o conteúdo do arquivo schema.sql
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Executa todos os comandos SQL do arquivo de uma vez só
        cursor.executescript(sql_script)
        conexao.commit()
        print("Banco de dados inicializado com sucesso e tabelas criadas!")
        
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
    finally:
        conexao.close()

if __name__ == "__main__":
    inicializar_banco()