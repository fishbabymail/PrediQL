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


class DDOSFuzzing():
    def __init__(self, url, base_path=None):
        ## Path to save results
        self.ep = url
        if not base_path:
            self.base_path = os.getcwd()
        else:
            self.base_path = base_path

    def read_DDOS_query(self):
        filepath = os.path.join(self.base_path, "llama_query", "ddos_queries.json")
        if not os.path.isfile(filepath):
            raise FileNotFoundError(filepath)
        with open(filepath, 'r') as f:
            queries = json.load(f)
        query_list = queries["query"]
        return query_list

    def fuzzing_endpoint(self):
        query_list = self.read_DDOS_query()
        results = {}
        for query in query_list:
            payload = {
                "query": query,
                "variables": {}
            }
            try:
                response = requests.post(self.ep, json=payload)
                results[query] = response.text
                print(response.text)
            except:
                logger.error("Exception request for query: {}".format(query))
        return results

    def run(self):
        results = self.fuzzing_endpoint()
        logger.info("Begin to save fuzzing results.")
        savepath = save_results(results, fuzztype="Ddos")
        logger.info("Results saved to path {}".format(savepath))
        return savepath


if __name__ == '__main__':
    url = "https://rickandmortyapi.com/graphql"
    DDOSfuzz = DDOSFuzzing(url)
    savepath = DDOSfuzz.run()



