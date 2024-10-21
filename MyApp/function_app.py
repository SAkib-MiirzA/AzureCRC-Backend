import azure.functions as func
import logging
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Cosmos DB client
cosmos_endpoint = 'https://db-00786.documents.azure.com:443/'  # Your Cosmos DB endpoint
cosmos_key = 'RIGVbyTdBO4fh33NNXbug4WyWsz26pxA5AD5VaTbWmVVoLAMVZHSk1NpiQJjhTBdaRlgxrframTVACDbSIbENA=='  # Your Cosmos DB key
database_name = 'sakib'  # Your database name
container_name = 'Counter'  # Your container name

# Create a Cosmos DB client
client = CosmosClient(cosmos_endpoint, cosmos_key)

# Get the database and container clients
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_triggersakib")
def http_triggersakib(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Check if the visitor count item exists
        try:
            visitor_count_item = container.read_item(item='visitor_count', partition_key='visitor_count')
            visitor_count = visitor_count_item['count']
        except exceptions.CosmosResourceNotFoundError:
            # If the item does not exist, start the count at 0
            visitor_count = 0

        # Increment the visitor count
        visitor_count += 1

        # Upsert the new count into Cosmos DB
        container.upsert_item({
            'id': 'visitor_count',  # Unique ID for the document
            'count': visitor_count
        })

        # Return only the visitor count as plain text
        return func.HttpResponse(
            str(visitor_count),  # Return the visitor count as plain text
            status_code=200
        )

    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Error storing item in Cosmos DB: {str(e)}")
        return func.HttpResponse(f"Failed to update the visitor count in Cosmos DB. Error: {str(e)}", status_code=500)
