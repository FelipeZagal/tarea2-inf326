# Tarea 2 INF326 — URL Shortener

## Integrantes

| Nombre | Rol |
|---|---|
| Felipe Zagal | 202121082-2 |
| Vicente Vizcarra | 202173036-2 |
| Joaquín Navarro | 202173125-3 |

## Requisitos

- Python 3.10 o superior
- Git

## Instalación (una sola vez)

```powershell
git clone https://github.com/FelipeZagal/tarea2-inf326.git
cd tarea2-inf326
python -m venv .venv
```

Activa el entorno desde la raíz del repositorio en cada terminal que uses.

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Con el entorno activado, instala las dependencias y genera los certificados una vez.

```
python -m pip install -r requirements.txt
python gen_cert.py
```

## Arquitectura 1

Redirección temporal 302 y registro de visitas por gRPC.

**Terminal 1** · Inicia Log en el puerto 50051 y espera el mensaje de arranque.

```
cd arquitectura1
python log_service.py
```

**Terminal 2** · Inicia Shortener v1 en el puerto 8001.

```
cd arquitectura1
python shortener_v1.py
```

**Terminal 3** · Ejecuta la prueba desde la raíz.

```
python pruebas/probar_v1.py
python arquitectura1/ver_logs.py
```

La prueba devuelve un 201, tres 302 y un 404. En una base vacía, el visor muestra `3 hits registrados`. Si ya había visitas, muestra el total acumulado.

## Arquitectura 2

Redirección permanente 301 con dos tácticas de Litestar.

- *Controlar arribo de eventos* con un límite de 20 peticiones por minuto por IP. Al superarlo, el servicio responde 429.
- *Mantener múltiples copias de datos* con una caché de 120 segundos para las respuestas de `GET /{hash}`.

**Terminal 1** · Inicia Shortener v2 en el puerto 8002.

```
cd arquitectura2
python shortener_v2.py
```

**Terminal 2** · Ejecuta la prueba desde la raíz con v2 recién iniciado y sin enviar otras solicitudes.

```
python pruebas/probar_v2.py
```

En la ráfaga de 30 GET, la prueba debe imprimir `301: 16  429: 14`. En la terminal de v2, debe aparecer una sola línea `[DB] Consultando` para ese código. Reinicia v2 antes de repetir la prueba.

## Consideraciones de la implementación

- `POST /shorten` recibe `long_url` y devuelve `short_url` y `hash`. `GET /{hash}` redirige al destino.
- Cada acortador tiene su base SQLite. En una base nueva, la primera URL recibe el ID `597652313` y el código Base62 `eRgfR`. La misma URL normalizada reutiliza el código. Si falta el esquema, se agrega `https://`.
- V1 responde con `Cache-Control: no-store` y manda en segundo plano la hora UTC y las dos URLs. Log guarda los hits en `log.db` y escucha por gRPC sin TLS en el despliegue local. Si se detiene Log, v1 sigue redirigiendo y muestra `[WARN]`.
- V2 guarda la caché y el contador en memoria. Ambos se reinician al volver a levantar el servicio. Si el navegador también guarda un 301, ese comportamiento depende del cliente y del certificado.
- Las dos versiones usan HTTPS con el certificado autofirmado que genera `gen_cert.py`. Los scripts de prueba locales usan `verify=False`. Swagger está en `/schema/swagger`.
- Los archivos `.db`, el entorno virtual y los certificados quedan fuera de Git. Para detener un servicio, presiona Ctrl+C en su terminal.

Para la comparación y la propuesta de IDs distribuidos, consultar [DISCUSION.md](DISCUSION.md).
