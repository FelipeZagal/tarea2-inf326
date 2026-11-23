# Discusión de trade-offs — Tarea 2 INF326

## 1. Arquitectura 1: redirección 302 + servicio Log gRPC

### Beneficios

El principal beneficio de esta arquitectura es la **analítica de visitas**. El acortador responde con HTTP `302` (redirección temporal) y agrega `Cache-Control: no-store` para que las cachés HTTP no almacenen la respuesta. Con Log disponible, la USM puede contar redirecciones y conocer en qué horario se solicitó cada enlace, lo cual resulta útil para evaluar campañas de postulación al magíster o la difusión de eventos universitarios. El registro identifica la hora y las URLs, por lo que permite medir solicitudes por enlace. [RFC 9111, directiva no-store](https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2.2.5)

Adicionalmente, la arquitectura ofrece un buen nivel de **desacople** al aislar el registro de visitas en un servicio independiente (`Log`) comunicado mediante un contrato explícito (`log.proto`) sobre gRPC. Como el envío del evento `"url hit"` se ejecuta en segundo plano (`BackgroundTask`) después de enviar el `302`, el cliente recibe la redirección antes de que termine la llamada de analítica. La prueba de desacople mostró que, si se detiene `Log`, el acortador sigue redirigiendo y emite una advertencia en consola.

### Trade-offs

Evitar la caché de la redirección genera **mayor carga**. Cada visita que llega a `Shortener v1` requiere una consulta a su base de datos, lo que aumenta el uso de recursos bajo alta demanda. A esto se suma una **mayor complejidad operativa**, ya que el equipo debe desplegar, monitorear y mantener dos servicios, dos bases de datos independientes (`shortener_v1.db` y `log.db`) y el contrato gRPC que los vincula.

Finalmente, existen compromisos en **confiabilidad de los eventos y seguridad interna**. Como no hay persistencia intermedia ni reintentos, el evento `"url hit"` se pierde cuando falla su envío a `Log`. En producción, una cola persistente y reintentos permitirían recuperar esos envíos. El canal gRPC opera sin TLS (`insecure_channel`) en la demostración local. Si los componentes se desplegaran en nodos separados, se debería proteger el canal interno con TLS o mTLS.

## 2. Arquitectura 2: redirección 301 + rate limiter + caché

### Beneficios

En primer lugar, esta arquitectura reduce el trabajo por visita repetida. Al responder con un código 301, el navegador puede guardar la redirección y reutilizarla sin contactar al servicio `Shortener v2`. Para las peticiones que sí llegan al servicio, la caché de respuestas de LiteStar (táctica *Mantener múltiples copias de datos*) evita consultar la base de datos si la respuesta sigue almacenada. En nuestras pruebas, la BD se consultó una sola vez para 19 redirecciones exitosas, lo que reduce las lecturas de `shortener_v2.db`.

Además, mejora la **disponibilidad ante picos de tráfico o abuso**. El rate limiter (táctica *Controlar arribo de eventos*) limita cada cliente a 20 peticiones por minuto. En las pruebas, de 34 peticiones seguidas se atendieron 20 y las 14 restantes recibieron `429 Too Many Requests`, lo que protege al servicio de bots o de ráfagas que podrían degradarlo para el resto de los usuarios.

### Trade-offs

La principal contrapartida es la **pérdida de visibilidad**. Las visitas que reutilizan una redirección en la caché del navegador no llegan al servidor. Un contador en el acortador, si se añadiera, dejaría fuera esas visitas.

También existe un problema de **reversibilidad**. Si la USM cambia la URL de destino, los navegadores que ya guardaron el 301 pueden seguir enviando a la dirección antigua mientras reutilicen su copia. La caché del servidor tiene su propio plazo de 120 segundos.

Por otro lado, el **límite por IP** puede afectar a usuarios legítimos. Dentro del campus, muchos usuarios salen a internet a través de la misma IP pública de la red universitaria, por lo que podrían recibir `429` sin estar abusando del servicio. El límite debe calibrarse según el tráfico real.

Finalmente, la caché y el contador del rate limiter **viven en memoria** de un único proceso. Si se levantan varias instancias para escalar, cada una tendría su propia caché y su propio contador, generando comportamientos inconsistentes. Para escalar habría que moverlos a un almacén compartido, como Redis, que LiteStar soporta.

## 3. Comparación y recomendación para la USM

Para una **campaña de admisión, postgrado o difusión**, recomendamos la Arquitectura 1. Permite medir las solicitudes por enlace y horario mientras Log está disponible. La ruta de postgrado del enunciado incluye `2025`, así que el destino podría cambiar en el siguiente proceso. Si se añadiera la opción de actualizar destinos, la USM podría mantener el enlace corto ya difundido y los clientes volverían al acortador para consultar el destino vigente. En la prueba, los tres accesos generaron tres hits. Con Log detenido, el 302 siguió funcionando y el intento de registro dejó un aviso.

Para un **enlace estable con alta demanda**, como un acceso al portal institucional, recomendamos la Arquitectura 2 si contar todas las visitas tiene menos valor. Su caché hizo una consulta a SQLite para 19 redirecciones 301. El límite por IP rechazó las 14 peticiones que excedieron el cupo de 20, que incluía una creación y 19 redirecciones. El límite protege frente a ráfagas de un mismo cliente. En una red de campus, varios usuarios legítimos pueden compartir una IP pública, por lo que conviene calibrar ese valor con el tráfico real.

La visibilidad de las visitas y la facilidad para cambiar destinos son trade-offs de consideración para la USM. La relevancia del rendimiento depende del tráfico y de sus picos, porque la prueba comprobó el comportamiento funcional y no midió la capacidad en producción. Si una campaña necesita analítica y también recibe picos, una alternativa sería conservar el 302 y el envío de cada evento y añadir una caché de la búsqueda en la BD. Así el handler se ejecutaría en cada visita y podría registrar el hit, aunque ya tenga el destino en memoria.

## 4. Bonus: ids únicos en un ambiente distribuido

En varias instancias que compartan el mismo dominio de enlaces, cada SQLite local podría asignar `597652313` al primer registro. El mismo ID produce el mismo código Base62, de modo que dos destinos competirían por `eRgfR`. En la demostración, v1 y v2 usan puertos distintos y sus bases son independientes, por lo que el mismo código en ambas no crea esa ambigüedad.

Una solución es un **asignador de rangos** con un contador global persistente. En una transacción, reserva un bloque de IDs y avanza el contador antes de entregarlo. Por ejemplo, el nodo A recibe `597652313–597662312` y el nodo B recibe `597662313–597672312`. Cada nodo asigna IDs crecientes dentro de su bloque y pide otro al agotarlo. Si un nodo reinicia, conserva el avance en disco o descarta los IDs que le quedaban y reserva otro bloque. El asignador nunca vuelve a entregar un rango reservado. Así pueden quedar huecos sin repetir identificadores.

Como la codificación Base62 usa un alfabeto fijo, los IDs distintos generan códigos distintos. Los mapeos deben quedar en un almacenamiento compartido o ser accesibles mediante un enrutamiento que encuentre el nodo dueño del rango. La restricción `UNIQUE(hash)` debe aplicarse en el almacenamiento común como defensa adicional. Una secuencia central por URL sería más sencilla, pero obligaría a consultar al asignador en cada creación. Con rangos, una caída del asignador solo detiene a los nodos que ya agotaron su bloque.
