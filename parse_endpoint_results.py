import os
import re
import json
import logging

from llama_initator import get_llm_model


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Find graphqler-output/endpoint_results/xx/failure/200 files
class ParseFailureResults():

    def __init__(self, base_path=None):
        if not base_path:
            base_path = os.getcwd()
        self.end_path = os.path.join(base_path, "graphqler-output", "endpoint_results")
        if not os.path.isdir(self.end_path):
            raise FileNotFoundError("Path {} does not exist. END".format(self.end_path))

    # Get paths of failure files
    def get_failure_files(self):
        failure_files = []
        for root, dirs, files in os.walk(self.end_path):
            if "200" in files:
                # print("200 file path = ", os.path.join(root, '200'))
                failure_files.append(os.path.join(root, '200'))
        return failure_files

    # Parse the 200 files results to {payload: response} format
    def parse_result_to_dict(self):
        payload_resp_pair = {}
        failure_files = self.get_failure_files()
        # print(failure_files)
        for filepath in failure_files:
            if len(payload_resp_pair) > 50:
                break
            try:
                with open(filepath, "r") as f:
                    contents = f.read()
            except Exception as e:
                print("Error reading file {}: {}".format(filepath, e))
                continue

            pair_pattern = (r"------------------Payload:-------------------\n(.*?)\n-"
                            r"-----------------Response:-------------------\n(.*?)"
                            r"(?=------------------Payload:-------------------|$)")

            pairs = re.findall(pair_pattern, contents, re.DOTALL)
            for payload, response in pairs:
                payload_clean = payload.strip()
                response_clean = response.strip()
                if payload_clean not in payload_resp_pair:
                    payload_resp_pair[payload_clean] = response_clean
            # For test, only read 50 records
                if len(payload_resp_pair) > 50:
                    break

        return payload_resp_pair


if __name__ == "__main__":
    pfr = ParseFailureResults()
    payload_resp_pair = pfr.parse_result_to_dict()
    for payload, response in payload_resp_pair.items():
        print("payload: {}\n".format(payload))
        print("response: {}\n".format(response))
