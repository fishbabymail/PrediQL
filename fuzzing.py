import json
import time
import requests
import logging
from typing import Dict, List
from datetime import datetime
import os

class GraphQLFuzzer:
    def __init__(self, endpoint_url: str, rate_limit: float = 1.0, headers: Dict = None):
        """
        Args:
            endpoint_url (str): The GraphQL endpoint
            rate_limit (float): Minimum time between requests in seconds
            headers (Dict): Optional headers for GraphQL requests
        """
        self.endpoint_url = endpoint_url
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.headers = headers or {
            'Content-Type': 'application/json',
        }
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_queries(self, file_path: str) -> List:
        """Load GraphQL queries from JSON file generated by Llama"""
        try:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Query file not found: {file_path}")

            with open(file_path, 'r') as f:
                data = json.load(f)
                queries = data.get("query", [])
            self.logger.info(f"Loaded queries from {file_path}")
            return queries
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading queries: {str(e)}")
            raise

    def send_graphql_request(self, query: List) -> Dict:
        """
        Send a single GraphQL request with rate limiting
        We never send requests faster than our rate limit
        We only wait as long as necessary to meet the rate limit
        """
        # Implement rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last_request)

        try:
            payload = {
                "query": query,
                "variables": {}
            }

            self.logger.info(f"Sending GraphQL query: {query}")
            self.logger.debug(f"Full query: {json.dumps(payload)[:200]}...")

            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=self.headers
            )
            self.last_request_time = time.time()

            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {
                    "error": "Invalid JSON response",
                    "raw_response": response.text
                }
            return {
                "status_code": response.status_code,
                "response": response_data
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            return {
                "error": str(e)
            }

    def run_testing(self, queries: List) -> List[Dict]:
        results = []
        total_queries = len(queries)

        self.logger.info(f"Starting to test {total_queries} queries")

        for i, query in enumerate(queries, 1):
            self.logger.info(f"Processing query {i}/{total_queries}")
            result = self.send_graphql_request(query)
            results.append({
                "query_id": i,
                "query": query,
                "response": result,
                "timestamp": datetime.now().isoformat()
            })
        return results
    #TODO: run result

    def save_results(self, results: List[Dict], output_file: str):
        """Save testing results to a JSON file"""
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, 'w') as f:
            json.dump({"results": results}, f, indent=2)
        self.logger.info(f"Results saved to {output_file}")

def main():
    fuzzer = GraphQLFuzzer(
        endpoint_url="https://rickandmortyapi.com/graphql",
        rate_limit=1.0,
        headers={
            'Content-Type': 'application/json',
        }
    )
    # Load and execute queries
    queries = fuzzer.load_queries("llama_query/rick_query_ep.json")
    print(queries)
    results = fuzzer.run_testing(queries)
    fuzzer.save_results(
        results,
        f"test_results/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )


if __name__ == "__main__":
    main()