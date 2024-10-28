import requests
import json

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


#from numba.typed.listobject import new_list

from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    'llm': {
        'model': 'ollama/llama3',
        'temperature': 0.7
    },
    'embedding_model': 'ollama/nomic-embed-text',
    'output_format': 'json',
    'rendering': 'playwright'  # Enable JavaScript rendering, if supported
}
# Initialize the scraper graph with the configuration

# Define the URL and prompt for scraping
url = 'https://www.sfu.ca'
prompt = 'Extract all article titles and their associated URLs from the homepage, especially under the main content section.'

# Execute the scraping task
scraper = SmartScraperGraph(config=graph_config,prompt=prompt, source=url)
result = scraper.run()

# Process the result as needed
print(result)

