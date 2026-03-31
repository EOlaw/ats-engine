"""Utility class for file system operations."""

import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.core.exceptions import StorageException
from app.core.logging import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class FileUtils:
    """Collection of static utility methods for file operations.

    Provides async file saving, extension extraction, size validation,
    and file deletion. All async methods are safe for use in FastAPI
    request handlers without blocking the event loop.
    """

    @staticmethod
    async def save_upload(file: UploadFile, dest_dir: Path) -> Path:
        """Save an UploadFile to the destination directory.

        Creates the destination directory if it does not exist. Generates
        a UUID-prefixed filename to prevent conflicts.

        Args:
            file: The FastAPI UploadFile object to save.
            dest_dir: Directory where the file should be saved.

        Returns:
            The absolute Path where the file was saved.

        Raises:
            StorageException: If the directory cannot be created or the
                file cannot be written.
        """
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageException(
                f"Failed to create upload directory: {dest_dir}",
                details={"path": str(dest_dir), "error": str(exc)},
            ) from exc

        filename = file.filename or "upload"
        safe_filename = f"{uuid.uuid4().hex}_{Path(filename).name}"
        dest_path = dest_dir / safe_filename

        try:
            async with aiofiles.open(dest_path, "wb") as out_file:
                while True:
                    chunk = await file.read(1024 * 1024)  # 1 MB chunks
                    if not chunk:
                        break
                    await out_file.write(chunk)
        except OSError as exc:
            raise StorageException(
                f"Failed to write upload file: {dest_path.name}",
                details={"path": str(dest_path), "error": str(exc)},
            ) from exc

        logger.debug("File saved", path=str(dest_path), filename=filename)
        return dest_path

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Extract the lowercase file extension from a filename.

        Args:
            filename: The filename string (with or without path components).

        Returns:
            Lowercase extension string without the leading dot, e.g. 'pdf'.
            Returns an empty string if the filename has no extension.
        """
        return Path(filename).suffix.lower().lstrip(".")

    @staticmethod
    def validate_file_size(file_size: int, max_mb: int) -> bool:
        """Validate that a file size is within the allowed limit.

        Args:
            file_size: File size in bytes.
            max_mb: Maximum allowed file size in megabytes.

        Returns:
            True if the file is within the size limit, False otherwise.
        """
        max_bytes = max_mb * 1024 * 1024
        return file_size <= max_bytes

    @staticmethod
    async def delete_file(path: Path) -> None:
        """Asynchronously delete a file if it exists.

        Does not raise an error if the file does not exist, but logs
        a warning. Raises StorageException on permission or OS errors.

        Args:
            path: Absolute path to the file to delete.

        Raises:
            StorageException: If deletion fails due to a permissions or OS error.
        """
        import asyncio

        if not path.exists():
            logger.warning("File to delete not found", path=str(path))
            return

        try:
            await asyncio.get_event_loop().run_in_executor(None, path.unlink)
            logger.debug("File deleted", path=str(path))
        except OSError as exc:
            raise StorageException(
                f"Failed to delete file: {path.name}",
                details={"path": str(path), "error": str(exc)},
            ) from exc

    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """Create a directory and all parent directories if they don't exist.

        Args:
            path: The directory path to create.

        Returns:
            The created (or pre-existing) directory path.

        Raises:
            StorageException: If directory creation fails.
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except OSError as exc:
            raise StorageException(
                f"Failed to create directory: {path}",
                details={"path": str(path), "error": str(exc)},
            ) from exc
