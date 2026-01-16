# API de Gestión de Estudiantes

API REST desarrollada con Flask para la gestión de estudiantes.

## Características
- CRUD completo de estudiantes
- Filtros por estado (aprobados/reprobados)
- Estadísticas académicas
- Base de datos SQL con SQLAlchemy
- Validación de datos
- Logging de operaciones

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
```bash
pip install -r requirements.txt


## RESPUESTAS DEL EXAMEN

Respuesta 1: Para una aplicación que solo saluda y no requiere conexión a base de datos ni panel de administración podemos elegir Flask por:
-	El código es muy corto porque solo requiere un endpoint, con Django se requiere crear un proyecto, una app, vistas, urls y configuraciones.
-	Flash no requiere una estructura de carpetas ni configuraciones, con Django requiere autenticación, panel de administración y migraciones.
-	Flash no requiere tanta memoria.
-	Flash permite agregar extensiones, pero el proyecto descrito no lo requiere


Respuesta 2: El cliente no entra a la cocina por razones de seguridad y orden del API.
-	Seguridad: La cocina tiene alimentos, recetas y equipos especializados, si el cliente entra podría ver otros alimentos, conocer información de concina y dañar equipos. En la API, el cliente no debe acceder a la base de datos por seguridad de información, manipulación y hasta pérdida de información, es por eso que la API actúa como un mecanismo de control.
-	Orden: El mesero toma los pedidos, los priorizan, los traduce a lenguaje de cocina y se asegura de seguir los procedimientos. El API realiza las validaciones y les da forma antes de pasarla al servidor, evitando que peticiones mal formadas o fuera de secuencia sean recibidas por el servidor.
-	Responsabilidades: En cada proyecto cada usuario tiene su rol por ejemplo, el cliente realiza el pedido de un menú, el mesero es el orquestador entre el cliente y la cocina, y la cocina prepara el menú. En el API, el frontend toma el pedido del usuario, el backend se encarga de la lógica y la información y el API tiene mecanismos que permiten la comunicación.


Respuesta 3: Un juego online que se sobreentiende que es en tiempo real, se requiere dejar la llamada abierta usando WebSockets porque:
-	El servidor debe actualizar en tiempo real a todos los jugadores todas las acciones de los jugadores sin esperar una petición del cliente, Con WebSocket se puede realizar un push de los datos a todos los clientes sin que se espere a una pregunta.
-	Mejora la latencia porque WebSocket mantiene la conexión abierta con mínima latencia porque REST requeriría solicitudes permanentes lo que significa demoras y sobrecarga de conexiones.
-	Eficiencia en la red: WebSocket requiere enviar datos en un frame simple hasta 60 veces por segundo, en cambio con RET se debe enviar cabeceras http completos en cada solicitud.
-	Estado de conexión: WebSocket detecta la desconexión al instante, con REST se debería esperar a una solicitud periódica.
