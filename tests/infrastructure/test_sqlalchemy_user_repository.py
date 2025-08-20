from uuid import UUID

from app.infrastructure.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.infrastructure.orm.user_model import UserORM
from app.domain.enities.user import User as DomainUser
from sqlalchemy.orm import Session
from unittest.mock import MagicMock


def test_get_by_id():
    # Mock the database session
    db_session = MagicMock(spec=Session)

    # Create an instance of the repository
    repo = SQLAlchemyUserRepository(db=db_session)

    test_user_id = UUID("12345678-1234-5678-1234-567812345678")

    # Mock the ORM object returned by the query
    mock_orm_user = UserORM(
        id=test_user_id,
        username="testuser",
        email="a@a.com",
        password_hash="hashed_password",
    )

    db_session.query.return_value.filter.return_value.first.return_value = mock_orm_user

    # Call the method under test
    result = repo.get_by_id(test_user_id)
    expected_user = DomainUser(
        id=test_user_id,
        username="testuser",
        email="a@a.com",
        password_hash="hashed_password",
    )
    # Assert the result
    assert result == expected_user
