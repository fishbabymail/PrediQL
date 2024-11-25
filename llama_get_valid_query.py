import os
import re
import yaml
import json
import logging
from parse_endpoint_results import ParseEndpointResults
from get_results_from_graphqler import *

from llama_initator import get_llm_model


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LlamaGetValidQuery:
    def __init__(self, base_path=None):
        if not base_path:
            self.base_path = os.getcwd()
        else:
            self.base_path = base_path
        self.end_path = os.path.join(self.base_path, "graphqler-output", "compiled")

        if not os.path.isdir(self.end_path):
            raise FileNotFoundError("Path {} does not exist. END".format(self.end_path))

    def get_compiled_queries(self, filename):
        filepath = os.path.join(self.end_path, filename)
        compiled_queries = None
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                compiled_queries = yaml.safe_load(f)
        return compiled_queries

    def get_object_buckets(self):
        filepath = os.path.join(self.base_path, "graphqler-output", "objects_bucket.txt")
        objects_marker = "------------------- OBJECTS BUCKET -------------------"
        scalars_marker = "------------------- SCALARS BUCKET -------------------"

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        objects_start = content.find(objects_marker) + len(objects_marker)
        scalars_start = content.find(scalars_marker) + len(scalars_marker)

        objects_str = content[objects_start:content.find(scalars_marker)].strip()
        scalars_str = content[scalars_start:].strip()

        return objects_str, scalars_str


    def get_valid_queries(self):
        # Get failure payloads and responses pairs
        per = ParseEndpointResults()
        payload_resp_pair = per.parse_result_to_dict()
        # print(payload_resp_pair)

        # Get compiled query schema
        compiled_queries = self.get_compiled_queries("compiled_queries.yml")
        compiled_mutations = self.get_compiled_queries("compiled_mutations.yml")
        compiled_objects = self.get_compiled_queries("compiled_objects.yml")

        # Get objects_bucket
        objects_str, scalars_str = self.get_object_buckets()

        query_json = {"query": []}
        tmp = """
            ```graphql
            {
            }
            ```
        """
        logger.info("Start to get valid queries from Llama.")
        for payload, response in payload_resp_pair.items():
            # Control running time
            if len(query_json["query"]) > 100:
                break
            prompt = (f"Based on the following information, please try to fix this graphql query and "
                      f"return me different possible valid queries, please use possible real values for "
                      f"parameters instead of placeholders. The query is :{payload}. "
                      f"The error response for this query is :{response}. The graphql query schema "
                      f"is: {compiled_queries}, the graphql mutation schema is: {compiled_mutations}, "
                      f"The graphql compiled objects schema is: {compiled_objects}."
                      f"The object values are: {objects_str}, the scalar values are: {scalars_str}. "
                      f"Please remember that your goal is to generate valid graphql queries according "
                      f"to all the information I provided to you.Each of the returned query should "
                      f"follow the format as: {tmp}.")
            llama_res = get_llm_model(prompt)
            # print("=============\nLLAMA PROMPT: \n", prompt)
            # print("=============\nLLAMA RESPONSE: \n", llama_res)
            flag = "```graphql"
            parse_time = 0
            while flag in llama_res and parse_time < 10:
                # Control running time
                if len(query_json["query"]) > 100:
                    break
                parse_time += 1
                try:
                    sidx = llama_res.find(flag)
                    j_start = llama_res[sidx+len(flag):]
                    j_end = j_start.find("```")
                    query_str = j_start[:j_end]
                    llama_res = j_start[j_end:]
                    # print(query_str)
                    if query_str not in query_json["query"]:
                        query_json["query"].append(query_str)
                    # logger.info("Parsed the response successfully.")
                except Exception as e:
                    logger.error(e)
                    break

            # print(query_json)
        return query_json

    # Save queries into file
    def save_json_to_file(self, query_json):
        filedir = os.path.join(self.base_path, "llama_query", "")
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        filepath = os.path.join(filedir, "llama_queries.json")
        with open(filepath, 'w') as f:
            json.dump(query_json, f, indent=4)
        logger.info("Saved query to {}".format(filepath))
        return True


    def run(self):
        query_json = self.get_valid_queries()
        self.save_json_to_file(query_json)



if __name__ == '__main__':
    llama_query = LlamaGetValidQuery()
    llama_query.run()
