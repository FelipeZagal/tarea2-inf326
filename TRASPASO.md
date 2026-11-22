# Traspaso de turnos — Tarea 2 INF326

## Turno 1 — Felipe Zagal — 22-11-2026 00:33

- **Qué hice:** entorno, certificados y servicio Log gRPC.
- **Cómo probarlo:** desde la raíz, activa el entorno. En una terminal, entra en `arquitectura1` y corre `python log_service.py`. En otra terminal, desde la raíz con el entorno activado, corre `python arquitectura1\ver_logs.py`.
- **Resultado de las pruebas:** Se instalaron las dependencias con Python 3.14.5 y se generaron los certificados y los dos archivos gRPC. Log inició en el puerto 50051, se comprobó la conexión local y el visor mostró `0 hits registrados` en la base nueva.
- **Problemas o dudas pendientes:** Ninguno para el turno 1.
- **Para el siguiente:** el Log escucha en el puerto 50051. La prueba integrada con visitas reales se hace en el turno 2.
