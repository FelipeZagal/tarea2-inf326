# Tarea 2 INF326 — URL Shortener

## Integrantes

| Nombre | Rol |
|---|---|
| Felipe Zagal | 2021XXXXX-X |
| Vicente Vizcarra | 202173036-2 |
| Joaquín Navarro | 202173125-X |

## Pre-requisitos

- Python 3.10 o superior
- Git

## Instalación (una sola vez)

```
git clone https://github.com/FelipeZagal/tarea2-inf326.git
cd tarea2-inf326
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
python gen_cert.py           # genera certs/cert.pem y certs/key.pem (autofirmados)
```

## Arquitectura 1

Redirección 302 (temporal) + componente gRPC Log que recibe un evento "url hit" (timestamp + URL) por cada visita.

Levantar (2 terminales con el entorno activado):
```

Terminal 1: servicio Log gRPC (puerto 50051)
cd arquitectura1
python log_service.py

Terminal 2: Shortener v1 (https://localhost:8001)
cd arquitectura1
python shortener_v1.py
```

Probar (Terminal 3, desde la raíz):
```
python pruebas/probar_v1.py
python arquitectura1/ver_logs.py
```
También desde el navegador en https://localhost:8001/schema/swagger (aceptar la advertencia del certificado autofirmado).

## Arquitectura 2

(la completa la Persona 3)

## Consideraciones de la implementación

(se completa en el turno 4)
