# Discusión de trade-offs — Tarea 2 INF326

## 1. Arquitectura 1: redirección 302 + servicio Log gRPC

### Beneficios

El principal beneficio de esta arquitectura es la **analítica completa**. Al responder con un código HTTP `302` (redirección temporal), se le indica al navegador que no almacene la redirección en su caché local, forzándolo a consultar al servidor en cada visita. Esto permite que la USM registre con exactitud cuántas veces y en qué horario se accede a cada enlace acortado, lo cual resulta especialmente útil para medir el alcance e impacto de campañas específicas, como un proceso de postulaciones al magíster o la difusión de eventos universitarios.

Adicionalmente, la arquitectura ofrece un buen nivel de **desacople** al aislar el registro de visitas en un servicio independiente (`Log`) comunicado mediante un contrato explícito (`log.proto`) sobre gRPC. Como el envío del evento `"url hit"` se ejecuta en segundo plano (`BackgroundTask`) una vez enviada la respuesta `302`, la llamada al servicio de analítica no agrega latencia perceptible a la redirección del usuario. Esto también evita que una falla en el registro interrumpa el servicio principal: tal como se verificó en las pruebas de desacople, si el servicio `Log` se cae, el acortador continúa redirigiendo sin problemas y solo emite una advertencia en consola.

### Trade-offs

Como contrapartida, evitar el caché del navegador genera **mayor carga y latencia**. Debido a que los clientes nunca reutilizan una redirección previa, el 100% del tráfico impacta directamente al servicio `Shortener v1` y a su base de datos, lo que se traduce en mayor consumo de recursos y mayores costos de infraestructura bajo alta demanda. A esto se suma una **mayor complejidad operativa**, ya que el equipo debe desplegar, monitorear y mantener dos servicios distintos, dos bases de datos independientes (`shortener_v1.db` y `log.db`) y la evolución del contrato gRPC que los vincula.

Finalmente, existen compromisos en **confiabilidad de los eventos y seguridad interna**. Por un lado, al no existir persistencia intermedia ni políticas de reintento, cualquier evento `"url hit"` enviado mientras el servicio `Log` está caído se pierde definitivamente; en un entorno real esto debería mitigarse introduciendo reintentos o una cola de mensajes (como RabbitMQ) para garantizar la entrega eventual. Por otro lado, el canal gRPC opera actualmente sin TLS (`insecure_channel`), lo cual es razonable mientras ambos componentes vivan en el mismo nodo de despliegue, pero en un escenario productivo con nodos separados requeriría habilitar TLS o mTLS para proteger la comunicación interna.

## 2. Arquitectura 2: redirección 301 + rate limiter + caché
(la completa la Persona 3)

## 3. Comparación y recomendación para la USM
(turno 4)

## 4. Bonus: ids únicos en un ambiente distribuido
(turno 4)