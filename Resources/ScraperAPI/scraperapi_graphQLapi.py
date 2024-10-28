import requests
import json
import warnings
from scrapegraphai.graphs import SmartScraperGraph

warnings.simplefilter(action='ignore', category=FutureWarning)

# Define the GraphQL endpoint URL
url = 'https://swapi-graphql.netlify.app/.netlify/functions/index'

# Define a GraphQL query payload
payload = {
    "query": """
    {
      allPeople {
        people {
          name
        }
      }
    }
    """
}

# Send a POST request to the GraphQL API endpoint
response = requests.post(url, json=payload)

# Initialize an empty data dictionary to avoid NameError
data = {}

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Extract the data based on the JSON structure
    character_names = [person['name'] for person in data['data']['allPeople']['people']]

    # Print the extracted data
    print({"character_names": character_names})
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")

# If the data was retrieved, save it to a local file for further processing with ScrapeGraphAI
if data:
    with open('character_data.json', 'w') as f:
        json.dump(data, f)

    # Define the configuration for ScrapeGraphAI
    graph_config = {
        'llm': {
            'model': 'ollama/llama3',
            'temperature': 0.7
        },
        'embedding_model': 'ollama/nomic-embed-text',
        'output_format': 'json',
        'data_type': 'json'
    }

    # Define prompt and source (local JSON file)
    prompt = "Extract all information to build a GraphQL schema from the JSON data, without GraphQL introspection query."
    source = 'character_data.json'

    # Execute the scraping task with ScrapeGraphAI
    scraper = SmartScraperGraph(config=graph_config, prompt=prompt, source=source)
    result = scraper.run()

    # Process the result as needed
    print(result)
else:
    print("No data to process with ScrapeGraphAI.")
