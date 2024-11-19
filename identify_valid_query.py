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
    query_list = queries["query"]
    return query_list


def request_query(url, query):
    # print(query)
    payload = {
        "query": query,
        "variables": {}
    }

    try:
        response = requests.post(url, json=payload)
        print(response.text)
    except:
        logger.error("Exception request for query: {}".format(query))
        return
    if response.status_code == 200:
        response_text = response.text
        logger.info("Response:{}".format(response_text))
        logger.info("This query is valid.")
        return query
    else:
        logger.error("Failed to fetch data: {}".format(response.status_code))
        return


def run(url):
    valid_queries = []
    filedir = os.path.join(os.getcwd(), "llama_query")
    filename = "llama_queries.json"
    query_list = get_queries(filedir, filename)
    for i, query in enumerate(query_list):
        res = request_query(url, query)
        if not res:
            valid_queries.append(query)

    res = {
        "query": valid_queries
    }

    save_name = "valid_query.json"
    filename = os.path.join(filedir, save_name)
    with open(filename, 'w') as f:
        json.dump(res, f)
    logger.info("Saved valid query to {}".format(filename))


if __name__ == '__main__':
    url = "https://rickandmortyapi.com/graphql"
    run(url)


