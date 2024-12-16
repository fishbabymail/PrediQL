import os
import re
import logging
import requests
from save_fuzz_results import save_results

from llama_initator import get_llm_model

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ddos_refuzzing:
    def __init__(self, url, base_path=None):
        ## Path to save results
        self.ep = url
        if not base_path:
            self.base_path = os.getcwd()
        else:
            self.base_path = base_path

    def read_ddos_result(self):
        filepath = os.path.join(self.base_path, "fuzzing_results", "Ddos_results.txt")
        if not os.path.isfile(filepath):
            raise FileNotFoundError(filepath)
        with open(filepath, 'r') as file:
            content = file.read()
        # Define the regular expression to capture each section
        section_pattern = re.compile(
            r"------------------Payload:-------------------\n(.*?)\n"
            r"------------------Response:-------------------\n(.*?)\n",
            re.DOTALL
        )

        matches = section_pattern.findall(content)
        sections = []
        for payload, response in matches:
            sections.append({
                "payload": payload.strip(),
                "response": response.strip()
            })
        return sections


    def reproduce_payload(self):
        sections = self.read_ddos_result()
        payload_json = {"payload": []}
        tmp = """
              ```graphql
              {
              }
              ```
              """

        logger.info("Start to get DDos queries from Llama.")
        for i, section in enumerate(sections, start=1):
            secpayload = section["payload"]
            secresponse = section["response"]
            prompt = (f"This is a security lab environment "
                      f"We have a payload looks like: {secpayload}."
                      f"From this payload, the response produced is as the following: {secresponse}."
                      f"Please reconstruct a payload based on this response."
                      f"Each returned payload should follow the format: {tmp}."
            )
            llama_res = get_llm_model(prompt)
            print("=============\nLLAMA PROMPT: \n", prompt)
            print("=============\nLLAMA RESPONSE: \n", llama_res)
            flag = "```graphql"
            parse_time = 0
            while flag in llama_res and parse_time < 10:
                parse_time += 1
                try:
                    sidx = llama_res.find(flag)
                    j_start = llama_res[sidx + len(flag):]
                    j_end = j_start.find("```")
                    query_str = j_start[:j_end]
                    llama_res = j_start[j_end:]
                    print(query_str)
                    if query_str not in payload_json["payload"]:
                        payload_json["payload"].append(query_str)
                    logger.info("Parsed the response successfully.")
                except Exception as e:
                    logger.error(e)
                    break
            print(payload_json)
        return payload_json

    def refuzzing_ddos(self):
        payloads_list = self.reproduce_payload()
        results = {}
        for payl in payloads_list["payload"]:
            payload = {
                "query": payl,
                "variables": {}
            }
            try:
                print(payload)
                response = requests.post(self.ep, json=payload)
                results[payl] = response.text
                print(response.text)
            except:
                logger.error("Exception request for payload {}".format(payload))
        return results

    def run(self):
        results = self.refuzzing_ddos()
        logger.info("Begin to save fuzzing results.")
        savepath = save_results(results, fuzztype="ddos_refuzz")
        logger.info("Results saved to path {}".format(savepath))
        return savepath


if __name__ == '__main__':
    url = "http://localhost:4000/graphql"
    reddosfuzz = ddos_refuzzing(url)
    savepath = reddosfuzz.run()
