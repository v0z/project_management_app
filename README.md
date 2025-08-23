# A CRUD application built with FASTAPI


## Project Structure:
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
│   │       └── project_service.py
│   ├── core
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   └── security.py
│   ├── domain
│   │   ├── enities
│   │   │   ├── project.py
│   │   │   └── user.py
│   │   ├── exceptions
│   │   │   └── user_exceptions.py
│   │   └── repositories
│   │       ├── project_repository.py
│   │       └── user_repository.py
│   ├── infrastructure
│   │   ├── orm
│   │   │   ├── project_model.py
│   │   │   └── user_model.py
│   │   ├── sqlalchemy_project_repository.py
│   │   └── sqlalchemy_user_repository.py
│   ├── main.py
│   └── presentation
│       ├── api
│       │   └── v1
│       │       ├── auth_routes.py
│       │       └── project_routes.py
│       ├── dependencies.py
│       └── schemas
│           └── auth_schemas.py
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


### Generate a SECRET KEY:
`openssl rand -hex 32`


`ALTER TABLE users ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();`