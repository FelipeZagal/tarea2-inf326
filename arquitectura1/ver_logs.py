"""Muestra los "url hits" guardados en Log DB. Uso: python ver_logs.py"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "log.db"
if not DB_PATH.exists():
    print("Aún no existe log.db (¿levantaste log_service.py?)")
else:
    with sqlite3.connect(DB_PATH) as con:
        filas = con.execute("SELECT id, timestamp, short_url, long_url FROM hits").fetchall()
    print(f"{len(filas)} hits registrados")
    for fila in filas:
        print(fila)
