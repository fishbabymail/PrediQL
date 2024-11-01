import os
import requests
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_queries(filedir, filename):
    filepath = os.path.join(filedir, filename)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(filepath)
    with open(filepath, 'r') as f:
        queries = json.load(f)
    query_list = queries['query']
    return query_list


def request_query(url, query):
    # print(query)
    payload = {
        "query": query,
        "variables": {}
    }

    try:
        response = requests.post(url, json=payload)
    except:
        return False
    # print(response.text)
    if response.status_code == 200:
        response_text = response.text
        logger.info("Response:{}".format(response_text))
        logger.info("This query is valid.")
        return True
    else:
        logger.info("Failed to fetch data: {}".format(response.status_code))
        # logger.info("Error msg:", response.text)
        return False

def main(url, filedir, filename):
    query_list = get_queries(filedir, filename)
    for i, query in enumerate(query_list):
        res = request_query(url, query)


if __name__ == '__main__':
    url = "https://rickandmortyapi.com/graphql"
    main(url, "llama_query", "rick_query_ep.json")


