#  FastAPI Project Management Application

A containerized **FastAPI** CRUD application following **clean architecture** with **PostgreSQL**, **pgAdmin**, and **Docker Compose**.  
Dependency management is handled with **Poetry**, and developer tasks are automated with a **Makefile**.  

---

## ✨ Features
- **FastAPI** backend with modular architecture and **Pydantic** schemas for validation
- **PostgreSQL** database (containerized)  
- **pgAdmin** web-interface for database management (containerized) 
- **Clean architecture**: Application, Domain, Infrastructure, Presentation 
- **Docker Compose** for full containerized setup
- **Poetry** for dependency management
- **GitHub Actions** CI workflow for:  
  - Code quality and linting (`Ruff, isort, Black, mypy`)  
  - Unit testing across multiple Python versions  
  - Dependency checks for outdated packages
  - Security scans with Bandit
- **Custom File Logging**:  
  The application uses a custom logging system that writes logs to a `logs/` directory.  
  All logs are stored in a single file named `app.log`.
- **Document Storage**:  
  Document uploads are configurable — they can be stored either on the **local filesystem** or in an **AWS S3 bucket**.  
  - **Local Storage**: Documents are saved in the `documents/` folder. Each project has its own subdirectory named after the `project_id`, containing all its documents.  
  - **S3 Storage**: Documents are stored in the configured S3 bucket. Each project gets its own prefix (acting as a subdirectory), where all documents for that project are kept.
- **Document Management**:  
  Uploaded files can be **downloaded** and **deleted**.  
  When the last document in a project’s directory/prefix is deleted, the directory/prefix itself is also removed (both locally and in S3).
- **Makefile** for common developer tasks


---
# 🚀 Getting Started

## 1. Clone the Repository
```bash
git clone https://github.com/v0z/project_management_app.git
cd project_management_app
```

