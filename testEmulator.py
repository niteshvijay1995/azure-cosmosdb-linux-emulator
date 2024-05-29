import os
import uuid
from azure.cosmos import CosmosClient, PartitionKey, exceptions

# Configure the connection to the Cosmos DB emulator
endpoint = "https://127.0.0.1:8081/"
key = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
database_name = "SampleDatabase"
container_name = "SampleContainer"

# Initialize the Cosmos client
client = CosmosClient(endpoint, key)

try:
    # Create a database
    database = client.create_database_if_not_exists(id=database_name)
    print(f"Database '{database_name}' created or already exists")

    # Create a container
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/id")
    )
    print(f"Container '{container_name}' created or already exists")

    # Insert 100 documents
    for i in range(100):
        item = {
            'id': str(uuid.uuid4()),
            'name': f'Test Item {i+1}',
            'age': 30 + (i % 10)  # Adding some variation to the data
        }

        # Insert the item
        container.create_item(body=item)
    print("100 items inserted")

    # Query the inserted items
    query = "SELECT * FROM c WHERE c.name LIKE 'Test Item%'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    print(f"Queried items: {len(items)} items found")

except exceptions.CosmosHttpResponseError as e:
    print(f"An error occurred: {e}")

print("Cosmos DB emulator test completed successfully.")
