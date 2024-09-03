from utils.decorators import ttl

from utils.type.jsonTypes import JsonType
import json
from . import session



@ttl(t=3600)
def _from_api() -> dict[str, JsonType]:
    db = session.get(f"/item/database", fullResult="True")
    with open("data/database.json", "r") as f:
        json.dump(db, f, indent=4)
    return db

def database() -> dict[str, JsonType]:
    try:
        db = _from_api()
    except TimeoutError:
        print("API get timed out, using local database!")
        with open("data/database.json", "r") as f:
            db = json.load(f)
    return db

