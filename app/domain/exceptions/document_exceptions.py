from uuid import UUID


class DocumentNotFoundError(Exception):
    """Raised when a Document is not found"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Document not found: {self.message}")


class DocumentRetrieveError(Exception):
    """Raised when couldn't return Document"""

    def __init__(self, message: str):
        super().__init__(f"Document retrieval failed: {message}")
        self.message = message


class DocumentCreateError(Exception):
    """Raised when couldn't create Document"""

    def __init__(self, message: str):
        super().__init__(f"Failed to create Document: {message}")
        self.message = message


class DocumentFileSaveError(Exception):
    """Raised when couldn't save Document on the filesystem"""

    def __init__(self, message: str):
        super().__init__(f"Failed to create Document: {message}")
        self.message = message


class DocumentFileDeleteError(Exception):
    """Raised when couldn't delete Document from the filesystem"""

    def __init__(self, message: str):
        super().__init__(f"Failed to delete Document: {message}")
        self.message = message


class DocumentDBDeleteError(Exception):
    """Raised when couldn't delete Document from the database"""

    def __init__(self, message: str):
        super().__init__(f"Failed to delete Document record: {message}")
        self.message = message
