from pathlib import Path
from uuid import UUID

import aiofiles
from fastapi import UploadFile

from app.domain.storage.document_storage import DocumentStorage
from app.domain.storage.utils import filename_normalizer


class FileSystemDocumentStorage(DocumentStorage):
    """A local file system storage implementation"""

    def __init__(self, upload_dir: str = "documents"):
        self.upload_dir = Path(upload_dir)
        self.storage_backend = "local"

    async def save(self, project_id: UUID, uploaded_file: UploadFile) -> tuple:
        """Save the uploaded file to the filesystem and return its metadata"""

        content_type = uploaded_file.content_type

        # a folder that will be used to store all documents uploaded to project (from project_id uuid)
        project_folder = project_id.hex

        # sanitize the file name
        normalized_file_name = filename_normalizer(uploaded_file.filename)

        # full path to save the file
        storage_path = self.upload_dir.joinpath(project_folder, normalized_file_name)

        # ensure the directories exists
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        # write the file
        async with aiofiles.open(storage_path, "wb") as file_object:
            content = uploaded_file.file.read()
            await file_object.write(content)

        return normalized_file_name, content_type, str(storage_path), self.storage_backend

    async def remove(self, storage_path: str) -> None:
        """Delete a file from the filesystem given its storage path"""

        file_path = Path(storage_path)

        # remove document
        if file_path.exists():
            file_path.unlink()

        # remove project directory if its empty
        project_dir_is_empty = not any(file_path.parent.iterdir())
        if project_dir_is_empty:
            file_path.parent.rmdir()
