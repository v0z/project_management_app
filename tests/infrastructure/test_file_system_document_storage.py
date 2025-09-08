import io, pytest
from uuid import uuid4

from fastapi import UploadFile

from app.infrastructure.storage.file_system_document_storage import FileSystemDocumentStorage


@pytest.fixture
def storage():
    storage = FileSystemDocumentStorage()
    yield storage

@pytest.mark.asyncio
async def test_save(tmp_path, storage):
    storage.upload_dir = tmp_path

    project_id = uuid4()
    file_content = b"\x89PNG\r\n"
    upload = UploadFile(filename="test.png", file=io.BytesIO(file_content), headers={"content-type": "image/png"})

    file_name, ctype, path, backend = await storage.save(project_id, upload)

    assert file_name == "test.png"
    assert ctype == "image/png"
    assert backend == "local"

    with open(path, "rb") as file:
        content = file.read()
    assert content == file_content


@pytest.mark.asyncio
async def test_remove_image(tmp_path, storage):
    storage.upload_dir = tmp_path

    project_id = uuid4()
    file_name = "test.png"
    file_content = b"\x89PNG\r\n"

    # Simulate saving the file
    project_dir = tmp_path / project_id.hex
    project_dir.mkdir(parents=True)
    file_path = project_dir / file_name
    file_path.write_bytes(file_content)

    # Ensure file exists before removal
    assert file_path.exists()
    assert any(project_dir.iterdir())

    # Act: remove the file
    await storage.remove(str(file_path))

    # Assert: file is deleted
    assert not file_path.exists()

    # Assert: parent directory is removed if empty
    assert not project_dir.exists()