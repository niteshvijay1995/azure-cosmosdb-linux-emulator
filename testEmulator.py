import os
import uuid
from azure.cosmos import CosmosClient, PartitionKey, exceptions

class CosmosDbService:
    def __init__(self):
        # Cosmos DB Emulator connection string
        self.endpoint = "https://127.0.0.1:8081/"
        self.key = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
        self.database_name = "SampleDatabase"
        self.container_name = "SampleContainer"
        self.client = CosmosClient(self.endpoint, self.key)
        self.database: DatabaseProxy = None
        self.container: ContainerProxy = None

    async def initialize(self):
        # Create database and container if they do not exist
        self.database = await self.client.create_database_if_not_exists(id=self.database_name)
        self.container = await self.database.create_container_if_not_exists(
            id=self.container_name,
            partition_key=PartitionKey(path="/id")
        )

    async def add_item(self, item):
        await self.container.create_item(body=item)

    async def get_item(self, item_id):
        try:
            item_response = await self.container.read_item(item=item_id, partition_key=item_id)
            return item_response
        except exceptions.CosmosResourceNotFoundError:
            return None

    async def query_items(self, query):
        items = self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        )
        async for item in items:
            print(item)

class Item:
    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age
        }

async def main():
    cosmos_db_service = CosmosDbService()
    await cosmos_db_service.initialize()

    # Insert 100 random items
    names = ["John Doe", "Jane Smith", "Alice Johnson", "Bob Brown", "Charlie Davis"]
    for _ in range(100):
        new_item = Item(id=str(uuid.uuid4()), name=random.choice(names), age=random.randint(20, 60))
        await cosmos_db_service.add_item(new_item.to_dict())

    print("Inserted 100 items")

    # Query items
    query_string = "SELECT * FROM c WHERE c.age > 25"
    await cosmos_db_service.query_items(query_string)

if __name__ == "__main__":
    asyncio.run(main())
