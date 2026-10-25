-- Script de criação do banco (SQLite). Equivale ao que o ORM gera automaticamente.
-- Uso opcional:  sqlite3 tarefas.db < schema.sql

CREATE TABLE IF NOT EXISTS usuarios (
    id          INTEGER PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    senha_hash  VARCHAR(255) NOT NULL,
    criado_em   DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS categorias (
    id          INTEGER PRIMARY KEY,
    nome        VARCHAR(80) NOT NULL,
    descricao   VARCHAR(255),
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    CONSTRAINT uq_categoria_usuario_nome UNIQUE (usuario_id, nome)
);

CREATE TABLE IF NOT EXISTS tarefas (
    id            INTEGER PRIMARY KEY,
    titulo        VARCHAR(120) NOT NULL,
    descricao     TEXT,
    status        VARCHAR(20) NOT NULL DEFAULT 'pendente',
    prioridade    VARCHAR(10) NOT NULL DEFAULT 'media',
    prazo         DATE,
    criado_em     DATETIME NOT NULL,
    atualizado_em DATETIME NOT NULL,
    usuario_id    INTEGER NOT NULL REFERENCES usuarios(id),
    categoria_id  INTEGER REFERENCES categorias(id)
);

CREATE INDEX IF NOT EXISTS ix_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS ix_tarefas_status ON tarefas(status);
CREATE INDEX IF NOT EXISTS ix_tarefas_usuario_id ON tarefas(usuario_id);
CREATE INDEX IF NOT EXISTS ix_tarefas_categoria_id ON tarefas(categoria_id);
CREATE INDEX IF NOT EXISTS ix_categorias_usuario_id ON categorias(usuario_id);
