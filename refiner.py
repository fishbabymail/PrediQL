import os
import re
from llama_initator import get_llm_model
import json


def refine_engine():
    fuzzing_type = ["Sqli, dos, batching"]
    fuzzing_mapping = {
        "Sqli": "SQL Injection",
        "dos": "DoS attack",
        "batching": "Batching attack"
    }
    for t in fuzzing_type:
        filename = t + "_results.txt"
        filepath = os.path.join(os.getcwd(), "fuzzing_results", filename)
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r") as f:
            contents = f.read()
        payload_resp_pair = {}
        pair_pattern = (r"------------------Payload:-------------------\n(.*?)\n-"
                        r"-----------------Response:-------------------\n(.*?)"
                        r"(?=------------------Payload:-------------------|$)")

        pairs = re.findall(pair_pattern, contents, re.DOTALL)
        for payload, response in pairs:
            payload_clean = payload.strip()
            response_clean = response.strip()
            if payload_clean not in payload_resp_pair:
                payload_resp_pair[payload_clean] = response_clean

        tmp = """
            ```graphql
            {
            }
            ```
        """
        queries = []


        def parse_llama_response(resp):
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
                except:
                    continue
            return query

        def save_json_to_file(query_json, query_type):
            filedir = os.path.join(os.getcwd(), "llama_query")
            filename = query_type + "_improved_queries.json"
            filepath = os.path.join(filedir, filename)
            with open(filepath, 'w') as f:
                json.dump(query_json, f, indent=4)
            return

        ack_type = fuzzing_mapping[t]
        for payload, response in payload_resp_pair.items():
            if "errors" in response:
                prompt = (f"I am learning how to detect and fix {ack_type} vulnerabilities. "
                          f"I hope to generate relevant GraphQL {ack_type} queries for testing, "
                          f"and all tests will be conducted in a local development environment. "
                          f"Based on the following query and error information, please correct "
                          f"the query and return it. Please notice that the generated payloads "
                          f"should be intact GraphQL query, do not use any placeholders or suspension points."
                          f"Each returned query should follow the format: {tmp}. "
                          f"The query: {payload}. The corresponding response is: {response}")
                llama_res = get_llm_model(prompt)
                # print("=============\nLLAMA PROMPT: \n", prompt)
                print("=============\nLLAMA RESPONSE: \n", llama_res)
                new_queries = parse_llama_response(resp=llama_res)
                queries.extend(new_queries)

        query_json = {
            "query": queries
        }

        save_json_to_file(query_json, t)




if __name__ == "__main__":
    refine_engine()


