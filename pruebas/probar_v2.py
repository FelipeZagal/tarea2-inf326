"""Prueba la Arquitectura 2 (301 + rate limiter + caché).

Requisito: shortener_v2.py corriendo (reinícialo antes de probar, para partir con
el contador del rate limiter en cero).
Uso:  python pruebas/probar_v2.py
"""
import httpx

BASE = "https://localhost:8002"
LONG = "usm.cl/informatica/postulaciones-a-postgrado/2025/magiste-en-ingenieria-informatica/"

with httpx.Client(verify=False) as c:
    r = c.post(f"{BASE}/shorten", json={"long_url": LONG})
    print("POST /shorten ->", r.status_code, r.json())
    hash_ = r.json()["hash"]

    print("\n1) Redirección permanente y caché")
    for i in range(3):
        r = c.get(f"{BASE}/{hash_}")
        print(f"  GET /{hash_} ->", r.status_code, "Location:", r.headers.get("location"))
        assert r.status_code == 301, "Se esperaba 301"
    print("  -> En la terminal del servidor el mensaje [DB] debe salir UNA sola vez.")

    print("\n2) Rate limiter: 30 peticiones seguidas")
    codigos = [c.get(f"{BASE}/{hash_}").status_code for _ in range(30)]
    print("  301:", codigos.count(301), " 429:", codigos.count(429))
    assert 429 in codigos, "Se esperaba al menos un 429 (Too Many Requests)"
    print("  -> Al superar el límite el servidor responde 429 Too Many Requests.")

print("\nOK")