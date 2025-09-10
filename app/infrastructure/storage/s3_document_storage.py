import asyncio
from uuid import UUID

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from mypy_boto3_s3.client import S3Client

from app.domain.storage.document_storage import DocumentStorage
from app.domain.storage.utils import filename_normalizer
from app.infrastructure.core.config import settings
from app.infrastructure.core.logger import logger


class S3DocumentStorage(DocumentStorage):
    """AWS S3 storage implementation"""

    # TODO Add custom exceptions

    def __init__(self):
        self.bucket_name: str = settings.aws_s3_bucket_name
        s3 =  boto3.client(
            "s3",
            # commented out to force to use instance profile credentials automatically.
            # aws_access_key_id=settings.aws_access_key_id,
            # aws_secret_access_key=settings.aws_secret_access_key
        )
        region = s3.meta.region_name
        self.client: S3Client = boto3.client(
            "s3",
            # aws_access_key_id=settings.aws_access_key_id,
            # aws_secret_access_key=settings.aws_secret_access_key, region_name=region
        )
        # Ensure bucket exists at initialization if not will call create bucket method
        self._ensure_bucket_exists()

    @property
    def storage_backend(self) -> str:
        return "s3"

    def create_bucket(self) -> None:
        """Create an Amazon S3 bucket in the default Region for the account"""
        try:
            region = self.client.meta.region_name
            if region != "us-east-1":
                self.client.create_bucket(
                    Bucket=self.bucket_name, CreateBucketConfiguration={"LocationConstraint": region}
                )
            else:
                self.client.create_bucket(Bucket=self.bucket_name)

            # TODO: Fix the autocreation of bucket (Sandbox Has Permissions issue. Test on my own account)

            # #  Wait until bucket is actually created
            # waiter = self.client.get_waiter("bucket_exists")
            # waiter.wait(Bucket=self.bucket_name)

        except ClientError as e:
            logger.error(f"Couldn't create bucket named {self.bucket_name}")
            raise e

    def _ensure_bucket_exists(self):
        """
        Checks if a bucket with the name specified in "bucket_name" property exists
        Creates the bucket if it does not exist - calling the "create_bucket" method
        """
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response.get("Error").get("Code")
            if error_code == "404":
                # bucket does not exist - create it
                try:
                    self.create_bucket()
                except Exception as e:
                    logger.error(f"bucket is not created {e}")

    async def save(self, project_id: UUID, uploaded_file: UploadFile) -> tuple:
        """
        Uploads the file to S3 under a project folder.
        Returns a tuple of file_name, content_type and S3 storage_key (prefix)
        """

        content_type = uploaded_file.content_type

        # a folder that will be used to store all documents uploaded to project (from project_id uuid)
        project_folder = project_id.hex

        # sanitize the file name
        normalized_file_name = filename_normalizer(uploaded_file.filename)

        # s3 key, (s3 prefix)
        storage_key = f"{project_folder}/{normalized_file_name}"

        # upload file-like object to s3 directly
        self.client.upload_fileobj(uploaded_file.file, self.bucket_name, storage_key)

        return normalized_file_name, content_type, storage_key, self.storage_backend

    def get_signed_url(self, storage_key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL to download a file from S3"""

        url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": storage_key},
            ExpiresIn=expires_in,  # time in seconds (default 1 hour)
        )
        return url

    async def download(self, storage_key: str):
        """Downloads a file-like object from S3 and returns it to be used in a StreamingResponse"""
        s3_object = await asyncio.to_thread(self.client.get_object, Bucket=self.bucket_name, Key=storage_key)
        return s3_object

    async def remove(self, storage_path: str) -> None:
        # run synchronous boto3 call in a separate thread
        await asyncio.to_thread(self.client.delete_object, Bucket=self.bucket_name, Key=storage_path)

        parent_prefix = storage_path.split("/")[0]

        # Check if any objects are left in this "directory"
        response = await asyncio.to_thread(
            self.client.list_objects_v2, Bucket=self.bucket_name, Prefix=parent_prefix, MaxKeys=1
        )

        if "Contents" not in response:
            # no files in "folder"
            try:
                await asyncio.to_thread(self.client.delete_object, Bucket=self.bucket_name, Key=parent_prefix)
            except self.client.exceptions.NoSuchKey:
                pass
