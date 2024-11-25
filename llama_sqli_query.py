import os
import yaml
import json
import logging
from parse_endpoint_results import ParseEndpointResults

from llama_initator import get_llm_model


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LlamaGetSQLIQuery:
    def __init__(self, base_path=None):
        if not base_path:
            self.base_path = os.getcwd()
        else:
            self.base_path = base_path
        self.end_path = os.path.join(self.base_path, "llama_query")

        if not os.path.isdir(self.end_path):
            raise FileNotFoundError("Path {} does not exist. END".format(self.end_path))

    def get_sqli_queries(self):

        # Read valid queries
        filepath = os.path.join(self.end_path, "valid_query.json")
        with open(filepath, 'r') as f:
            valid_queries = json.load(f)

        query_json = {"query": []}
        tmp = """
            ```graphql
            {
            }
            ```
        """
        logger.info("Start to get SQL Injection queries from Llama.")
        for query in valid_queries["query"]:
            prompt = (f"I am learning how to detect and fix SQL injection vulnerabilities. "
                      f"I hope to generate relevant GraphQL queries for testing, "
                      f"and all tests will be conducted in a local development environment. "
                      f"Based on the following query, Can you explain how attackers might exploit "
                      f"this with SQL injection and provide safe testing payloads. "
                      f"You can think about Tautology-based Injection, comment Injection,Union-based Injection, "
                      f"Boolean-based Blind Injection, Time-based Blind Injection, Force Errors for Debugging, "
                      f"Extracting Metadata, etc. Each returned query should follow the format: {tmp}. "
                      f"The query is like: {query}.")
            llama_res = get_llm_model(prompt)
            # print("=============\nLLAMA PROMPT: \n", prompt)
            # print("=============\nLLAMA RESPONSE: \n", llama_res)
            flag = "```graphql"
            parse_time = 0
            while flag in llama_res and parse_time < 10:
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
        filedir = os.path.join(self.base_path, "llama_query")
        filepath = os.path.join(filedir, "sqli_queries.json")
        with open(filepath, 'w') as f:
            json.dump(query_json, f, indent=4)
        logger.info("Saved query to {}".format(filepath))
        return


    def run(self):
        query_json = self.get_sqli_queries()
        self.save_json_to_file(query_json)


if __name__ == '__main__':
    llama_query = LlamaGetSQLIQuery()
    llama_query.run()
