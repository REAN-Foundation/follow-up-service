import uuid

from app.common.exceptions import UUIDValidationError

def validate_uuid4(uuid_str):
    try:
        val = uuid.UUID(uuid_str, version=4)
    except ValueError:
        raise UUIDValidationError("{uuid_str} is not valid UUID.")
    return uuid_str