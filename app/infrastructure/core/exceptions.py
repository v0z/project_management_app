class DatabaseError(Exception):
    """Custom exception for database-related errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
