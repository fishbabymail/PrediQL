import os
import json
import logging


from parse_endpoint_results import ParseEndpointResults
from get_results_from_graphqler import GetGraphqlerResults

from llama_initator import get_llm_model


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LlamaGetValidQuery:
    def __init__(self, url):
        self.qler_handler = GetGraphqlerResults(url)

    def get_compiled_queries(self):
        compiled_results = self.qler_handler.get_compiled_results()
        compiled_queries = compiled_results["queries"]
        compiled_mutations = compiled_results["mutations"]
        return compiled_queries, compiled_mutations


    def get_object_buckets(self):
        object_results = self.qler_handler.get_object_buckets()
        objects_dict = object_results["objects"]
        scalars_dict = object_results["scalars"]
        return objects_dict, scalars_dict


    def get_parameters(self):
        parameters_results = self.qler_handler.get_extracted_results()
        query_parameters = parameters_results["query"]
        mutation_parameters = parameters_results["mutation"]
        return query_parameters, mutation_parameters

    def form_object_promp(self):
        object_dict, scalars_dict = self.get_object_buckets()
        object_promp_text = ""
        for object_name, object_values in object_dict.items():
            object_promp_text += f"The object '{object_name}' has valid values: {object_values}. "
        return object_promp_text


    def get_valid_queries(self):
        # Get failure payloads and responses pairs
        per = ParseEndpointResults()
        payload_resp_pair = per.parse_result_to_dict()
        # print(payload_resp_pair)

        # Get compiled query schema
        compiled_queries, compiled_mutations = self.get_compiled_queries()
        object_promp_text = self.form_object_promp()
        query_parameters, mutation_parameters = self.get_parameters()

        query_json = {"query": []}
        tmp = """
            ```graphql
            {
            }
            ```
        """
        logger.info("Start to get valid queries from Llama.")
        for payload, response in payload_resp_pair.items():
            # # Control running time
            # if len(query_json["query"]) > 50:
            #     break
            # prompt = (f"Based on the following graphql query, the corresponding response, "
            #           f"and graphql schema information, please try to fix this query and "
            #           f"return me different valid queries, and separate each of the returned query "
            #           f"as: {tmp}, please use real values for fields instead of placeholders. The query is :{payload}, "
            #           f"the error response for this query is :{response}, the graphql schema "
            #           f"is: {compiled_queries}.")
            prompt = (f"There is a Graphql Endpoint, the schema for query is: {compiled_queries}, "
                      f"the schema for mutation is: {compiled_mutations}. In addition, ")
            prompt += object_promp_text

            prompt += (f"Based on the above information and the following query and response, please generate "
                       f"some valid queries, and separate each of the returned query as: {tmp}, please use "
                       f"real values for fields instead of placeholders. The query is: {payload}, the response "
                       f"for this query is: {response}.")

            llama_res = get_llm_model(prompt)
            # print("=============\nLLAMA PROMPT: \n", prompt)
            print("=============\nLLAMA RESPONSE: \n", llama_res)
            flag = "```graphql"
            parse_time = 0
            while flag in llama_res and parse_time < 10:
                # # Control running time
                # if len(query_json["query"]) > 50:
                #     break
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
        base_path = os.getcwd()
        filedir = os.path.join(base_path, "llama_query")
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        filepath = os.path.join(filedir, "llama_queries_with_buckets.json")
        with open(filepath, 'w') as f:
            json.dump(query_json, f, indent=4)
        logger.info("Saved query to {}".format(filepath))
        return True


    def run(self):
        query_json = self.get_valid_queries()
        self.save_json_to_file(query_json)



if __name__ == '__main__':
    url = "http://localhost:4000/graphql"
    llama_query = LlamaGetValidQuery(url)
    llama_query.run()
