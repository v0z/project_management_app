from app.core.database import Base, engine
from app.infrastructure.orm import *


def run():
    print("Dropping existing database tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating new database tables...")
    Base.metadata.create_all(bind=engine)

    print("Database tables recreated successfully.")


if __name__ == "__main__":
    run()
