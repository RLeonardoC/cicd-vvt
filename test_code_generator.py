"""
test_code_generator.py
Testes automatizados (pytest) para a função gerar_codigo e a integração
com o banco de dados MySQL.

Cobertura:
  - Conexão com o banco
  - Existência da tabela e dados iniciais
  - Geração de próximo código para grupo existente
  - Geração do primeiro código (sec=1) para grupo inexistente
  - Incremento correto do campo sec
  - Zerofill com 4 dígitos
  - Entradas inválidas
  - Prevenção de duplicidade
"""

import pytest
from db_connection import get_connection
from code_generator import gerar_codigo

# País de teste isolado para não interferir nos dados de referência
PAIS_TESTE = "TS"


# ── Fixture: limpeza dos dados de teste após cada caso ────────────────────────

@pytest.fixture(autouse=True)
def limpar_dados_teste():
    """Remove registros inseridos pelos testes ao final de cada caso."""
    yield
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM codigos_sequenciais WHERE Pais = %s",
        (PAIS_TESTE,),
    )
    conn.commit()
    cursor.close()
    conn.close()


# ── 1. Infraestrutura ─────────────────────────────────────────────────────────

def test_conexao_banco_de_dados():
    """Verifica se é possível conectar ao MySQL."""
    conn = get_connection()
    assert conn.is_connected(), "A conexão com o banco de dados deve estar ativa."
    conn.close()


def test_tabela_codigos_sequenciais_existe():
    """Confirma que a tabela codigos_sequenciais foi criada pelo setup.sql."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'codigos_sequenciais'")
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    assert resultado is not None, "A tabela 'codigos_sequenciais' deve existir no banco."


def test_dados_iniciais_carregados():
    """Verifica se os 9 registros iniciais foram inseridos pelo setup.sql."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM codigos_sequenciais WHERE Pais = 'BR'")
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    assert total >= 9, f"Devem existir ao menos 9 registros iniciais (BR). Encontrados: {total}."


# ── 2. Regra de negócio – geração de códigos ─────────────────────────────────

def test_proximo_codigo_grupo_existente():
    """
    Grupo 'C' (BR) já possui sec=3. O próximo deve ser sec=4 → BRC0004A.
    """
    codigo, sec = gerar_codigo("C", "A", "BR")
    assert sec == 4, f"sec esperado: 4, obtido: {sec}"
    assert codigo == "BRC0004A", f"Código esperado: BRC0004A, obtido: {codigo}"
    # Limpa o registro inserido no grupo BR/C para não afetar outros testes
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM codigos_sequenciais WHERE codigo = 'BRC0004A'")
    conn.commit()
    cursor.close()
    conn.close()


def test_primeiro_codigo_grupo_inexistente():
    """Para um grupo novo, sec deve começar em 1."""
    codigo, sec = gerar_codigo("Z", "A", PAIS_TESTE)
    assert sec == 1, f"sec esperado: 1, obtido: {sec}"
    assert codigo == f"{PAIS_TESTE}Z0001A", f"Código inválido: {codigo}"


def test_incremento_correto_do_sec():
    """Inserções sucessivas para o mesmo grupo devem incrementar sec."""
    _, sec1 = gerar_codigo("M", "A", PAIS_TESTE)
    _, sec2 = gerar_codigo("M", "B", PAIS_TESTE)
    _, sec3 = gerar_codigo("M", "C", PAIS_TESTE)
    assert sec1 == 1
    assert sec2 == sec1 + 1, f"sec2 deveria ser {sec1 + 1}, obtido {sec2}"
    assert sec3 == sec2 + 1, f"sec3 deveria ser {sec2 + 1}, obtido {sec3}"


def test_zerofill_4_digitos():
    """A parte numérica do código deve sempre ter exatamente 4 dígitos."""
    codigo, _ = gerar_codigo("Q", "X", PAIS_TESTE)
    # Estrutura: TS(2) + Q(1) + NNNN(4) + X(1) = 8 chars
    parte_numerica = codigo[3:7]  # posições 3,4,5,6
    assert len(parte_numerica) == 4, f"Parte numérica deve ter 4 dígitos: '{parte_numerica}'"
    assert parte_numerica.isdigit(), f"Parte numérica deve conter apenas dígitos: '{parte_numerica}'"
    assert parte_numerica == "0001", f"Primeiro valor zerofill deve ser '0001': '{parte_numerica}'"


def test_zerofill_preservado_em_valores_maiores():
    """Verifica o zerofill para sec > 9 (ex: sec=10 → '0010')."""
    # Insere 10 registros para chegar ao sec=10
    for i in range(9):
        gerar_codigo("N", "A", PAIS_TESTE)
    codigo, sec = gerar_codigo("N", "B", PAIS_TESTE)
    assert sec == 10
    parte_numerica = codigo[3:7]
    assert parte_numerica == "0010", f"Zerofill para 10 deve ser '0010': '{parte_numerica}'"


# ── 3. Entradas inválidas ─────────────────────────────────────────────────────

def test_grupo_vazio_levanta_erro():
    with pytest.raises(ValueError, match="Grupo"):
        gerar_codigo("", "A", "BR")


def test_tipo_alimento_vazio_levanta_erro():
    with pytest.raises(ValueError, match="Tipo_Alimento"):
        gerar_codigo("C", "", "BR")


def test_pais_vazio_levanta_erro():
    with pytest.raises(ValueError, match="Pais"):
        gerar_codigo("C", "A", "")


def test_pais_com_mais_de_2_caracteres():
    with pytest.raises(ValueError, match="2 caracteres"):
        gerar_codigo("C", "A", "BRA")


def test_pais_com_menos_de_2_caracteres():
    with pytest.raises(ValueError, match="2 caracteres"):
        gerar_codigo("C", "A", "B")


# ── 4. Prevenção de duplicidade ───────────────────────────────────────────────

def test_codigos_gerados_sao_unicos():
    """Múltiplas chamadas para o mesmo grupo devem gerar códigos distintos."""
    codigos = [gerar_codigo("P", chr(65 + i), PAIS_TESTE)[0] for i in range(5)]
    assert len(codigos) == len(set(codigos)), "Todos os códigos gerados devem ser únicos."
