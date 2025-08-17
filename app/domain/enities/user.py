from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    """User entity."""
    id: UUID
    username: str
    email: str
    password_hash: str

    def __post_init__(self):
        if not isinstance(self.id, UUID):
            raise ValueError("id must be a UUID instance")
