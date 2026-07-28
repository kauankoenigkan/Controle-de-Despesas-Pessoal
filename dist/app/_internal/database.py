import sqlite3 as mConn
from hashlib import sha256
from datetime import date, timedelta
import os


BASE_DIR = os.getenv("FLET_APP_STORAGE_DATA") or os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "KauanKoenigkan.db")

def conectar():
    return mConn.connect(DB_PATH)

def criar_tabela():
    conexao = conectar()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            IDusuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR UNIQUE NOT NULL,
            senha VARCHAR NOT NULL)
        """)
    conexao.commit()
    conexao.close()

def usuarios():
    conexao = conectar()
    cursor = conexao.execute("SELECT nome FROM usuarios LIMIT 1")
    result = cursor.fetchone()
    conexao.close()
    return result

def buscar_usuario(nome):
    conexao = conectar()
    cursor = conexao.execute("SELECT nome FROM usuarios WHERE nome = ?",
    (nome,))
    result = cursor.fetchone()
    conexao.close()
    return result

def cadastrar_usuario(nome, senha):
    senha_hash = sha256(senha.encode()).hexdigest()

    conexao = conectar()
    cursor = conexao.execute("INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
    (nome, senha_hash))
    conexao.commit()
    conexao.close()

def verificar_login(nome, senha):
    senha_hash = sha256(senha.encode()).hexdigest()

    conexao = conectar()
    cursor = conexao.execute(
        "SELECT IDusuario, nome FROM usuarios WHERE nome = ? AND senha = ?",
        (nome, senha_hash)
    )
    result = cursor.fetchone()
    conexao.close()
    return result

# ============================================================================ TABELA DE RENDA MENSAL =======================================================================================

def criar_tabela_renda():
    conexao = conectar()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS renda_mensal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            IDusuario INTEGER NOT NULL,
            mes_referencia TEXT NOT NULL,
            salario_fixo REAL NOT NULL,
            renda_extra REAL NOT NULL,
            pct_obrigacoes REAL DEFAULT 70,
            pct_investimento REAL DEFAULT 20,
            pct_lazer REAL DEFAULT 10,
            UNIQUE (IDusuario, mes_referencia),
            FOREIGN KEY (IDusuario) REFERENCES usuarios (IDusuario)
        )
    """)
    
    colunas = ["pct_obrigacoes REAL DEFAULT 70", "pct_investimento REAL DEFAULT 20", "pct_lazer REAL DEFAULT 10"]
    for coluna in colunas:
        try:
            conexao.execute(f"ALTER TABLE renda_mensal ADD COLUMN {coluna}")
        except mConn.OperationalError:
            pass  # Ignora caso a coluna já exista
            
    conexao.commit()
    conexao.close()

def periodo_atual():
    hoje = date.today()
    if hoje.day >= 6:
        referencia = hoje
    else:
        primeiro_dia_deste_mes = hoje.replace(day=1)
        referencia = primeiro_dia_deste_mes - timedelta(days=1)
    return referencia.strftime("%Y-%m")


def periodo_anterior(periodo_referencia):
    ano, mes = map(int, periodo_referencia.split("-"))
    primeiro_dia = date(ano, mes, 1)
    dia_anterior = primeiro_dia - timedelta(days=1)
    return dia_anterior.strftime("%Y-%m")

def buscar_renda_mes(id_usuario, mes_referencia):
    conexao = conectar()
    cursor = conexao.execute(
        "SELECT salario_fixo, renda_extra FROM renda_mensal WHERE IDusuario = ? AND mes_referencia = ?",
        (id_usuario, mes_referencia)
    )
    result = cursor.fetchone()
    conexao.close()
    return result

def salvar_renda_mes(id_usuario, mes_referencia, salario_fixo, renda_extra):
    conexao = conectar()
    conexao.execute(
        "INSERT INTO renda_mensal (IDusuario, mes_referencia, salario_fixo, renda_extra) VALUES (?, ?, ?, ?)",
        (id_usuario, mes_referencia, salario_fixo, renda_extra)
    )
    conexao.commit()
    conexao.close()

def criar_tabela_lancamentos():
    conexao = conectar()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            IDusuario INTEGER NOT NULL,
            mes_referencia TEXT NOT NULL,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY (IDusuario) REFERENCES usuarios (IDusuario)
        )
    """)
    conexao.commit()
    colunas_existentes = [linha[1] for linha in conexao.execute("PRAGMA table_info(lancamentos)")]

    if "bloco" not in colunas_existentes:
        conexao.execute("ALTER TABLE lancamentos ADD COLUMN bloco TEXT")

    if "subtipo" not in colunas_existentes:
        conexao.execute("ALTER TABLE lancamentos ADD COLUMN subtipo TEXT")

    conexao.commit()
    conexao.close()

def adicionar_lancamento(id_usuario, mes_referencia, tipo, categoria, descricao, valor, bloco, subtipo=None):
    hoje = date.today().strftime("%Y-%m-%d")
    conexao = conectar()
    conexao.execute(
        """INSERT INTO lancamentos (IDusuario, mes_referencia, tipo, categoria, descricao, valor, data, bloco, subtipo)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (id_usuario, mes_referencia, tipo, categoria, descricao, valor, hoje, bloco, subtipo)
    )
    conexao.commit()
    conexao.close()

