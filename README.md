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
  - On push to `main`, GitHub Actions automatically builds and pushes a Docker image to the configured **DockerHub repository**.  
- **Infrastructure as Code (IaC) with AWS CloudFormation**:  
  - A CloudFormation template provisions all required resources automatically.  
  - (Note: currently the previous stack must be deleted before redeployment).  
  - Resources created include:  
    - **VPC** with networking setup.  
    - **EC2 instance** for hosting the application.  
    - **RDS PostgreSQL database**.  
    - **S3 buckets** for storage, including one with a **Lambda trigger**.
    - (Note: Currently the Lambda trigger needs to be set manually because the custom BucketNotification resource
    - though works, but the stack deployment process is in pending state which results in an error in Github Actions)
    - **Lambda function** (from a pre-uploaded zip in S3) that resizes images placed in one bucket and saves the processed images into another bucket.  
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

## 📡 API Endpoints

| Category      | Method | Endpoint                                           | Description                     |
|---------------|--------|----------------------------------------------------|---------------------------------|
| **Auth**      | POST   | `/auth/`                                           | Register a new user             |
|               | POST   | `/auth/login`                                      | Login and retrieve access token |
|               | GET    | `/auth/protected`                                  | Just an auth test endpoint      |
| **Projects**  | GET    | `/projects/`                                       | List all projects               |
|               | POST   | `/projects/`                                       | Create a new project            |
|               | GET    | `/projects/{project_id}`                           | Retrieve a specific project     |
|               | PATCH  | `/projects/{project_id}`                           | Update a project                |
|               | DELETE | `/projects/{project_id}`                           | Delete a project                |
|               | POST   | `/projects/{project_id}/invite`                    | Invite a user to a project      |
| **Documents** | GET    | `/projects/{project_id}/documents/`                | List all documents in a project |
|               | POST   | `/projects/{project_id}/documents/`                | Upload a document               |
|               | GET    | `/projects/{project_id}/documents/{document_id}`   | Download a document             |
|               | PATCH  | `/projects/{project_id}/documents/{document_id}`   | Update document metadata        |
|               | DELETE | `/projects/{project_id}/documents/{document_id}`   | Delete a document               |
| **Health**    | GET    | `/`                                                | Health check endpoint           |


---

# 🏗 Project Architecture Overview

This project follows a layered (clean architecture) structure to keep the code modular, maintainable, and testable.

## 🏗 Project Architecture Overview

| Layer / Folder            | Purpose |
|----------------------------|---------|
| **`app/main.py`**          | Entry point of the FastAPI application. |
| **`app/domain/`**          | Business/domain logic (problem space):<br>- `entities/`: Core domain models (`User`, `Project`, `Document`, `UserProjectRole`).<br>- `repositories/`: Abstract repository interfaces.<br>- `storage/`: Abstract storage interfaces + utils.<br>- `exceptions/`: Domain-specific errors. |
| **`app/services/`**        | Application services — orchestrates business logic (e.g., `auth_service`, `project_service`, `document_service`, `user_project_role_service`). |
| **`app/infrastructure/`**  | Technology-specific implementations:<br>- `core/`: App config, DB, logger, security, shared exceptions.<br>- `orm/`: SQLAlchemy models.<br>- `sqlalchemy_*_repository.py`: Repository implementations.<br>- `storage/`: File system & S3 storage backends. |
| **`app/routers/`**         | API presentation layer:<br>- `api/v1/`: FastAPI route definitions (auth, projects, documents).<br>- `schemas/`: Pydantic request/response models.<br>- `dependencies.py`: Dependency injection. |
| **`aws/`**                 | Infrastructure as Code & Serverless:<br>- `cloudformation_ec2_rds.yml`: CloudFormation template for VPC, EC2, RDS PostgreSQL, S3, and Lambda setup.<br>- `lambda/`: Lambda function source, requirements, and deployment zip (image resizing). |
| **`scripts/`**             | Utility scripts (e.g., `recreate_db.py` for database reset). |
| **`tests/`**               | Automated tests organized by feature/layer (auth, infrastructure, project, root). |


