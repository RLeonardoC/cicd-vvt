-- ============================================================
--  setup.sql  –  Banco de dados para Códigos Sequenciais
--  UniDomBosco  |  VV&T  |  Prof. Osmar Betazzi Dordal
-- ============================================================

CREATE DATABASE IF NOT EXISTS food_codes
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE food_codes;

-- Tabela principal
CREATE TABLE IF NOT EXISTS codigos_sequenciais (
    id            INT           NOT NULL AUTO_INCREMENT,
    codigo        VARCHAR(10)   NOT NULL,
    sec           INT           NOT NULL,
    Grupo         CHAR(1)       NOT NULL,
    Tipo_Alimento CHAR(1)       NOT NULL,
    Pais          CHAR(2)       NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_codigo (codigo),
    -- garante que não existam dois registros com mesmo grupo+sec+pais
    UNIQUE KEY uq_grupo_sec_pais (Grupo, sec, Pais)
) ENGINE=InnoDB;

-- ── Dados iniciais de referência ──────────────────────────────────────────────
INSERT INTO codigos_sequenciais (codigo, sec, Grupo, Tipo_Alimento, Pais) VALUES
  ('BRC0001A', 1, 'C', 'A', 'BR'),
  ('BRD0001I', 1, 'D', 'I', 'BR'),
  ('BRA0001K', 1, 'A', 'K', 'BR'),
  ('BRF0001F', 1, 'F', 'F', 'BR'),
  ('BRG0001A', 1, 'G', 'A', 'BR'),
  ('BRC0002A', 2, 'C', 'A', 'BR'),
  ('BRD0002K', 2, 'D', 'K', 'BR'),
  ('BRF0002A', 2, 'F', 'A', 'BR'),
  ('BRC0003C', 3, 'C', 'C', 'BR');
