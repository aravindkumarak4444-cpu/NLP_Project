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

    async def find_one(self, query: dict):
        for doc in self.docs:
            match = True
            for k, v in query.items():
                if isinstance(v, dict) and "$regex" in v:
                    pattern = v["$regex"]
                    if pattern.lower() not in str(doc.get(k, '')).lower():
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                return dict(doc)
        return None

    async def find_one_and_update(self, query: dict, update: dict, return_document=True):
        doc = await self.find_one(query)
        if doc and "$set" in update:
            doc.update(update["$set"])
            return dict(doc)
        return doc

    async def delete_one(self, query: dict):
        doc = await self.find_one(query)
        if doc:
            self.docs.remove(doc)
            return type('DeleteResult', (), {'deleted_count': 1})()
        return type('DeleteResult', (), {'deleted_count': 0})()

    async def count_documents(self, query: dict):
        count = 0
        for doc in self.docs:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                count += 1
        return count

    def find(self, query: dict):
        return DictCursor(self.docs, query)

    async def create_index(self, keys, **kwargs):
        pass


class DictCursor:
    def __init__(self, docs: list, query: dict):
        self.docs = []
        for doc in docs:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                self.docs.append(doc)
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