## 📂 Project Structure
```
.
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── app
│   ├── domain
│   │   ├── enities
│   │   │   ├── document.py
│   │   │   ├── project.py
│   │   │   ├── user.py
│   │   │   └── user_project_role.py
│   │   ├── exceptions
│   │   │   ├── document_exceptions.py
│   │   │   ├── domain_exceptions.py
│   │   │   ├── project_exceptions.py
│   │   │   ├── user_exceptions.py
│   │   │   └── user_project_role_exceptions.py
│   │   ├── repositories
│   │   │   ├── document_repository.py
│   │   │   ├── project_repository.py
│   │   │   ├── user_project_role_repository.py
│   │   │   └── user_repository.py
│   │   └── storage
│   │       ├── document_storage.py
│   │       ├── exceptions
│   │       └── utils.py
│   ├── infrastructure
│   │   ├── core
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── exceptions.py
│   │   │   ├── logger.py
│   │   │   └── security.py
│   │   ├── orm
│   │   │   ├── document_model.py
│   │   │   ├── project_model.py
│   │   │   ├── user_model.py
│   │   │   └── user_project_role_model.py
│   │   ├── sqlalchemy_documet_repository.py
│   │   ├── sqlalchemy_project_repository.py
│   │   ├── sqlalchemy_user_project_role_repository.py
│   │   ├── sqlalchemy_user_repository.py
│   │   └── storage
│   │       ├── file_system_document_storage.py
│   │       └── s3_document_storage.py
│   ├── main.py
│   ├── routers
│   │   ├── api
│   │   │   └── v1
│   │   │       ├── auth_routes.py
│   │   │       ├── document_routes.py
│   │   │       └── project_routes.py
│   │   ├── dependencies.py
│   │   └── schemas
│   │       ├── auth_schemas.py
│   │       ├── document_schemas.py
│   │       └── project_schemas.py
│   └── services
│       ├── auth_service.py
│       ├── document_service.py
│       ├── project_service.py
│       └── user_project_role_service.py
├── aws
│   ├── cloudformation_ec2_rds.yml
│   └── lambda
│       ├── lambda_function.py
│       ├── lambda_function.zip
│       └── requirements.txt
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
    │   ├── test_file_system_document_storage.py
    │   ├── test_s3_document_storage.py
    │   └── test_sqlalchemy_user_repository.py
    ├── project
    │   └── test_project_service.py
    └── test_root.py

```


## 🔄 Continuous Integration (CI)

This project includes a **GitHub Actions workflow** that runs on:

- **Pushes and Pull Requests** to the `main` branch  
- **Weekly scheduled runs** (every Monday at midnight)  

1. **Code Quality Checks**
   - Runs on every push and pull request to `main`.
   - Steps:
     - **Import sorting** with `isort`.
     - **Linting** and auto-fixing issues using `Ruff`.
     - **Code formatting check** with `Black`.
     - **Security scan** using `Bandit`.
     - (Optional, currently commented) Static typing with `mypy`.

2. **Unit Tests**
   - Runs against multiple Python versions (`3.12`, `3.13`).
   - Executes the full test suite with `pytest`.
   - Ensures compatibility with the latest Python releases.

3. **Dependency Check**
   - Installs dev dependencies only.
   - Runs `poetry show --outdated` to check for outdated packages weekly.

4. **Build & Push to DockerHub**
   - Runs only if all previous jobs succeed on the `main` branch.
   - Steps:
     - Logs in to DockerHub using repository secrets.
     - Builds the Docker image with the application code.
     - Pushes the image to DockerHub, tagged with the current commit SHA.

5. **Deploy to AWS (via CloudFormation)**
   - Runs after a successful DockerHub push.
   - Steps:
     - Configures AWS credentials via GitHub secrets.
     - Validates the CloudFormation template (`aws/cloudformation_ec2_rds.yml`).
     - Deploys the stack with parameters (DB credentials, token secret, Docker image, etc.).
     - Creates/updates:
       - **VPC and networking stack**
       - **EC2 instance** running the Docker container
       - **RDS PostgreSQL database**
       - **S3 buckets** for document storage
       - **Lambda function** (from a pre-uploaded zip in S3) that resizes images between buckets.
     - Outputs the **public IP** of the deployed instance.

📂 Workflow file: `.github/workflows/ci_workflow.yml`

## 📄 License
This project is licensed under the **Apache License 2.0**.  

