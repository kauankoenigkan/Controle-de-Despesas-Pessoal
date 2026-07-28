import database as db
import pandas as pd
import sqlite3 as mConn
from rich.console import Console
from rich.table import Table

conn = mConn.connect("KauanKoenigkan.db")

tabelas = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table';", conn
)

dados = pd.read_sql_query("SELECT * FROM usuarios;", conn)

conn.close()

console = Console()

tabela_rich = Table(title="Usuários cadastrados")

for coluna in dados.columns:
    tabela_rich.add_column(str(coluna), style="cyan", header_style="bold magenta")

for _, linha in dados.iterrows():
    tabela_rich.add_row(*[str(valor) for valor in linha])

console.print(tabela_rich)

conexao = mConn.connect("KauanKoenigkan.db")
cursor = conexao.execute("SELECT * FROM renda_mensal")
for linha in cursor.fetchall():
    print(linha)
conexao.close()