## 2. Install Dependencies with Poetry
Make sure you have [Poetry](https://python-poetry.org/docs/#installation) installed, then run:

```bash
poetry install
```

This will create a virtual environment and install all dependencies defined in `pyproject.toml`.

## 3. Environment Setup

Create a `.env` file in the project root with the following content:

```ini
# custom logging configuration
LOGGER_LOG_DIR=logs
LOGGER_FILENAME=app.log

# auth config
TOKEN_SECRET_KEY=some_super_secret_key
TOKEN_ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=60

# Database configuration with local dev database creds
DB_NAME=pm_database
DB_USERNAME=root
DB_PASSWORD=toor
DB_PORT=5432
DB_HOST=localhost # inside pgadmin this should be your postgres database service name in your docker-compose file, in my case it's: postgres_db

# pgAdmin configuration 
PGADMIN_DEFAULT_EMAIL=fast@api.com
PGADMIN_DEFAULT_PASSWORD=toor

# files
ALLOWED_TYPES='["application/pdf", "image/png", "image/jpeg"]'
MAX_FILE_SIZE_IN_MB=5

# set the storage backend to use -  local or s3
STORAGE_BACKEND=s3

# aws environment variables
AWS_S3_BUCKET_NAME=super_unique_bucket_name_123
AWS_ACCESS_KEY_ID=ABC
AWS_SECRET_ACCESS_KEY=abc123

```

### 🔑 Generating a Secure Secret Key

You can generate a strong secret key using the following command:

```bash
openssl rand -hex 32
```
---

## 4. Run with Docker Compose
Build and start the application and its services (PostgreSQL, pgAdmin, FastAPI):

```bash
docker-compose up --build
```
---


## 5. pgAdmin Setup

1. Open [http://localhost:8080](http://localhost:8080)  
2. Log in with credentials from `.env`  
3. Click **Add New Server**:  
   - On tab **General:
     - **Name**: `pm_database`  
   - On tab **Connection:
     - **Hostname**: `postgres_db`  
     - **Username**: `root`  
     - **Password**: `toor`  
4. Click **Save** → Database ready to manage 🎉

---

## 6. Access the Application
- **FastAPI** → [http://localhost:8000](http://localhost:8000)  
- **Swagger Docs** → [http://localhost:8000/docs](http://localhost:8000/docs)  
- **pgAdmin** → [http://localhost:8080](http://localhost:8080)  


---
### 🛠️ Developer Commands (Makefile)

| Command        | Description |
|----------------|-------------|
| `make run`     | Start FastAPI locally (`uvicorn app.main:app --reload`) |
| `make test`    | Run all tests with pytest |
| `make coverage`| Run tests with coverage report |
| `make lint`    | Lint code using Ruff and auto-fix |
| `make format`  | Format code using Ruff |
| `make isort`   | Sort imports with isort |
| `make typing`  | Run type checking with mypy |
| `make recreate_db` | Drop & recreate database (`scripts/recreate_db.py`) |
| `make tree`    | Show project folder structure (ignores `.gitignore` & `__init__.py`) |

---

## 🧪 Development (without Docker)

Install dependencies:

```bash
poetry install
```

Run the app:

```bash
poetry run uvicorn app.main:app --reload
```

Run tests:

```bash
poetry run pytest
```

Or using Makefile:

```bash
make test
```

---

## 📜 API Documentation

- **Swagger UI** → [http://localhost:8000/docs](http://localhost:8000/docs)  
- **ReDoc** → [http://localhost:8000/redoc](http://localhost:8000/redoc)  

---

## 📡 API Endpoints

### **Auth**
| Method | Endpoint         | Description        |
|--------|-----------------|------------------|
| POST   | `/auth/`        | Register User      |
| POST   | `/auth/login`   | Login              |

### **Projects**
| Method | Endpoint                   | Description        |
|--------|----------------------------|------------------|
| GET    | `/projects/`               | Show all projects  |
| POST   | `/projects/`               | Create project     |
| GET    | `/projects/{project_id}`   | Get a project      |
| PATCH  | `/projects/{project_id}`   | Update project     |
| DELETE | `/projects/{project_id}`   | Delete project     |

### **Documents**
| Method | Endpoint                                          | Description         |
|--------|--------------------------------------------------|-------------------|
| GET    | `/projects/{project_id}/documents/`             | List Documents      |
| POST   | `/projects/{project_id}/documents/`             | Upload Document     |
| GET    | `/projects/{project_id}/documents/{document_id}`| Download Document   |
| PATCH  | `/projects/{project_id}/documents/{document_id}`| Update Document     |
| DELETE | `/projects/{project_id}/documents/{document_id}`| Delete Document     |

### **Health**
| Method | Endpoint | Description   |
|--------|---------|---------------|
| GET    | `/`     | Health Check  |

---

# 🏗 Project Architecture Overview

This project follows a layered (clean architecture) structure to keep the code modular, maintainable, and testable.

| Layer / Folder         | Purpose |
|-------------------------|---------|
| **`app/main.py`**       | Entry point of the FastAPI application. |
| **`app/core/`**         | Cross-cutting concerns and core infrastructure:<br>- `config.py`: App settings (env vars).<br>- `database.py`: DB connection/session.<br>- `logger.py`: Logging to `logs/app.log`.<br>- `security.py`: Security utilities (JWT, hashing).<br>- `exceptions.py`: Shared exceptions. |
| **`app/domain/`**       | Business/domain logic (problem space):<br>- `entities/`: Domain models (`User`, `Project`, `Document`).<br>- `repositories/`: Abstract repository interfaces.<br>- `storage/`: Abstract storage interfaces + utils.<br>- `exceptions/`: Domain-specific errors. |
| **`app/application/`**  | Application services — implements business use cases:<br>`auth_service.py`, `project_service.py`, `document_service.py`. |
| **`app/infrastructure/`** | Technology-specific implementations:<br>- `orm/`: SQLAlchemy models.<br>- `sqlalchemy_*_repository.py`: Repository implementations.<br>- `storage/`: File system & S3 storage implementations. |
| **`app/presentation/`** | Presentation/API layer:<br>- `api/v1/`: FastAPI routes (auth, projects, documents).<br>- `schemas/`: Pydantic request/response models.<br>- `dependencies.py`: Dependency injection. |
| **`scripts/`**          | Utility scripts (e.g., `recreate_db.py` to reset DB). |
| **`tests/`**            | Automated tests organized by feature/layer. |


## 📂 Project Structure
```
.
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── app
│   ├── application
│   │   └── services
│   │       ├── auth_service.py
│   │       ├── document_service.py
│   │       └── project_service.py
│   ├── core
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   ├── logger.py
│   │   └── security.py
│   ├── domain
│   │   ├── enities
│   │   │   ├── document.py
│   │   │   ├── project.py
│   │   │   └── user.py
│   │   ├── exceptions
│   │   │   ├── document_exceptions.py
│   │   │   ├── domain_exceptions.py
│   │   │   ├── project_exceptions.py
│   │   │   └── user_exceptions.py
│   │   ├── repositories
│   │   │   ├── document_repository.py
│   │   │   ├── project_repository.py
│   │   │   └── user_repository.py
│   │   └── storage
│   │       ├── document_storage.py
│   │       ├── exceptions
│   │       └── utils.py
│   ├── infrastructure
│   │   ├── orm
│   │   │   ├── document_model.py
│   │   │   ├── project_model.py
│   │   │   └── user_model.py
│   │   ├── sqlalchemy_documet_repository.py
│   │   ├── sqlalchemy_project_repository.py
│   │   ├── sqlalchemy_user_repository.py
│   │   └── storage
│   │       ├── file_system_document_storage.py
│   │       └── s3_document_storage.py
│   ├── main.py
│   └── presentation
│       ├── api
│       │   └── v1
│       │       ├── auth_routes.py
│       │       ├── document_routes.py
│       │       └── project_routes.py
│       ├── dependencies.py
│       └── schemas
│           ├── auth_schemas.py
│           ├── document_schemas.py
│           └── project_schemas.py
├── docker-compose.yml
├── poetry.lock
├── pyproject.toml
├── scripts
│   └── recreate_db.py
└── tests
    ├── auth
    │   └── test_auth_service.py
    ├── conftest.py
    ├── infrastructure
    │   └── test_sqlalchemy_user_repository.py
    └── test_root.py

```


## 🔄 Continuous Integration (CI)

This project includes a **GitHub Actions workflow** that runs on:

- **Pushes and Pull Requests** to the `main` branch  
- **Weekly scheduled runs** (every Monday at midnight)  

The workflow consists of three jobs:

1. **Code Quality**
   - Linting with **Ruff**  
   - Import sorting with **isort**  
   - Formatting check with **Black**  
   - (Optional) Static typing with **mypy**  
   - (Optional) Security scan with **Bandit**

2. **Unit Tests**
   - Runs **pytest** across multiple Python versions (`3.10`, `3.11`, `3.12`)  
   - Ensures code works consistently in different environments

3. **Dependency Check**
   - Runs `poetry show --outdated`  
   - Helps keep dependencies up to date

📂 Workflow file: `.github/workflows/ci_workflow.yml`

## 📄 License
This project is licensed under the **Apache License 2.0**.  

