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


def get_queries(filedir, filename):
    filepath = os.path.join(filedir, filename)
    if not os.path.isfile(filepath):
        raise Exception("There is no query file {}".format(filepath))
    with (open(filepath, 'r') as f):
        schema = json.load(f)
    prompt = (f"Generate GraphQL queries for fuzzing an API endpoint, "
              f"the schema of this endpoint is {schema}. The queries should "
              f"explore various fields, include different types of input, "
              f"and vary in structure to test the endpoint's robustness. "
              f"In addition, the queries must can be sent to the endpoint directly."
              f"Structure the output in JSON, ready to be saved to a file.")
    SAVED = False
    retry_n = 0
    query_json = {}
    while not SAVED and retry_n < 3:
        logger.info("The {} 's attemp to parse the response".format(retry_n))
        llama_res = get_llm_model(prompt)
        # print(llama_res)
        sidx = llama_res.find("json")
        if sidx == -1:
            logger.info("The {}'s Response from Llama is not formatted.".format(retry_n))
            retry_n += 1
            continue
        j_start = llama_res[sidx+4:]
        j_end = j_start.find("```")
        if j_end == -1:
            logger.info("The {}'s Response from Llama is not formatted.".format(retry_n))
            retry_n += 1
            continue
        query_str = j_start[:j_end]
        # print(query_str)
        try:
            query_json = json.loads(query_str)
        except:
            logger.info("Failed to decode to json file, RETRY.")
            retry_n += 1
            continue

        SAVED = True
        logger.info("Parsed the response successfully.")
    return query_json

def save_json_to_file(filedir, filename, query_json):
    filepath = os.path.join(filedir, filename)
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    with open(filepath, 'w') as f:
        json.dump(query_json, f, indent=4)
    logger.info("Saved query to {}".format(filepath))
    return True

def main(rf_dir, rf_name, wf_dir, wf_name):
    query_json = get_queries(rf_dir, rf_name)
    if query_json == {}:
        raise Exception("There is no valid query file {} generated with 3 times prompts ".format(rf_name))
    saved = save_json_to_file(wf_dir, wf_name, query_json)
    return saved


if __name__ == '__main__':
    main("graphql_schema", "rick_schema.json", "llama_query", "rick_query.json")
