import os
import json
import logging
from llama_initator import get_llm_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LlamaAttackQueryGenerator:
    def __init__(self, base_path=None):
        """Initialize with base path for files"""
        self.base_path = base_path or os.getcwd()
        self.config_path = os.path.join(self.base_path, "attack_config")
        self.query_path = os.path.join(self.base_path, "llama_query")

        for path in [self.config_path, self.query_path]:
            if not os.path.exists(path):
                os.makedirs(path)

        # Load attack prompts
        with open(os.path.join(self.config_path, "attack_prompts.json"), 'r') as f:
            self.attack_prompts = json.load(f)

    def parse_llama_response(self, llama_res):
        """Extract GraphQL queries from Llama's response"""
        queries = []
        current_pos = 0

        while "```graphql" in llama_res[current_pos:]:
            # Find start and end of GraphQL block
            start_idx = llama_res.find("```graphql", current_pos)
            content_start = start_idx + len("```graphql")
            content_end = llama_res.find("```", content_start)

            if content_end == -1:
                break

            # Extract and clean query
            query = llama_res[content_start:content_end].strip()
            if query:
                queries.append(query)

            current_pos = content_end + 3 # Move position past the closing ```

        return queries

    def generate_queries(self, attack_type):
        """Generate queries for specified attack type"""
        # Load valid queries
        with open(os.path.join(self.query_path, "valid_query.json"), 'r') as f:
            valid_queries = json.load(f)

        results = {"query": []}
        seen_queries = set()

        # Get prompt template for attack type
        prompt_config = self.attack_prompts[attack_type]

        # Generate attacks for each valid query
        for query in valid_queries["query"]:
            prompt = prompt_config["prompt_template"].format(query=query)

            try:
                # Get response from Llama
                llama_res = get_llm_model(prompt)
                print(f"=============\nPrompt ({attack_type}): \n", prompt)
                print("=============\nResponse: \n", llama_res)

                # Parse and save unique queries
                for q in self.parse_llama_response(llama_res):
                    if q not in seen_queries:
                        results["query"].append(q)
                        seen_queries.add(q)

            except Exception as e:
                logger.error(f"Error processing query: {e}")
                continue

        # Save results
        output_file = f"{prompt_config['name']}.json"
        with open(os.path.join(self.query_path, output_file), 'w') as f:
            json.dump(results, f, indent=4)

        logger.info(f"Generated {len(results['query'])} queries for {attack_type}")

    def run(self, attack_types=None):
        """Run generator for specified attack types or all types"""
        if attack_types is None:
            attack_types = self.attack_prompts.keys()

        for attack_type in attack_types:
            try:
                logger.info(f"Generating {attack_type} queries...")
                self.generate_queries(attack_type)
            except Exception as e:
                logger.error(f"Error generating {attack_type} queries: {e}")


if __name__ == '__main__':
    try:
        generator = LlamaAttackQueryGenerator()
        # Generate all attack types:
        generator.run()
        # Or specific types:
        # generator.run(["sql_injection", "batch_attack"])
    except Exception as e:
        logger.error(f"Error: {e}")