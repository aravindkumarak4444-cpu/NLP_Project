import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.connection import db_manager, get_database


class DictCollection:
    def __init__(self, name: str):
        self.name = name
        self.docs = []

    async def insert_one(self, doc: dict):
        self.docs.append(dict(doc))
        return type('InsertOneResult', (), {'inserted_id': doc.get('_id', 'id_123')})()

def _match_doc(doc: dict, query: dict) -> bool:
    if not query:
        return True
    if "$or" in query:
        or_list = query["$or"]
        if not any(_match_doc(doc, q) for q in or_list):
            return False
    for k, v in query.items():
        if k == "$or":
            continue
        val = doc
        for part in k.split("."):
            if isinstance(val, dict):
                val = val.get(part)
            else:
                val = None
                break
        if isinstance(v, dict) and "$regex" in v:
            pattern = str(v["$regex"]).lower()
            if pattern not in str(val or "").lower():
                return False
        elif val != v:
            return False
    return True


class DictCollection:
    def __init__(self, name: str):
        self.name = name
        self.docs = []

    async def insert_one(self, doc: dict):
        self.docs.append(dict(doc))
        return type('InsertOneResult', (), {'inserted_id': doc.get('_id', 'id_123')})()

    async def find_one(self, query: dict):
        for doc in self.docs:
            if _match_doc(doc, query):
                return dict(doc)
        return None

    async def find_one_and_update(self, query: dict, update: dict, return_document=True):
        for doc in self.docs:
            if _match_doc(doc, query):
                if "$set" in update:
                    doc.update(update["$set"])
                return dict(doc)
        return None

    async def delete_one(self, query: dict):
        doc = await self.find_one(query)
        if doc:
            self.docs.remove(doc)
            return type('DeleteResult', (), {'deleted_count': 1})()
        return type('DeleteResult', (), {'deleted_count': 0})()

    async def count_documents(self, query: dict):
        return sum(1 for doc in self.docs if _match_doc(doc, query))

    def find(self, query: dict):
        return DictCursor(self.docs, query)

    async def create_index(self, keys, **kwargs):
        pass


class DictCursor:
    def __init__(self, docs: list, query: dict):
        self.docs = [d for d in docs if _match_doc(d, query)]
        self.index = 0

    def sort(self, key, direction):
        return self

    def skip(self, n):
        self.docs = self.docs[n:]
        return self

    def limit(self, n):
        self.docs = self.docs[:n]
        return self

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index < len(self.docs):
            doc = self.docs[self.index]
            self.index += 1
            return dict(doc)
        raise StopAsyncIteration


class MockDatabase:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, item: str):
        if item not in self.collections:
            self.collections[item] = DictCollection(item)
        return self.collections[item]

    @property
    def admin(self):
        class Admin:
            async def command(self, cmd):
                return {"ok": 1}
        return Admin()


mock_db = MockDatabase()


@pytest.fixture(autouse=True)
def override_db():
    db_manager.db = mock_db
    db_manager.client = mock_db
    app.dependency_overrides[get_database] = lambda: mock_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
