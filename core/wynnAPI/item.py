from async_lru import alru_cache

from utils.type.jsonTypes import JsonType
from . import session


@alru_cache(ttl=3600)
async def database() -> dict[str, JsonType]:
    return await session.get(f"/item/database", fullResult="True")
