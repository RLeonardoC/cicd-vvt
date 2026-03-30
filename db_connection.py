"""
db_connection.py
Módulo responsável por estabelecer e retornar a conexão com o MySQL.
As credenciais são lidas via variáveis de ambiente para que a pipeline
CI/CD as injete sem expor segredos no código-fonte.
"""

import os
import mysql.connector
from mysql.connector import Error


def get_connection():
    """
    Retorna uma conexão ativa com o banco MySQL.

    Variáveis de ambiente esperadas:
        DB_HOST      – endereço do servidor   (padrão: 127.0.0.1)
        DB_PORT      – porta TCP              (padrão: 3306)
        DB_USER      – usuário                (padrão: root)
        DB_PASSWORD  – senha                  (padrão: root)
        DB_NAME      – nome do banco          (padrão: food_codes)

    Raises:
        ConnectionError: se não for possível conectar ao servidor.
    """
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "127.0.0.1"),
            port=int(os.environ.get("DB_PORT", 3306)),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", "root"),
            database=os.environ.get("DB_NAME", "food_codes"),
            autocommit=False,
        )
        return conn
    except Error as e:
        raise ConnectionError(f"Erro ao conectar ao MySQL: {e}") from e
