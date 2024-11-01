import os
import requests
import json
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Introspection query to fetch the schema
def get_official_schema(url, schema_dir, filename):

    # GraphQL query to get the schema
    query = """
        {
          __schema {
            types {
              name
              kind
              fields {
                name
                type {
                  name
                  kind
                }
              }
            }
          }
        }
    """

    # Set up the request headers
    headers = {
        'Content-Type': 'application/json'
    }

    # Send the POST request to the GitHub GraphQL API
    response = requests.post(
        url,
        headers=headers,
        json={'query': query}
    )

    # Check if the request was successful
    if response.status_code == 200:
        logger.info("Valid response returned from endpoint server.")
        schema_data = response.json()
        savepath = os.path.join(schema_dir, filename)
        if not os.path.exists(schema_dir):
            os.makedirs(schema_dir)
            logger.info("Create new directory {}".format(schema_dir))
        with open(savepath, 'w') as f:
            json.dump(schema_data, f)
            logger.info("save schema to {}".format(savepath))
    else:
        raise Exception(f"Query failed with status code {response.status_code}")


if __name__ == "__main__":
    endpoint = "https://rickandmortyapi.com/graphql"
    keyword_list = get_official_schema(endpoint, "graphql_schema", "rick_schema.json")
