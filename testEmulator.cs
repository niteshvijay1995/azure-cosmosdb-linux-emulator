using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Azure.Cosmos;

namespace CosmosDbExample
{
    class Program
    {
        private static readonly string endpoint = "https://localhost:8081/";
        private static readonly string key = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==";
        private static readonly string databaseName = "SampleDatabase";
        private static readonly string containerName = "SampleContainer";
        private static CosmosClient cosmosClient;

        static async Task Main(string[] args)
        {
            cosmosClient = new CosmosClient(endpoint, key);

            await CreateDatabaseAsync();
            await CreateContainerAsync();
            await InsertItemsAsync();
            await QueryItemsAsync();
        }

        private static async Task CreateDatabaseAsync()
        {
            Database database = await cosmosClient.CreateDatabaseIfNotExistsAsync(databaseName);
            Console.WriteLine($"Database '{databaseName}' created or already exists.");
        }

        private static async Task CreateContainerAsync()
        {
            Container container = await cosmosClient.GetDatabase(databaseName).CreateContainerIfNotExistsAsync(containerName, "/id");
            Console.WriteLine($"Container '{containerName}' created or already exists.");
        }

        private static async Task InsertItemsAsync()
        {
            Container container = cosmosClient.GetContainer(databaseName, containerName);

            for (int i = 0; i < 10000; i++)
            {
                var item = new
                {
                    id = Guid.NewGuid().ToString(),
                    name = $"Test Item {i + 1}",
                    age = 30 + (i % 10),
                    size = i + 1
                };

                // Add random fields
                var randomFields = new Dictionary<string, int>();
                Random rand = new Random();
                for (int j = 1; j <= 10; j++)
                {
                    randomFields[$"field{j}"] = rand.Next(1, 101);
                }

                // Combine with the item
                var combinedItem = new { item.id, item.name, item.age, item.size, randomFields };

                await container.CreateItemAsync(combinedItem, new PartitionKey(combinedItem.id));
            }
        }

        private static async Task QueryItemsAsync()
        {
            Container container = cosmosClient.GetContainer(databaseName, containerName);

            // Query items with age greater than 35
            string query = "SELECT * FROM c WHERE c.age > 35";
            var queryResult = container.GetItemQueryIterator<dynamic>(query);
            int count = 0;

            while (queryResult.HasMoreResults)
            {
                foreach (var item in await queryResult.ReadNextAsync())
                {
                    count++;
                }
            }
            Console.WriteLine($"Queried items: {count} items found with age > 35");

            // Query items with size less than or equal to 50
            query = "SELECT * FROM c WHERE c.size <= 50";
            queryResult = container.GetItemQueryIterator<dynamic>(query);
            count = 0;

            while (queryResult.HasMoreResults)
            {
                foreach (var item in await queryResult.ReadNextAsync())
                {
                    count++;
                }
            }
            Console.WriteLine($"Queried items: {count} items found with size <= 50");
        }
    }
}
