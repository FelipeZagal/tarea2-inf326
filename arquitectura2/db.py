"""Shortener DB: guarda la 3-tupla <id, hash, long_url> en SQLite.

El id es autoincremental y parte en 597652313 (pedido por el enunciado).
El hash es el id codificado en base62 (pybase62).
"""
import sqlite3
from pathlib import Path

import base62

ID_INICIAL = 597652313


class ShortenerDB:
    def __init__(self, ruta: Path):
        self.ruta = ruta
        with self._con() as con:
            con.execute(
                """CREATE TABLE IF NOT EXISTS urls (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       hash TEXT UNIQUE,
                       long_url TEXT NOT NULL
                   )"""
            )
            # Si la tabla nunca ha tenido filas, fijamos el contador para que
            # el primer id sea ID_INICIAL.
            existe = con.execute(
                "SELECT 1 FROM sqlite_sequence WHERE name = 'urls'"
            ).fetchone()
            if not existe:
                con.execute(
                    "INSERT INTO sqlite_sequence (name, seq) VALUES ('urls', ?)",
                    (ID_INICIAL - 1,),
                )

    def _con(self) -> sqlite3.Connection:
        return sqlite3.connect(self.ruta)

    def crear(self, long_url: str) -> str:
        """Guarda long_url y retorna su hash. Si ya existía, retorna el mismo hash."""
        with self._con() as con:
            fila = con.execute(
                "SELECT hash FROM urls WHERE long_url = ?", (long_url,)
            ).fetchone()
            if fila:
                return fila[0]
            cur = con.execute("INSERT INTO urls (long_url) VALUES (?)", (long_url,))
            nuevo_id = cur.lastrowid
            hash_ = base62.encode(nuevo_id)
            con.execute("UPDATE urls SET hash = ? WHERE id = ?", (hash_, nuevo_id))
            return hash_

    def buscar(self, hash_: str) -> str | None:
        """Retorna la long_url asociada al hash, o None si no existe."""
        with self._con() as con:
            fila = con.execute(
                "SELECT long_url FROM urls WHERE hash = ?", (hash_,)
            ).fetchone()
        return fila[0] if fila else None