-- TABELA DE CONFIGURAÇÕES GERAIS (Controlada pelo Admin)
-- Guarda quanto vale cada acerto e os prazos globais
CREATE TABLE IF NOT EXISTS configuracoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pontos_artilheiro INTEGER DEFAULT 10,
    pontos_assistencia INTEGER DEFAULT 7,
    pontos_melhor_jogador INTEGER DEFAULT 10,
    pontos_luva_ouro INTEGER DEFAULT 7,
    pontos_campeao INTEGER DEFAULT 15,
    pontos_grupo_exato INTEGER DEFAULT 5,
    pontos_semifinalista INTEGER DEFAULT 5,
    pontos_placar_exato INTEGER DEFAULT 5,
    pontos_resultado_jogo INTEGER DEFAULT 2,
    prazo_palpites_iniciais DATETIME NOT NULL -- Data limite para os prêmios/grupos
);

-- TABELA DE USUÁRIOS
-- O e-mail do admin será cadastrado aqui para o sistema identificar seu acesso
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    eh_admin INTEGER DEFAULT 0 -- 0 para jogador comum, 1 para Admin
);

-- TABELA DE JOGOS (Cadastrados e atualizados pelo Admin)
CREATE TABLE IF NOT EXISTS jogos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_a TEXT NOT NULL,
    time_b TEXT NOT NULL,
    data_hora DATETIME NOT NULL, -- O sistema usará isso para calcular a trava de 1 hora antes
    gols_a_real INTEGER DEFAULT NULL, -- Preenchido pelo admin após o jogo
    gols_b_real INTEGER DEFAULT NULL  -- Preenchido pelo admin após o jogo
);

-- TABELA DE PALPITES INICIAIS (feitos antes de começar a copa)
CREATE TABLE IF NOT EXISTS palpites_iniciais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    campeao TEXT,
    artilheiro TEXT,
    melhor_jogador TEXT,
    luva_ouro TEXT,
    assistencias TEXT,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    UNIQUE(usuario_id) -- Garante que cada usuário só tenha um palpite inicial salvo
);

-- TABELA DE PALPITES DOS GRUPOS 
CREATE TABLE IF NOT EXISTS palpites_grupos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    grupo TEXT NOT NULL, -- 'A', 'B', 'C', etc.
    ordem_selecoes TEXT NOT NULL, -- Ex: "Brasil,França,Egito,Japão"
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    UNIQUE(usuario_id, grupo) -- Um palpite de ordem por grupo para cada usuário
);

-- TABELA DE PALPITES DE JOGOS
CREATE TABLE IF NOT EXISTS palpites_jogos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    jogo_id INTEGER NOT NULL,
    gols_a INTEGER NOT NULL,
    gols_b INTEGER NOT NULL,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (jogo_id) REFERENCES jogos(id),
    UNIQUE(usuario_id, jogo_id) -- Impede que o jogador envie dois palpites para o mesmo jogo
);