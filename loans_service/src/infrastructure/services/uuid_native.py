import uuid
from ...domain.ports.uuid_gen import UUIDGen


class NativeUuid(UUIDGen):
    def new(self) -> str:
        return str(uuid.uuid4())