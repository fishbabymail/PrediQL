import os
import requests
import json
import logging
from save_fuzz_results import save_results

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SqliFuzzing():
    def __init__(self, url):
        self.ep = url

    def read_payload_query(self, fuzz_type, refine):
        if refine:
            filename = fuzz_type + "_improved_queries.json"
        else:
            filename = fuzz_type + "_queries.json"
        filepath = os.path.join(os.getcwd(), "llama_query", filename)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(filepath)
        with open(filepath, 'r') as f:
            queries = json.load(f)
        query_list = queries["query"]
        return query_list


    def fuzzing_endpoint(self, query_list):
        results = {}
        for query in query_list:
            payload = {
                "query": query,
                "variables": {}
            }

            try:
                response = requests.post(self.ep, json=payload)
                # print(response.text)
                results[query] = response.text
                # print(response.text)
            except:
                logger.error("Exception request for query: {}".format(query))
        return results

    def run(self, sqli = False, dos = False, batching = False, refine=False):
        if sqli:
            query_list = self.read_payload_query("sqli", refine)
            results = self.fuzzing_endpoint(query_list)
            logger.info("Begin to save sql injection fuzzing results.")
            savepath = save_results(results, fuzztype="sqli", refine=refine)
            logger.info("Results saved to path {}".format(savepath))
        if dos:
            query_list = self.read_payload_query("dos", refine)
            results = self.fuzzing_endpoint(query_list)
            logger.info("Begin to save DOS fuzzing results.")
            savepath = save_results(results, fuzztype="dos_improved", refine=refine)
            logger.info("Results saved to path {}".format(savepath))

        if batching:
            query_list = self.read_payload_query("batching", refine)
            results = self.fuzzing_endpoint(query_list)
            logger.info("Begin to save Batching fuzzing results.")
            savepath = save_results(results, fuzztype="batching_improved", refine=refine)
            logger.info("Results saved to path {}".format(savepath))


if __name__ == '__main__':
    url = "http://localhost:4000/graphql"
    sqlifuzz = SqliFuzzing(url)
    sqlifuzz.run(dos=True)




