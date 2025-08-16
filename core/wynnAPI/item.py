from utils.decorators import ttl

from utils.type.jsonTypes import JsonType
import json
from . import session


@ttl(t=3600)
def _from_api() -> dict[str, JsonType]:
    print('Fetching item database from API...')
    db = session.get(f"/item/database", fullResult="")
    with open("data/database.json", "w") as f:
        json.dump(db, f, indent=4)
    return db


def database() -> dict[str, JsonType]:
    try:
        db = _from_api()
    except Exception as e:
        print(f"Error fetching database from API: {e}")
        with open("data/database.json", "r") as f:
            db = json.load(f)
    return db

