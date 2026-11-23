# Discusión de trade-offs — Tarea 2 INF326

## 1. Arquitectura 1: redirección 302 + servicio Log gRPC

### Beneficios

El principal beneficio de esta arquitectura es la **analítica completa**. Al responder con un código HTTP `302` (redirección temporal), se le indica al navegador que no almacene la redirección en su caché local, forzándolo a consultar al servidor en cada visita. Esto permite que la USM registre con exactitud cuántas veces y en qué horario se accede a cada enlace acortado, lo cual resulta especialmente útil para medir el alcance e impacto de campañas específicas, como un proceso de postulaciones al magíster o la difusión de eventos universitarios.

Adicionalmente, la arquitectura ofrece un buen nivel de **desacople** al aislar el registro de visitas en un servicio independiente (`Log`) comunicado mediante un contrato explícito (`log.proto`) sobre gRPC. Como el envío del evento `"url hit"` se ejecuta en segundo plano (`BackgroundTask`) una vez enviada la respuesta `302`, la llamada al servicio de analítica no agrega latencia perceptible a la redirección del usuario. Esto también evita que una falla en el registro interrumpa el servicio principal: tal como se verificó en las pruebas de desacople, si el servicio `Log` se cae, el acortador continúa redirigiendo sin problemas y solo emite una advertencia en consola.

### Trade-offs

Como contrapartida, evitar el caché del navegador genera **mayor carga y latencia**. Debido a que los clientes nunca reutilizan una redirección previa, el 100% del tráfico impacta directamente al servicio `Shortener v1` y a su base de datos, lo que se traduce en mayor consumo de recursos y mayores costos de infraestructura bajo alta demanda. A esto se suma una **mayor complejidad operativa**, ya que el equipo debe desplegar, monitorear y mantener dos servicios distintos, dos bases de datos independientes (`shortener_v1.db` y `log.db`) y la evolución del contrato gRPC que los vincula.

Finalmente, existen compromisos en **confiabilidad de los eventos y seguridad interna**. Por un lado, al no existir persistencia intermedia ni políticas de reintento, cualquier evento `"url hit"` enviado mientras el servicio `Log` está caído se pierde definitivamente; en un entorno real esto debería mitigarse introduciendo reintentos o una cola de mensajes (como RabbitMQ) para garantizar la entrega eventual. Por otro lado, el canal gRPC opera actualmente sin TLS (`insecure_channel`), lo cual es razonable mientras ambos componentes vivan en el mismo nodo de despliegue, pero en un escenario productivo con nodos separados requeriría habilitar TLS o mTLS para proteger la comunicación interna.

## 2. Arquitectura 2: redirección 301 + rate limiter + caché

### Beneficios

En primer lugar, esta arquitectura ofrece un **mejor rendimiento**. Al responder con un código 301, el navegador guarda la redirección y en las visitas siguientes ya no contacta al servicio `Shortener v2`. Para los usuarios que visitan el link por primera vez, la caché de respuestas de LiteStar (táctica *Mantener múltiples copias de datos*) evita consultar la base de datos. En nuestras pruebas, la BD se consultó una sola vez para 19 redirecciones exitosas, lo que reduce la latencia y la carga sobre `shortener_v2.db`.

Además, mejora la **disponibilidad ante picos de tráfico o abuso**. El rate limiter (táctica *Controlar arribo de eventos*) limita cada cliente a 20 peticiones por minuto. En las pruebas, de 34 peticiones seguidas se atendieron 20 y las 14 restantes recibieron `429 Too Many Requests`, lo que protege al servicio de bots o de ráfagas que podrían degradarlo para el resto de los usuarios.

### Trade-offs

La principal contrapartida es la **pérdida de analítica**. Como el navegador reutiliza la redirección cacheada, las visitas posteriores nunca llegan al servidor, así que no es posible contar cuántas veces ni cuándo se usó un link. Es justamente lo que la Arquitectura 1 sí permite.

También existe un problema de **reversibilidad**. Un 301 es difícil de deshacer: si la USM cambia la URL de destino, los navegadores que ya guardaron la redirección seguirán enviando a la dirección antigua hasta que se limpie su caché. A esto se suma que la caché del servidor puede entregar una redirección desactualizada durante hasta 120 segundos.

Por otro lado, el **límite por IP** puede afectar a usuarios legítimos. Dentro del campus, muchos usuarios salen a internet a través de la misma IP pública de la red universitaria, por lo que podrían recibir `429` sin estar abusando del servicio. El límite debe calibrarse según el tráfico real.

Finalmente, la caché y el contador del rate limiter **viven en memoria** de un único proceso. Si se levantan varias instancias para escalar, cada una tendría su propia caché y su propio contador, generando comportamientos inconsistentes. Para escalar habría que moverlos a un almacén compartido, como Redis, que LiteStar soporta.

## 3. Comparación y recomendación para la USM
(turno 4)

## 4. Bonus: ids únicos en un ambiente distribuido
(turno 4)