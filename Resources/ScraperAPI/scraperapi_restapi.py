import requests
import json
import warnings
from scrapegraphai.graphs import SmartScraperGraph

warnings.simplefilter(action='ignore', category=FutureWarning)

# Define the REST API endpoint URL
url = 'https://api.openbrewerydb.org/breweries'

# Send a GET request to the REST API endpoint
response = requests.get(url)

# Initialize an empty data dictionary to avoid NameError
data = {}

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Extract the data based on the JSON structure
    brewery_names = []
    brewery_urls = []

    for item in data:
        brewery_names.append(item.get("name"))
        brewery_urls.append(item.get("website_url"))

    # Print the extracted data
    print({"brewery_names": brewery_names, "brewery_urls": brewery_urls})
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")

# If the data was retrieved, save it to a local file for further processing with ScrapeGraphAI
if data:
    with open('breweries_data.json', 'w') as f:
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
    prompt = "Extract all brewery names and URLs from the JSON data."
    source = 'breweries_data.json'

    # Execute the scraping task with ScrapeGraphAI
    scraper = SmartScraperGraph(config=graph_config, prompt=prompt, source=source)
    result = scraper.run()

    # Process the result as needed
    print(result)
else:
    print("No data to process with ScrapeGraphAI.")
