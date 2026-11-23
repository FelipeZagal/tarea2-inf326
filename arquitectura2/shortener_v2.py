"""Componente Shortener v2 (<<http_endpoint>>) — Arquitectura 2.

- POST /shorten  {"long_url": "..."}  -> {"short_url": "...", "hash": "..."}
- GET  /{hash}   -> redirect 301 (permanente: el navegador puede guardarla en caché)

Tácticas:
- "Controlar arribo de eventos": rate limiter (RateLimitConfig) -> HTTP 429 al exceder el límite
- "Mantener múltiples copias de datos": caché de respuestas de LiteStar en el GET

Uso:  python shortener_v2.py
"""
from dataclasses import dataclass
from pathlib import Path

import uvicorn
from litestar import Litestar, Request, get, post
from litestar.config.response_cache import ResponseCacheConfig
from litestar.exceptions import NotFoundException
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.response import Redirect

from db import ShortenerDB

AQUI = Path(__file__).parent
CERTS = AQUI.parent / "certs"
PUERTO = 8002

LIMITE_POR_MINUTO = 20   # peticiones por cliente (IP) por minuto
CACHE_SEGUNDOS = 120     # tiempo que una redirección queda en la caché del servidor

db = ShortenerDB(AQUI / "shortener_v2.db")


@dataclass
class ShortenIn:
    long_url: str


@dataclass
class ShortenOut:
    short_url: str
    hash: str


def normalizar(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


@post("/shorten")
async def acortar(data: ShortenIn, request: Request) -> ShortenOut:
    hash_ = db.crear(normalizar(data.long_url))
    return ShortenOut(short_url=f"{request.base_url}{hash_}", hash=hash_)


@get("/{hash_:str}", cache=CACHE_SEGUNDOS)
async def redirigir(hash_: str) -> Redirect:
    # Este print solo aparece cuando la respuesta NO viene de la caché.
    print(f"[DB] Consultando la base de datos por '{hash_}'")
    long_url = db.buscar(hash_)
    if long_url is None:
        raise NotFoundException(f"La URL corta '{hash_}' no existe")
    return Redirect(path=long_url, status_code=301)  # permanente


rate_limit = RateLimitConfig(
    rate_limit=("minute", LIMITE_POR_MINUTO),
    exclude=["/schema"],  # no limitar la documentación Swagger
)

app = Litestar(
    route_handlers=[acortar, redirigir],
    middleware=[rate_limit.middleware],
    response_cache_config=ResponseCacheConfig(default_expiration=CACHE_SEGUNDOS),
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PUERTO,
        ssl_certfile=str(CERTS / "cert.pem"),
        ssl_keyfile=str(CERTS / "key.pem"),
    )