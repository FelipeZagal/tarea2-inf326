"""Prueba la Arquitectura 1 (Shortener v1 + Log gRPC).

Requisitos: log_service.py y shortener_v1.py corriendo.
Uso:  python pruebas/probar_v1.py
"""
import time

import httpx

BASE = "https://localhost:8001"
LONG = "usm.cl/informatica/postulaciones-a-postgrado/2025/magiste-en-ingenieria-informatica/"

# verify=False porque el certificado es autofirmado
with httpx.Client(verify=False) as c:
    r = c.post(f"{BASE}/shorten", json={"long_url": LONG})
    print("POST /shorten ->", r.status_code, r.json())
    hash_ = r.json()["hash"]

    for i in range(3):
        r = c.get(f"{BASE}/{hash_}")  # httpx no sigue redirecciones por defecto
        print(f"GET /{hash_} ->", r.status_code, "Location:", r.headers.get("location"))
        assert r.status_code == 302, "Se esperaba 302"

    r = c.get(f"{BASE}/noexiste")
    print("GET /noexiste ->", r.status_code)

time.sleep(1)
print("\nOK. Revisa los hits con:  python arquitectura1/ver_logs.py")