import os
import requests
import json
import logging

from llama_initator import get_llm_model


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_queries(url, filedir, filename):
    filepath = os.path.join(filedir, filename)
    if not os.path.isfile(filepath):
        raise Exception("There is no query file {}".format(filepath))
    with (open(filepath, 'r') as f):
        schema = json.load(f)
    prompt = f"Please generate some queries for the endpoint {url}."
    retry_n = 0
    query_json = {"query": []}
    while len(query_json["query"]) < 10 and retry_n < 3:
        retry_n += 1
        logger.info("The {} 's attempt to parse the response".format(retry_n))
        llama_res = get_llm_model(prompt)
        # print(llama_res)
        flag = "query {"
        while flag in llama_res:
            sidx = llama_res.find(flag)
            j_start = llama_res[sidx:]
            j_end = j_start.find("```")
            query_str = j_start[:j_end]
            llama_res = j_start[j_end:]
            # print(query_str)
            if query_str not in query_json["query"]:
                query_json["query"].append(query_str)

        logger.info("Parsed the response successfully.")
        # print(query_json)
    return query_json

def save_json_to_file(filedir, filename, query_json):
    filepath = os.path.join(filedir, filename)
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    with open(filepath, 'w') as f:
        json.dump(query_json, f, indent=4)
    logger.info("Saved query to {}".format(filepath))
    return True

def main(url, rf_dir, rf_name, wf_dir, wf_name):
    query_json = get_queries(url, rf_dir, rf_name)
    if query_json == {}:
        raise Exception("There is no valid query file {} generated with 3 times prompts ".format(rf_name))
    saved = save_json_to_file(wf_dir, wf_name, query_json)
    return saved


if __name__ == '__main__':
    url = "https://rickandmortyapi.com/graphql"
    main(url, "graphql_schema", "rick_schema.json", "llama_query", "rick_query_ep.json")
