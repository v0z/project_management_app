import io
import pytest
from uuid import uuid4
from moto import mock_aws
from fastapi import UploadFile
from app.infrastructure.storage.s3_document_storage import S3DocumentStorage


@pytest.fixture
def storage(monkeypatch):
    """Fixture that sets up mocked S3 with our storage class."""
    with mock_aws():
        monkeypatch.setattr("app.core.config.settings.aws_s3_bucket_name", "test-bucket")
        monkeypatch.setattr("app.core.config.settings.aws_access_key_id", "test")
        monkeypatch.setattr("app.core.config.settings.aws_secret_access_key", "test")

        storage = S3DocumentStorage()
        yield storage


@pytest.mark.asyncio
async def test_save(storage):
    project_id = uuid4()
    upload = UploadFile(filename="test.png", file=io.BytesIO(b"\x89PNG\r\n"), headers={"content-type": "image/png"})

    file_name, ctype, key, backend = await storage.save(project_id, upload)

    assert file_name == "test.png"
    assert ctype == "image/png"
    assert backend == "s3"
    assert storage.client.get_object(Bucket=storage.bucket_name, Key=key)["Body"].read() == b"\x89PNG\r\n"


@pytest.mark.asyncio
async def test_download(storage):
    # put an object directly in mocked S3
    key = "test-bucket/test.png"
    content = b"\x89PNG\r\n"
    storage.client.put_object(Bucket=storage.bucket_name, Key=key, Body=content)

    s3_object = await storage.download(storage_key=key)

    assert "Body" in s3_object
    assert s3_object["Body"].read() == content


@pytest.mark.asyncio
async def test_remove(storage):
    # put an object directly in mocked S3
    key = "test-bucket/test.png"
    content = b"\x89PNG\r\n"
    storage.client.put_object(Bucket=storage.bucket_name, Key=key, Body=content)

    # Ensure it exists
    obj = storage.client.get_object(Bucket=storage.bucket_name, Key=key)
    assert obj["Body"].read() == content

    # remove the file
    await storage.remove(key)

    parent_prefix = key.split("/")[0]

    # Check if any objects are left in this "directory"
    response = storage.client.list_objects_v2(Bucket=storage.bucket_name, Prefix=parent_prefix, MaxKeys=1)

    assert "Contents" not in response  # no objects left