def listar_lancamentos(id_usuario, mes_referencia):
    conexao = conectar()
    cursor = conexao.execute(
        """SELECT tipo, categoria, descricao, valor, data FROM lancamentos
           WHERE IDusuario = ? AND mes_referencia = ?
           ORDER BY id DESC""",
        (id_usuario, mes_referencia)
    )
    result = cursor.fetchall()
    conexao.close()
    return result

def listar_todos_lancamentos(id_usuario):
    conexao = conectar()
    cursor = conexao.execute(
        """SELECT tipo, categoria, descricao, valor, data FROM lancamentos
           WHERE IDusuario = ?
           ORDER BY data DESC, id DESC""",
        (id_usuario,)
    )
    result = cursor.fetchall()
    conexao.close()
    return result

def somar_gastos_por_bloco(id_usuario, mes_referencia):
    conexao = conectar()
    cursor = conexao.execute(
        """SELECT bloco, subtipo, SUM(valor) FROM lancamentos
           WHERE IDusuario = ? AND mes_referencia = ? AND tipo = 'Gasto'
           GROUP BY bloco, subtipo""",
        (id_usuario, mes_referencia)
    )
    resultado = cursor.fetchall()
    conexao.close()
    return resultado

def calcular_saldo_periodo(id_usuario, periodo_referencia):
    renda_salva = buscar_renda_mes(id_usuario, periodo_referencia)
    if renda_salva is None:
        return 0

    salario_fixo, renda_extra = renda_salva
    renda_total = salario_fixo + renda_extra

    conexao = conectar()
    cursor = conexao.execute(
        """SELECT
               SUM(CASE WHEN tipo = 'Gasto' THEN valor ELSE 0 END) AS total_gastos,
               SUM(CASE WHEN tipo = 'Entrada' THEN valor ELSE 0 END) AS total_entradas
           FROM lancamentos
           WHERE IDusuario = ? AND mes_referencia = ?""",
        (id_usuario, periodo_referencia)
    )
    total_gastos, total_entradas = cursor.fetchone()
    conexao.close()

    total_gastos = total_gastos or 0
    total_entradas = total_entradas or 0

    saldo = renda_total + total_entradas - total_gastos
    return saldo

def somar_entradas_extras(id_usuario, periodo_atual):
    conexao = conectar()
    cursor = conexao.execute(
        """SELECT COALESCE(SUM(valor), 0) FROM lancamentos
           WHERE IDusuario = ? AND mes_referencia = ? AND tipo = 'Entrada'""",
        (id_usuario, periodo_atual)
    )
    result = cursor.fetchone()[0]
    conexao.close()
    return result

def listar_todos_lancamentos(id_usuario):
    conexao = conectar()
    cursor = conexao.execute(
        """SELECT id, tipo, categoria, descricao, valor, data FROM lancamentos
           WHERE IDusuario = ?
           ORDER BY id DESC""",
        (id_usuario,)
    )
    result = cursor.fetchall()
    conexao.close()
    return result

def deletar_lancamento(id_lancamento):
    conexao = conectar()
    conexao.execute(
        "DELETE FROM lancamentos WHERE id = ?",
        (id_lancamento,)
    )
    conexao.commit()
    conexao.close()

def buscar_porcentagens(id_usuario, periodo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT pct_obrigacoes, pct_investimento, pct_lazer FROM renda_mensal WHERE IDusuario = ? AND mes_referencia = ?",
        (id_usuario, periodo),
    )
    res = cursor.fetchone()
    conn.close()
    if res and None not in res:
        return res
    return (70.0, 20.0, 10.0)


def salvar_porcentagens(id_usuario, periodo, pct_ob, pct_in, pct_lz):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE renda_mensal 
        SET pct_obrigacoes = ?, pct_investimento = ?, pct_lazer = ? 
        WHERE IDusuario = ? AND mes_referencia = ?
    """,
        (pct_ob, pct_in, pct_lz, id_usuario, periodo),
    )
    conn.commit()
    conn.close()

def listar_lancamentos_por_mes_ano(id_usuario, periodo_referencia):
    partes = periodo_referencia.split("-")
    if len(partes[0]) == 2:
        periodo_referencia = f"{partes[1]}-{partes[0]}"

    conexao = conectar()
    cursor = conexao.execute(
        """SELECT id, tipo, categoria, descricao, valor, data 
           FROM lancamentos
           WHERE IDusuario = ? AND (mes_referencia = ? OR data LIKE ?)
           ORDER BY id DESC""",
        (id_usuario, periodo_referencia, f"{periodo_referencia}%")
    )
    result = cursor.fetchall()
    conexao.close()
    return result

def listar_lancamentos_para_exportar(id_usuario, periodo_referencia):
    partes = periodo_referencia.split("-")
    if len(partes[0]) == 2:
        periodo_referencia = f"{partes[1]}-{partes[0]}"

    conexao = conectar()
    cursor = conexao.execute(
        """SELECT tipo, categoria, descricao, valor, data 
           FROM lancamentos
           WHERE IDusuario = ? AND (mes_referencia = ? OR data LIKE ?)
           ORDER BY data DESC""",
        (id_usuario, periodo_referencia, f"{periodo_referencia}%")
    )
    result = cursor.fetchall()
    conexao.close()
    return result