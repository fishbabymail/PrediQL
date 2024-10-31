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
              "be in JSON format, include typical CRUD operations, and "
              "cover cases like nested queries, optional parameters. "
              "Structure the output in JSON, ready to be saved to a file.")
    llama_res = get_llm_model(prompt)
    # print(llama_res)
    sidx = llama_res.find("json")
    if sidx == -1:
        raise Exception("Response from Llama is not formatted.")
    j_start = llama_res[sidx+4:]
    j_end = j_start.find("```")
    if j_end == -1:
        raise Exception("Response from Llama is not formatted.")
    query_str = j_start[:j_end]
    print(query_str)
    query_json = json.loads(query_str)
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
    saved = save_json_to_file(wf_dir, wf_name, query_json)

if __name__ == '__main__':
    main("graphql_schema", "rick_schema.json", "llama_query", "rick_query.json")
