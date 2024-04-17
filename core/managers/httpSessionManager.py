import aiohttp
from aiohttp import ClientSession
from yarl import URL


class HTTPSessionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HTTPSessionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._sessions: dict[int, ClientSession] = {}
        self._session_urls: dict[int, str | URL | None] = {}
        self._initialized = True
        self._started = False
        self._next_id = 0

    def register_session(self, base_url: str | URL = None) -> int:
        curr_id = self._next_id
        self._next_id += 1

        self._session_urls[curr_id] = base_url
        if self._started:
            self._sessions[curr_id] = aiohttp.ClientSession(base_url)

        return curr_id

    def get_session(self, session_id: int) -> ClientSession:
        if session_id not in self._sessions:
            raise ValueError(f"There is no session with ID {session_id}.")

        return self._sessions[session_id]

    async def start(self):
        for s_id, url in self._session_urls.items():
            self._sessions[s_id] = aiohttp.ClientSession(url)
        self._started = True

    async def close(self):
        for session in self._sessions.values():
            await session.close()
        self._sessions.clear()
        self._started = False
