# Traspaso de turnos — Tarea 2 INF326

## Turno 1 — Felipe Zagal — 22-11-2026 00:33

- **Qué hice:** entorno, certificados y servicio Log gRPC.
- **Cómo probarlo:** desde la raíz, activa el entorno. En una terminal, entra en `arquitectura1` y corre `python log_service.py`. En otra terminal, desde la raíz con el entorno activado, corre `python arquitectura1\ver_logs.py`.
- **Resultado de las pruebas:** Se instalaron las dependencias con Python 3.14.5 y se generaron los certificados y los dos archivos gRPC. Log inició en el puerto 50051, se comprobó la conexión local y el visor mostró `0 hits registrados` en la base nueva.
- **Problemas o dudas pendientes:** Ninguno para el turno 1.
- **Para el siguiente:** el Log escucha en el puerto 50051. La prueba integrada con visitas reales se hace en el turno 2.

## Turno 2 — Vicente Vizcarra — 22-11-2026 17:06

- **Qué hice:** creé `arquitectura1/db.py`, `arquitectura1/shortener_v1.py`, `pruebas/probar_v1.py` y `DISCUSION.md` (sección Arquitectura 1); actualicé `README.md` con las instrucciones de la Arquitectura 1.
- **Cómo probarlo:** abrir 3 terminales con el entorno virtual activado (`.\.venv\Scripts\Activate.ps1`):
  1. Terminal 1: `cd arquitectura1` y luego `python log_service.py`
  2. Terminal 2: `cd arquitectura1` y luego `python shortener_v1.py`
  3. Terminal 3 (en la raíz): `python pruebas\probar_v1.py` y luego `python arquitectura1\ver_logs.py`
- **Resultado de las pruebas:** `POST /shorten` devolvió `201` con hash `eRgfR`, los 3 `GET /eRgfR` respondieron `302`, `GET /noexiste` devolvió `404` y `ver_logs.py` mostró los 3 hits registrados. También se validó el desacople deteniendo `log_service.py` (las redirecciones siguen dando `302` y aparece `[WARN]` en consola) y la prueba desde Swagger en el navegador.
- **Problemas o dudas pendientes:** ninguno.
- **Para el siguiente:** antes de empezar el Turno 3, corre las pruebas de arriba para confirmar que la Arquitectura 1 anda bien en tu PC. Luego copia `arquitectura1/db.py` hacia `arquitectura2/db.py` y levanta Shortener v2 en el puerto 8002.

## Turno 3 — Joaquín Navarro — dom 22, 21:33
- Qué hice: arquitectura2/db.py (copia), arquitectura2/shortener_v2.py, pruebas/probar_v2.py, sección Arq. 2 del README y de DISCUSION.md
- Cómo probarlo: `cd arquitectura2` + `python shortener_v2.py`; en otra terminal desde la raíz `python pruebas\probar_v2.py`
- Resultado de las pruebas: 3x 301, rate limiter 301: 16 / 429: 14, [DB] aparece una sola vez (caché funcionando)
- Problemas o dudas pendientes: ninguno
- Para el siguiente: faltan las secciones 3 y 4 de DISCUSION.md, las "Consideraciones" del README y la revisión final. Si se corre probar_v2 dos veces seguidas salen puros 429: reiniciar el servidor o esperar 1 minuto.

## Turno 4 — Felipe Zagal — 22-11-2026 21:51

- **Qué hice:** completé las consideraciones del README, la comparación para la USM y el bonus de IDs distribuidos. Corregí los roles del README y agregué la cabecera `Cache-Control: no-store` en los 302 de v1.
- **Cómo probarlo:** instala las dependencias y genera los certificados desde una clonación nueva. Sigue las instrucciones del README y ejecuta `python pruebas/probar_v1.py`, `python arquitectura1/ver_logs.py` y `python pruebas/probar_v2.py` con sus servicios levantados.
- **Resultado de las pruebas:** desde bases vacías, v1 devolvió 201 y el primer código `eRgfR`, tres 302 con destino correcto y `no-store`, un 404 y tres hits registrados por gRPC. El 302 siguió funcionando al detener Log y apareció `[WARN]`. V2 devolvió 201 y `eRgfR`, 19 redirecciones 301 con una sola lectura de SQLite y 14 respuestas 429 al superar el límite.
- **Problemas o dudas pendientes:** ninguno en las pruebas de la versión final.
