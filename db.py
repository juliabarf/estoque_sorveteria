# db.py
import sqlite3
import json
import os
from datetime import datetime

# Nome do arquivo do banco de dados
DB_NAME = "estoque.db"


def get_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Permite acesso por nome das colunas
    return conn


def get_database():
    """Retorna uma conexão com o banco de dados (alias para compatibilidade)"""
    return get_connection()


def init_db():
    """Inicializa o banco de dados criando as tabelas se não existirem"""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de produtos
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS produtos
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       categoria
                       TEXT
                       NOT
                       NULL,
                       nome
                       TEXT
                       NOT
                       NULL,
                       quantidade
                       INTEGER
                       NOT
                       NULL,
                       preco
                       REAL
                       NOT
                       NULL
                   )
                   """)

    # Tabela de pedidos
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS pedidos
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       categoria
                       TEXT
                       NOT
                       NULL,
                       nome_produto
                       TEXT
                       NOT
                       NULL,
                       quantidade
                       INTEGER
                       NOT
                       NULL,
                       preco_unitario
                       REAL
                       NOT
                       NULL,
                       total
                       REAL
                       NOT
                       NULL,
                       data_hora
                       TEXT
                       NOT
                       NULL
                   )
                   """)

    conn.commit()
    conn.close()


def fazer_backup():
    """
    Exporta as tabelas 'produtos' e 'pedidos' para um arquivo JSON.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Busca produtos
        cursor.execute("SELECT * FROM produtos")
        produtos = [dict(row) for row in cursor.fetchall()]

        # Busca pedidos
        cursor.execute("SELECT * FROM pedidos")
        pedidos = [dict(row) for row in cursor.fetchall()]

        conn.close()

        dados_backup = {
            "produtos": produtos,
            "pedidos": pedidos
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dados_backup, f, ensure_ascii=False, indent=4)

        return True, filename
    except Exception as e:
        return False, str(e)


# Inicializa o banco ao importar o módulo
init_db()