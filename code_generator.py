"""
code_generator.py
Implementa a regra de negócio para geração de códigos sequenciais
no formato: PAIS(2) + GRUPO(1) + SEC(4 dígitos zerofill) + TIPO_ALIMENTO(1)
Exemplo: BRC0004A
"""

from db_connection import get_connection


# ── Validação de entradas ─────────────────────────────────────────────────────

def _validar_entradas(grupo: str, tipo_alimento: str, pais: str) -> None:
    """
    Valida os parâmetros recebidos antes de gerar o código.

    Raises:
        ValueError: para qualquer entrada inválida.
    """
    if not grupo:
        raise ValueError("O campo 'Grupo' não pode ser vazio.")
    if not tipo_alimento:
        raise ValueError("O campo 'Tipo_Alimento' não pode ser vazio.")
    if not pais:
        raise ValueError("O campo 'Pais' não pode ser vazio.")
    if len(pais) != 2:
        raise ValueError(
            f"'Pais' deve ter exatamente 2 caracteres. Recebido: '{pais}' ({len(pais)} chars)."
        )
    if len(grupo) != 1:
        raise ValueError(
            f"'Grupo' deve ter exatamente 1 caractere. Recebido: '{grupo}' ({len(grupo)} chars)."
        )
    if len(tipo_alimento) != 1:
        raise ValueError(
            f"'Tipo_Alimento' deve ter exatamente 1 caractere. Recebido: '{tipo_alimento}'."
        )


# ── Função principal ──────────────────────────────────────────────────────────

def gerar_codigo(grupo: str, tipo_alimento: str, pais: str) -> tuple[str, int]:
    """
    Gera o próximo código sequencial para o grupo/país informado,
    persiste o registro na tabela `codigos_sequenciais` e retorna
    o código gerado e o valor de `sec` utilizado.

    Parâmetros:
        grupo          – letra identificadora do grupo  (ex: 'C')
        tipo_alimento  – letra do tipo de alimento      (ex: 'A')
        pais           – sigla do país com 2 caracteres (ex: 'BR')

    Retorno:
        (codigo, sec)  – código gerado e sequência utilizada.

    Raises:
        ValueError:       para entradas inválidas.
        ConnectionError:  se a conexão com o banco falhar.
    """
    # Normaliza para maiúsculas
    grupo = grupo.strip().upper()
    tipo_alimento = tipo_alimento.strip().upper()
    pais = pais.strip().upper()

    _validar_entradas(grupo, tipo_alimento, pais)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Bloqueia as linhas do grupo para evitar condição de corrida
        cursor.execute(
            """
            SELECT MAX(sec)
            FROM   codigos_sequenciais
            WHERE  Grupo = %s AND Pais = %s
            FOR UPDATE
            """,
            (grupo, pais),
        )
        resultado = cursor.fetchone()
        max_sec = resultado[0] if resultado[0] is not None else 0
        novo_sec = max_sec + 1

        # Formata o código: PAIS + GRUPO + SEC(4 dígitos) + TIPO
        codigo = f"{pais}{grupo}{novo_sec:04d}{tipo_alimento}"

        # Persiste o novo registro
        cursor.execute(
            """
            INSERT INTO codigos_sequenciais (codigo, sec, Grupo, Tipo_Alimento, Pais)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (codigo, novo_sec, grupo, tipo_alimento, pais),
        )
        conn.commit()
        return codigo, novo_sec

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
