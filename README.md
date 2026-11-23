# Tarea 2 INF326 — URL Shortener

## Integrantes

| Nombre | Rol |
|---|---|
| Felipe Zagal | Entorno, certificados y Log gRPC. Revisión final y entrega. |
| Vicente Vizcarra | Implementación, pruebas y discusión de la Arquitectura 1. |
| Joaquín Navarro | Implementación, pruebas y discusión de la Arquitectura 2. |

## Pre-requisitos

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

Redirección temporal 302 y servicio Log que recibe un evento gRPC por cada redirección exitosa.

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

En una base vacía se espera un POST 201, tres redirecciones 302 con la cabecera `Cache-Control: no-store`, un 404 para un código inexistente y tres hits en Log DB. El visor muestra el total acumulado si ya había visitas.

## Arquitectura 2

Redirección **301** (permanente) + tácticas:
- *Controlar arribo de eventos*: rate limiter de LiteStar, 20 peticiones por minuto por IP (responde 429 al excederlo).
- *Mantener múltiples copias de datos*: caché de respuestas de LiteStar en `GET /{hash}`, 120 segundos.

**Terminal 1** · Inicia Shortener v2 en el puerto 8002.

```
cd arquitectura2
python shortener_v2.py
```

**Terminal 2** · Ejecuta la prueba desde la raíz con v2 recién iniciado y sin enviar otras solicitudes.

```
python pruebas/probar_v2.py
```

La prueba obtiene un POST 201 y tres GET 301. En la ráfaga posterior de treinta GET se esperan 16 respuestas 301 y 14 respuestas 429. Para verificar la caché del servidor, comprueba que la línea `[DB] Consultando` para el código probado aparece una sola vez en esa ejecución. Reinicia v2 antes de repetir la prueba.

## Consideraciones de la implementación

- Ambas arquitecturas reciben una URL larga en `POST /shorten` con el campo `long_url` y devuelven `short_url` y `hash`. `GET /{hash}` redirige a la URL original.
- SQLite crea `shortener_v1.db`, `shortener_v2.db` y `log.db` al iniciar los servicios. En cada base de acortamiento nueva, el ID parte en `597652313` y se codifica en Base62 como `eRgfR`. Enviar de nuevo la misma URL normalizada devuelve el mismo código.
- Si una URL se entrega sin `http://` ni `https://`, se le agrega `https://` para redirigir a una dirección absoluta.
- Las dos versiones usan HTTPS con un certificado autofirmado para pruebas locales. Los scripts usan `verify=False` para conectarse a esos servicios. La documentación Swagger se publica en `/schema/swagger` en cada puerto. La posibilidad de observar la caché del 301 en el navegador depende del cliente y de la confianza del certificado.
- V1 devuelve 302 con `Cache-Control: no-store` y envía el evento en segundo plano con la hora UTC, la URL corta y la URL de destino. Si Log está caído, la redirección se mantiene y aparece `[WARN]`. El cliente gRPC usa `localhost:50051` sin TLS en este despliegue local.
- En v2, el límite de 20 peticiones por minuto por IP y la caché de 120 segundos viven en memoria del proceso. El reinicio restablece ambos.
- Los certificados, el entorno virtual y las bases de datos se generan localmente y están excluidos de Git. Para detener un servicio, usa Ctrl+C en su terminal.

Para la comparación y la propuesta de IDs distribuidos, consulta [DISCUSION.md](DISCUSION.md).
