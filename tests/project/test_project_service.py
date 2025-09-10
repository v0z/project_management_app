from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from app.domain.enities import Project
from app.domain.enities.document import Document
from app.domain.enities.user_project_role import RoleEnum
import pytest
from app.services.project_service import ProjectService


def test_add_project():
    mock_repo = Mock()
    mock_storage = Mock()
    mock_role_service = Mock()

    service = ProjectService(repo=mock_repo, storage=mock_storage, role_service=mock_role_service)

    user_id = uuid4()
    test_project = Project(
        id=uuid4(),
        name="test_name",
        description="test_description",
        owner=user_id,
        created_at=datetime.now(timezone.utc)
    )

    # repo should return the test project
    mock_repo.add.return_value = test_project

    # act
    result = service.add_project(name="test_name", description="test_description", user_id=user_id)

    # check project
    assert result == test_project
    assert result.name == "test_name"
    assert result.description == "test_description"
    assert result.owner == user_id

    # check method calls
    mock_repo.add.assert_called_once()
    mock_role_service.add_role.assert_called_once_with(project_id=test_project.id, user_id=user_id, role=RoleEnum.OWNER)

def test_get_all_projects():
    mock_repo = Mock()
    mock_storage = Mock()
    mock_role_service = Mock()

    service = ProjectService(repo=mock_repo, storage=mock_storage, role_service=mock_role_service)
    user_id = uuid4()

    test_project = Project(
        id=uuid4(),
        name="test_name",
        description="test_description",
        owner=user_id,
        created_at=datetime.now(timezone.utc)
    )
    test_project2 = Project(
        id=uuid4(),
        name="test_name2",
        description="test_description2",
        owner=user_id,
        created_at=datetime.now(timezone.utc)
    )

    mock_repo.list_by_user.return_value = [test_project, test_project2]

    # act
    result = service.get_all_projects(user_id=user_id)

    assert isinstance(result, list)
    assert result == [test_project, test_project2]
    assert mock_repo.list_by_user.call_count == 1


def test_get_project():
    mock_repo = Mock()
    mock_storage = Mock()
    mock_role_service = Mock()

    service = ProjectService(repo=mock_repo, storage=mock_storage, role_service=mock_role_service)
    user_id = uuid4()
    project_id = uuid4()

    test_project = Project(
        id=project_id,
        name="test_name",
        description="test_description",
        owner=user_id,
        created_at=datetime.now(timezone.utc)
    )

    # repo returns a project
    mock_repo.get_by_id.return_value = test_project
    service.is_project_participant = Mock(return_value=True)

    result = service.get_project(project_id=project_id, user_id=user_id)

    assert result == test_project
    assert result.id == project_id
    assert mock_repo.get_by_id.call_count == 1
    service.is_project_participant.assert_called_once_with(project=test_project, user_id=user_id)

@pytest.mark.asyncio
async def test_delete_project():
    mock_repo = Mock()
    mock_storage = AsyncMock()
    mock_role_service = Mock()

    service = ProjectService(repo=mock_repo, storage=mock_storage, role_service=mock_role_service)
    user_id = uuid4()
    project_id = uuid4()

    test_project = Project(
        id=project_id,
        name="Test Project",
        description="desc of test project",
        owner=user_id,
        created_at=datetime.now(timezone.utc),
        documents=[Document(id=uuid4(), project_id=project_id, content_type="image/jpg", created_at=datetime.now(timezone.utc),
                            storage_path="documents/file.jpg", file_name="file.jpg", storage_backend="local")],
    )

    mock_repo.get_by_id.return_value = test_project
    service.is_project_owner = Mock(return_value=True)
    mock_repo.delete.return_value = True

    result = await service.delete_project(project_id=project_id, user_id=user_id)

    assert result is True
    mock_repo.get_by_id.assert_called_once_with(project_id=project_id)
    mock_storage.remove.assert_awaited_once_with(storage_path="documents/file.jpg")

