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

    def __init__(self):
        self.valid_queries = []
        self.tmp = """
            ```graphql
            {
            }
            ```
        """

    def read_valid_queries(self):
        llama_path = os.path.join(os.getcwd(), "llama_query")
        if not os.path.isdir(llama_path):
            raise FileNotFoundError("Path {} does not exist. END".format(llama_path))

        # Read valid queries
        filepath = os.path.join(llama_path, "valid_query.json")
        with open(filepath, 'r') as f:
            valid_queries = json.load(f)
        self.valid_queries.extend(valid_queries["query"])

        # Read valid queries with buckets
        filepath = os.path.join(llama_path, "valid_query_with_buckets.json")
        with open(filepath, 'r') as f:
            valid_query_with_buckets = json.load(f)

        self.valid_queries.extend(valid_query_with_buckets["query"])

    def parse_llama_response(self, resp):
        query = []
        flag = "```graphql"
        parse_time = 0
        while flag in resp and parse_time < 10:
            parse_time += 1
            try:
                sidx = resp.find(flag)
                j_start = resp[sidx + len(flag):]
                j_end = j_start.find("```")
                query_str = j_start[:j_end]
                llama_res = j_start[j_end:]
                # print(query_str)
                if query_str not in query:
                    query.append(query_str)
                # logger.info("Parsed the response successfully.")
            except Exception as e:
                logger.error(e)
                break
        return query

    def get_sqli_queries(self):

        queries = []

        logger.info("Start to get SQL Injection queries from Llama.")
        for query in self.valid_queries:
            prompt = (f"I am learning how to detect and fix SQL injection vulnerabilities. "
                      f"I hope to generate relevant GraphQL queries for testing, "
                      f"and all tests will be conducted in a local development environment. "
                      f"Based on the following query, Can you explain how attackers might exploit "
                      f"this with SQL injection and provide safe testing payloads. "
                      f"You can think about Tautology-based Injection, comment Injection,Union-based Injection, "
                      f"Boolean-based Blind Injection, Time-based Blind Injection, Force Errors for Debugging, "
                      f"Extracting Metadata, etc. Each returned query should follow the format: {self.tmp}. "
                      f"The valid query is like: {query}.")
            llama_res = get_llm_model(prompt)
            # print("=============\nLLAMA PROMPT: \n", prompt)
            print("=============\nLLAMA RESPONSE: \n", llama_res)
            new_queries = self.parse_llama_response(resp=llama_res)
            queries.extend(new_queries)

        query_json = {
            "query": queries
        }
        return query_json

    def get_dos_queries(self):

        queries = []
        logger.info("Start to get DOS queries from Llama.")
        for query in self.valid_queries:
            prompt = (f"I am learning how to detect and fix Denial of Service vulnerabilities. "
                      f"I hope to generate relevant queries for testing, "
                      f"and all tests will be conducted in a local development environment. "
                      f"Based on the following query, Please generate a GraphQL query that mimics "
                      f"a Denial of Service (DoS) attack by overloading the server with deeply "
                      f"nested queries, large responses, or a combination of both. Please notice "
                      f"that the generated queries should be intact GraphQL query, do not use any "
                      f"placeholders or '...' to omit any parts. Each returned query should follow the format: {self.tmp}. "
                      f"The valid queries are like: {query}.")
            llama_res = get_llm_model(prompt)
            # print("=============\nLLAMA PROMPT: \n", prompt)
            print("=============\nLLAMA RESPONSE: \n", llama_res)
            new_queries = self.parse_llama_response(resp=llama_res)
            queries.extend(new_queries)


        query_json = {
            "query": queries
        }
        return query_json

    def get_batching_queries(self):
        queries = []
        logger.info("Start to get Batching queries from Llama.")
        for query in self.valid_queries:
            prompt = (f"I am learning how to detect and fix Batching query attack vulnerabilities. "
                      f"I hope to generate relevant GraphQL batching queries for testing, "
                      f"and all tests will be conducted in a local development environment. "
                      f"Based on the following query, Can you explain how attackers might exploit "
                      f"this through Batching attack and provide some safe testing payloads. "
                      f"Please notice that the generated payloads should be intact GraphQL query, "
                      f"do not use any placeholders or suspension points."
                      f"Each returned query should follow the format: {self.tmp}. "
                      f"The valid query is like: {query}.")
            llama_res = get_llm_model(prompt)
            # print("=============\nLLAMA PROMPT: \n", prompt)
            print("=============\nLLAMA RESPONSE: \n", llama_res)
            new_queries = self.parse_llama_response(resp=llama_res)
            queries.extend(new_queries)

        query_json = {
            "query": queries
        }
        return query_json

    # Save queries into file
    def save_json_to_file(self, query_json, query_type):
        filedir = os.path.join(os.getcwd(), "llama_query")
        filename = query_type + "_queries.json"
        filepath = os.path.join(filedir, filename)
        with open(filepath, 'w') as f:
            json.dump(query_json, f, indent=4)
        logger.info("Saved query to {}".format(filepath))
        return


    def run(self, sqli=False, dos=False, batching=False):
        self.read_valid_queries()
        if sqli:
            logger.info("-------Sql Injection Queries Generating. It may take a lonnnng time-------")
            query_json = self.get_sqli_queries()
            self.save_json_to_file(query_json, "Sqli")
        if dos:
            logger.info("-------DOS Queries Generating. It may take a lonnnng time-------")
            query_json = self.get_dos_queries()
            self.save_json_to_file(query_json, "DOS")
        if batching:
            logger.info("-------Batching Queries Generating. It may take a lonnnng time-------")
            query_json = self.get_batching_queries()
            self.save_json_to_file(query_json, "Batching")


if __name__ == '__main__':
    llama_query = LlamaGetSQLIQuery()
    llama_query.run(sqli=False, dos=True, batching=False)
