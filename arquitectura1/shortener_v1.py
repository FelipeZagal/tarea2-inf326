"""Componente Shortener v1 (<<http_endpoint>> + <<grpc_client>>) — Arquitectura 1.

- POST /shorten  {"long_url": "..."}  -> {"short_url": "...", "hash": "..."}
- GET  /{hash}   -> redirect 302 (temporal) + envía evento "url hit" al servicio Log por gRPC

Uso:  python shortener_v1.py   (antes levantar log_service.py)
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import grpc
import uvicorn
from litestar import Litestar, Request, get, post
from litestar.background_tasks import BackgroundTask
from litestar.exceptions import NotFoundException
from litestar.response import Redirect

import log_pb2
import log_pb2_grpc
from db import ShortenerDB

AQUI = Path(__file__).parent
CERTS = AQUI.parent / "certs"
PUERTO = 8001
LOG_GRPC = "localhost:50051"

db = ShortenerDB(AQUI / "shortener_v1.db")

# Cliente gRPC (<<grpc_client>>): un canal compartido hacia el servicio Log.
canal = grpc.insecure_channel(LOG_GRPC)
log_stub = log_pb2_grpc.LogServiceStub(canal)


@dataclass
class ShortenIn:
    long_url: str


@dataclass
class ShortenOut:
    short_url: str
    hash: str


def normalizar(url: str) -> str:
    # Sin esquema, el navegador trataría la redirección como ruta relativa.
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def enviar_hit(short_url: str, long_url: str) -> None:
    """Envía el evento "url hit" al servicio Log.

    Corre como tarea en segundo plano DESPUÉS de responder al navegador, así la
    redirección no espera al Log. Si Log está caído, solo se avisa por consola.
    """
    hit = log_pb2.UrlHit(
        timestamp=datetime.now(timezone.utc).isoformat(),
        short_url=short_url,
        long_url=long_url,
    )
    try:
        log_stub.RegistrarHit(hit, timeout=2)
    except grpc.RpcError as e:
        print(f"[WARN] No se pudo registrar el hit en Log: {e.code()}")


@post("/shorten")
async def acortar(data: ShortenIn, request: Request) -> ShortenOut:
    hash_ = db.crear(normalizar(data.long_url))
    return ShortenOut(short_url=f"{request.base_url}{hash_}", hash=hash_)


@get("/{hash_:str}")
async def redirigir(hash_: str, request: Request) -> Redirect:
    long_url = db.buscar(hash_)
    if long_url is None:
        raise NotFoundException(f"La URL corta '{hash_}' no existe")
    return Redirect(
        path=long_url,
        status_code=302,
        headers={"Cache-Control": "no-store"},
        background=BackgroundTask(enviar_hit, str(request.url), long_url),
    )


app = Litestar(route_handlers=[acortar, redirigir])

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PUERTO,
        ssl_certfile=str(CERTS / "cert.pem"),
        ssl_keyfile=str(CERTS / "key.pem"),
    )
