"""Componente <<grpc_service>> Log (Arquitectura 1).

Recibe eventos "url hit" por gRPC y los guarda en Log DB (SQLite: log.db).
Uso: python log_service.py
"""
import sqlite3
from concurrent import futures
from pathlib import Path

import grpc

import log_pb2
import log_pb2_grpc

DB_PATH = Path(__file__).parent / "log.db"
PUERTO = 50051


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS hits (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   timestamp TEXT NOT NULL,
                   short_url TEXT NOT NULL,
                   long_url TEXT NOT NULL
               )"""
        )


class LogService(log_pb2_grpc.LogServiceServicer):
    def RegistrarHit(self, request, context):
        with sqlite3.connect(DB_PATH) as con:
            con.execute(
                "INSERT INTO hits (timestamp, short_url, long_url) VALUES (?, ?, ?)",
                (request.timestamp, request.short_url, request.long_url),
            )
        print(f"[LOG] {request.timestamp} {request.short_url} -> {request.long_url}")
        return log_pb2.Ack(ok=True)


def main() -> None:
    init_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    log_pb2_grpc.add_LogServiceServicer_to_server(LogService(), server)
    server.add_insecure_port(f"[::]:{PUERTO}")
    server.start()
    print(f"Servicio Log gRPC escuchando en el puerto {PUERTO}")
    server.wait_for_termination()


if __name__ == "__main__":
    main()
