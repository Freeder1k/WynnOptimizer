from utils.ttl_decorator import ttl

from utils.type.jsonTypes import JsonType
from . import session


@ttl(t=3600)
def database() -> dict[str, JsonType]:
    return session.get(f"/item/database", fullResult="True")
