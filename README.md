# Items API

🎬 [Video demo](https://drive.google.com/file/d/1NhWAI-BtxAcMDf5yS9Ps6ZXO8BeW-qZ_/view?usp=sharing)

API REST construida con FastAPI para la gestión de items. Permite crear, leer, actualizar y eliminar items con validación automática, paginación y documentación interactiva.

---

## Estructura del proyecto

```
kalmy-fastapi/
├── .github/
│   └── workflows/
│       └── ci.yml                # Pipeline de integración continua
├── app/
│   ├── controllers/
│   │   └── item_controller.py    # Operaciones CRUD
│   ├── models/
│   │   └── item.py               # Modelo de SQLAlchemy
│   ├── routes/
│   │   └── items.py              # Definición de endpoints
│   ├── schemas/
│   │   └── item.py               # Esquemas de validación
│   ├── database.py
│   └── main.py
├── tests/
│   ├── conftest.py               # Fixtures y configuración de pruebas
│   └── test_items.py             # Casos de prueba
├── .dockerignore
├── .gitignore
├── Dockerfile
├── LICENSE
├── docker-compose.yml
├── pytest.ini
└── requirements.txt
```

El proyecto sigue una arquitectura en capas: las rutas reciben las peticiones HTTP, las delegan a los controladores que contienen la lógica, y estos interactúan con los modelos ORM para acceder a la base de datos. Los esquemas de validación actúan como contrato entre la API y el cliente.

---

## Cómo correr la API

### Opción 1: Entorno local

**Requisitos:** Python 3.13

1. Clona el repositorio:

```bash
git clone https://github.com/eduardo-hdez/Kalmy-FastAPI.git
cd kalmy-fastapi
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Corre el servidor:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`.

### Opción 2: Docker Compose (RECOMENDADA)

**Requisitos:** Docker y Docker Compose instalados.

```bash
docker compose up --build
```

La API estará disponible en `http://localhost:8000`.

La base de datos se persiste en el volumen `db-data`, por lo que los datos sobreviven a reinicios del contenedor.

Para detener y eliminar completamente los contenedores, redes y volúmenes:

```bash
docker compose down -v --rmi all
```

### Variables de entorno

| Variable       | Valor por defecto      | Descripción                        |
| -------------- | ---------------------- | ---------------------------------- |
| `DATABASE_URL` | `sqlite:///./items.db` | URL de conexión a la base de datos |

Con Docker Compose, `DATABASE_URL` apunta a `sqlite:///./data/items.db` dentro del volumen persistente.

---

## Decisiones tecnológicas

### Pydantic v2

Se usa Pydantic para la validación declarativa de todos los datos de entrada y salida. Los esquemas definen constraints directamente en los campos (`max_length=128` en nombres, `max_length=256` en descripciones, `gt=0` en precios, campos opcionales con `None`). En las actualizaciones parciales, `model_dump(exclude_unset=True)` garantiza que solo se modifiquen los campos enviados por el cliente, evitando sobrescrituras accidentales.

### SQLAlchemy 2.0 + SQLite

Inicialmente el proyecto usaba MongoDB con Motor (el cliente async oficial). Durante el desarrollo de los tests surgieron dos problemas que resultaron irresolubles:

1. **`Event loop is closed`**: pytest no mantiene un event loop activo entre tests por defecto. Cada fixture async requería manejo explícito del loop, generando errores intermitentes difíciles de reproducir.
2. **Una sola request activa por archivo**: `AsyncIOMotorClient` en modo de pruebas forzaba a serializar las operaciones, haciendo imposible tener múltiples fixtures independientes dentro del mismo archivo de tests.

El cambio a SQLite con SQLAlchemy síncrono eliminó ambos problemas de raíz: no hay event loop que gestionar, las sesiones son objetos Python ordinarios y el aislamiento entre tests se logra simplemente creando y destruyendo las tablas. Se usa la API moderna de SQLAlchemy 2.0 (`Mapped`, `mapped_column`) y el flag `check_same_thread=False` requerido por SQLite para permitir su uso con el sistema de dependencias de FastAPI.

### pytest + TestClient

Los tests usan `TestClient`, que levanta la aplicación sin necesidad de correr un servidor real. La configuración en `conftest.py` define dos fixtures clave:

- `setup_test_db` (`autouse=True`): crea todas las tablas antes de cada test y las destruye al terminar, garantizando que cada prueba parte de una base de datos limpia e independiente.
- `override_get_db`: reemplaza la dependencia `get_db` con una sesión que apunta a `test.db`, de modo que los tests nunca tocan la base de datos de desarrollo.

### UUID como identificador de items

El campo `id` de cada item se genera automáticamente como un UUID v4 (`uuid.uuid4()`) al momento de la creación, sin necesidad de que el cliente lo provea. Se almacena como `String` en la base de datos y se expone como cadena de texto en la API. Esto garantiza identificadores únicos globalmente y evita colisiones en entornos distribuidos.

### Docker y Docker Compose

La imagen está basada en `python:3.13-slim` para mantener un tamaño reducido. Docker Compose define un volumen nombrado (`db-data`) montado en `/app/data`, donde reside la base de datos SQLite en producción. Esto garantiza que los datos persistan entre reinicios del contenedor y que el proyecto pueda ejecutarse en cualquier entorno sin instalar Python ni dependencias manualmente.

### GitHub Actions (CI)

El pipeline en `.github/workflows/ci.yml` se ejecuta automáticamente en cada push y pull request hacia la rama `main`. Los pasos son: checkout del código, instalación de Python 3.13, instalación de dependencias desde `requirements.txt` y ejecución de `pytest`. Esto asegura que ningún cambio pueda fusionarse sin pasar todos los tests.

---

## Cómo probar los endpoints

### Documentación

Al iniciar la aplicación, la ruta raíz `/` redirige automáticamente a `/docs`, por lo que basta con abrir `http://localhost:8000` en el navegador para acceder a la documentación sin necesidad de recordar ninguna ruta adicional.

### Endpoints disponibles

| Método   | Ruta          | Descripción                             |
| -------- | ------------- | --------------------------------------- |
| `POST`   | `/items/`     | Crear un nuevo item                     |
| `GET`    | `/items/`     | Obtener lista de items (con paginación) |
| `GET`    | `/items/{id}` | Obtener un item por ID                  |
| `PUT`    | `/items/{id}` | Actualizar un item existente            |
| `DELETE` | `/items/{id}` | Eliminar un item                        |

### Paginación

El endpoint `GET /items/` acepta los parámetros de query `skip` y `limit`:

```
GET /items/?skip=0&limit=10
```

| Parámetro | Tipo   | Valor por defecto | Restricciones |
| --------- | ------ | ----------------- | ------------- |
| `skip`    | entero | `0`               | >= 0          |
| `limit`   | entero | `10`              | >= 1, <= 100  |

### Ejecutar los tests

```bash
pytest
```

Para ver el detalle de cada caso:

```bash
pytest -v
```

### Casos de prueba existentes

| Test                            | Descripción                                                     |
| ------------------------------- | --------------------------------------------------------------- |
| `test_create_item`              | Crea un item y verifica que retorne 201 con los datos correctos |
| `test_get_all_items`            | Verifica que la lista de items retorne 200 y contenga elementos |
| `test_get_item_by_id`           | Crea un item y lo recupera por su ID                            |
| `test_get_item_by_id_not_found` | Verifica que un ID inexistente retorne 404                      |
| `test_update_item`              | Actualiza precio y disponibilidad de un item existente          |
| `test_update_item_not_found`    | Verifica que actualizar un ID inexistente retorne 404           |
| `test_delete_item`              | Elimina un item y confirma que ya no existe con un GET          |
| `test_delete_item_not_found`    | Verifica que eliminar un ID inexistente retorne 404             |

Cada test opera sobre una base de datos limpia gracias al fixture `setup_test_db`, por lo que son completamente independientes entre sí y pueden ejecutarse en cualquier orden.
