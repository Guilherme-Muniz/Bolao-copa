import os

# Caminho absoluto para a raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho para o arquivo do banco de dados SQL
DB_PATH = os.path.join(BASE_DIR, "fantasy.db")

# E-mail do Administrador Supremo (O seu e-mail de acesso)
# Quando você digitar esse e-mail no login do site, ele te dará acesso ao painel admin
ADMIN_EMAIL = "@seuemail.com"  # Altere para o seu e-mail real aqui