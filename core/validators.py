from datetime import datetime, timedelta
import sqlite3
from database.connection import conectar_banco

def verificar_prazo_palpite_inicial():
    """
    Checa se ainda é permitido enviar os palpites iniciais (longo prazo).
    Busca a data limite configurada pelo administrador no banco.
    Retorna True se estiver dentro do prazo, False se já tiver expirado.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        # Busca a data limite cadastrada na tabela de configurações
        cursor.execute("SELECT prazo_palpites_iniciais FROM configuracoes ORDER BY id DESC LIMIT 1;")
        resultado = cursor.fetchone()
        
        # Se o admin ainda não configurou nenhum prazo, por segurança, bloqueia
        if not resultado or not resultado['prazo_palpites_iniciais']:
            return False
            
        # Converte a string de data do banco para um objeto datetime do Python
        prazo = datetime.strptime(resultado['prazo_palpites_iniciais'], "%Y-%m-%d %H:%M:%S")
        
        # Retorna True se a hora atual for menor ou igual ao prazo
        return datetime.now() <= prazo
        
    except (sqlite3.Error, ValueError) as e:
        print(f"Erro ao verificar prazo inicial: {e}")
        return False
    finally:
        conexao.close()


def verificar_prazo_jogo(jogo_id):
    """
    Checa se o palpite para um jogo específico está sendo feito a tempo.
    Regra: Permitido até 1 hora ANTES do horário do jogo.
    Retorna True se for válido, False se estiver bloqueado.
    """
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        # Busca o horário oficial do jogo
        cursor.execute("SELECT data_hora FROM jogos WHERE id = ?;", (jogo_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            return False # Jogo não existe
            
        horario_jogo = datetime.strptime(resultado['data_hora'], "%Y-%m-%d %H:%M:%S")
        
        # Calcula o momento limite (Horário do Jogo menos 1 hora)
        limite_envio = horario_jogo - timedelta(hours=1)
        
        # Retorna True se o usuário estiver enviando ANTES do limite
        return datetime.now() <= limite_envio
        
    except (sqlite3.Error, ValueError) as e:
        print(f"Erro ao verificar prazo do jogo {jogo_id}: {e}")
        return False
    finally:
        conexao.close()