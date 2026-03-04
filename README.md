# Items API

🎬 [Video demo](https://drive.google.com/file/d/1NhWAI-BtxAcMDf5yS9Ps6ZXO8BeW-qZ_/view?usp=sharing) (Spanish)

REST API built with FastAPI for item management. Allows creating, reading, updating, and deleting items with automatic validation, pagination, and interactive documentation.

---

## Project structure

```
items-fastapi/
├── .github/
│   └── workflows/
│       └── ci.yml                # Continuous integration pipeline
├── app/
│   ├── controllers/
│   │   └── item_controller.py    # CRUD operations
│   ├── models/
│   │   └── item.py               # SQLAlchemy model
│   ├── routes/
│   │   └── items.py              # Endpoint definitions
│   ├── schemas/
│   │   └── item.py               # Validation schemas
│   ├── database.py
│   └── main.py
├── tests/
│   ├── conftest.py               # Fixtures and test configuration
│   └── test_items.py             # Test cases
├── .dockerignore
├── .gitignore
├── Dockerfile
├── LICENSE
├── docker-compose.yml
├── pytest.ini
└── requirements.txt
```

The project follows a layered architecture: routes receive HTTP requests and delegate them to controllers that contain the business logic, which in turn interact with ORM models to access the database. Validation schemas act as a contract between the API and the client.

---

## How to run the API

### Option 1: Local environment

**Requirements:** Python 3.13

1. Clone the repository:

```bash
git clone https://github.com/eduardo-hdez/Items-FastAPI
cd items-fastapi
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Option 2: Docker Compose (RECOMMENDED)

**Requirements:** Docker and Docker Compose installed.

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

The database is persisted in the `db-data` volume, so data survives container restarts.

To stop and completely remove containers, networks, and volumes:

```bash
docker compose down -v --rmi all
```

### Environment variables

| Variable       | Default value          | Description             |
| -------------- | ---------------------- | ----------------------- |
| `DATABASE_URL` | `sqlite:///./items.db` | Database connection URL |

With Docker Compose, `DATABASE_URL` points to `sqlite:///./data/items.db` inside the persistent volume.

---

## Technology decisions

### Pydantic v2

Pydantic is used for declarative validation of all input and output data. Schemas define constraints directly on the fields (`max_length=128` for names, `max_length=256` for descriptions, `gt=0` for prices, optional fields with `None`). For partial updates, `model_dump(exclude_unset=True)` ensures that only the fields sent by the client are modified, avoiding accidental overwrites.

### SQLAlchemy 2.0 + SQLite

Initially the project used MongoDB with Motor (the official async client). During test development, two problems arose that proved irresolvable:

1. **`Event loop is closed`**: pytest does not maintain an active event loop between tests by default. Each async fixture required explicit loop management, generating intermittent errors that were hard to reproduce.
2. **Single active request per file**: `AsyncIOMotorClient` in test mode forced operations to be serialized, making it impossible to have multiple independent fixtures within the same test file.

Switching to SQLite with synchronous SQLAlchemy eliminated both problems at the root: there is no event loop to manage, sessions are ordinary Python objects, and test isolation is achieved simply by creating and dropping tables. The modern SQLAlchemy 2.0 API is used (`Mapped`, `mapped_column`) along with the `check_same_thread=False` flag required by SQLite to allow its use with FastAPI's dependency injection system.

### pytest + TestClient

Tests use `TestClient`, which runs the application without needing to start a real server. The configuration in `conftest.py` defines two key fixtures:

- `setup_test_db` (`autouse=True`): creates all tables before each test and drops them when done, ensuring each test starts with a clean, independent database.
- `override_get_db`: replaces the `get_db` dependency with a session pointing to `test.db`, so tests never touch the development database.

### UUID as item identifier

The `id` field of each item is automatically generated as a UUID v4 (`uuid.uuid4()`) at creation time, with no need for the client to provide it. It is stored as a `String` in the database and exposed as a string in the API. This guarantees globally unique identifiers and avoids collisions in distributed environments.

### Docker and Docker Compose

The image is based on `python:3.13-slim` to keep the size small. Docker Compose defines a named volume (`db-data`) mounted at `/app/data`, where the SQLite database resides in production. This ensures data persists between container restarts and that the project can run in any environment without manually installing Python or dependencies.

### GitHub Actions (CI)

The pipeline in `.github/workflows/ci.yml` runs automatically on every push and pull request to the `main` branch. The steps are: checkout the code, install Python 3.13, install dependencies from `requirements.txt`, and run `pytest`. This ensures no change can be merged without passing all tests.

---

## How to test the endpoints

### Documentation

When starting the application, the root route `/` automatically redirects to `/docs`, so simply opening `http://localhost:8000` in the browser is enough to access the documentation without needing to remember any additional route.

### Available endpoints

| Method   | Route         | Description                         |
| -------- | ------------- | ----------------------------------- |
| `POST`   | `/items/`     | Create a new item                   |
| `GET`    | `/items/`     | Get list of items (with pagination) |
| `GET`    | `/items/{id}` | Get an item by ID                   |
| `PUT`    | `/items/{id}` | Update an existing item             |
| `DELETE` | `/items/{id}` | Delete an item                      |

### Pagination

The `GET /items/` endpoint accepts `skip` and `limit` query parameters:

```
GET /items/?skip=0&limit=10
```

| Parameter | Type    | Default value | Constraints  |
| --------- | ------- | ------------- | ------------ |
| `skip`    | integer | `0`           | >= 0         |
| `limit`   | integer | `10`          | >= 1, <= 100 |

### Running tests

```bash
pytest
```

To see the detail of each case:

```bash
pytest -v
```

### Existing test cases

| Test                            | Description                                                       |
| ------------------------------- | ----------------------------------------------------------------- |
| `test_create_item`              | Creates an item and verifies it returns 201 with the correct data |
| `test_get_all_items`            | Verifies the item list returns 200 and contains elements          |
| `test_get_item_by_id`           | Creates an item and retrieves it by its ID                        |
| `test_get_item_by_id_not_found` | Verifies that a non-existent ID returns 404                       |
| `test_update_item`              | Updates the price and availability of an existing item            |
| `test_update_item_not_found`    | Verifies that updating a non-existent ID returns 404              |
| `test_delete_item`              | Deletes an item and confirms it no longer exists with a GET       |
| `test_delete_item_not_found`    | Verifies that deleting a non-existent ID returns 404              |

Each test operates on a clean database thanks to the `setup_test_db` fixture, so they are completely independent and can run in any order.
