import json
import logging
from typing import Dict, List
from datetime import datetime
import os
import yaml
from llama_initator import get_llm_model


class QueryImprover:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_schema(self, schema_file: str) -> Dict:
        """Load GraphQL schema from compiled queries YAML"""
        try:
            with open(schema_file, 'r') as f:
                schema_data = yaml.safe_load(f)
            return schema_data
        except Exception as e:
            self.logger.error(f"Error loading schema: {str(e)}")
            raise

    def load_results(self, file_path: str) -> List[Dict]:
        """Load test results file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get("results", [])
        except Exception as e:
            self.logger.error(f"Error loading results file: {str(e)}")
            raise

    def analyze_query_results(self, results: List[Dict], schema: Dict = None, attack_type: str = None) -> str:
        """
        Create an analytical prompt that encourages Llama to think through errors and generate improved queries
        """
        if attack_type:
            analysis_text = f"""As a GraphQL security expert,analyze these query results and their errors to generate a massive set of {attack_type} attack queries.
I need you to generate 100-200 different attack queries (or even more) to thoroughly test the system's security.

To generate such a large number of unique queries, systematically:
1. Take each field in the schema and create multiple attack variations
2. Combine different attack techniques within the {attack_type} category
3. Generate queries of increasing complexity levels
4. Create mutations of successful patterns
5. Explore all possible input combinations

For EACH field in the schema:
- Create multiple attack variations
- Try different argument combinations
- Nest fields in different ways
- Combine with other relevant fields
- Test boundary conditions
- Mix with known attack patterns

"""
        else:
            analysis_text = """As a GraphQL expert, analyze these query results and their errors carefully.
I need you to generate 100-200 different improved queries (or even more) to thoroughly test the system.

To generate such a large number of unique queries, systematically:
1. Take each field in the schema and create multiple variations
2. Try all possible field combinations
3. Generate queries of increasing complexity
4. Create mutations of successful patterns
5. Explore all possible input combinations

For EACH field in the schema:
- Create multiple query variations
- Try different argument combinations
- Nest fields in different ways
- Combine with other relevant fields
- Test boundary conditions
"""

        # Add schema information if available
        if schema:
            analysis_text += "Schema Information:\n"
            analysis_text += yaml.dump(schema, default_flow_style=False)
            analysis_text += "\n---\n\n"

        # Group queries by error type for pattern recognition
        error_patterns = {}

        for result in results:
            query = result.get("query", "")
            response = result.get("response", {})
            status_code = response.get("status_code")

            analysis_text += f"Query:\n{query}\n"
            analysis_text += f"Status: {status_code}\n"

            if "errors" in response.get("response", {}):
                errors = response["response"]["errors"]
                for error in errors:
                    error_msg = error.get('message', '')
                    analysis_text += f"Error: {error_msg}\n"

                    if error_msg not in error_patterns:
                        error_patterns[error_msg] = []
                    error_patterns[error_msg].append(query)

            analysis_text += "\n---\n\n"

        # Add error pattern analysis
        if error_patterns:
            analysis_text += "\nError Pattern Analysis:\n"
            for error_msg, queries in error_patterns.items():
                analysis_text += f"\nPattern: {error_msg}\n"
                analysis_text += f"Occurred in {len(queries)} queries\n"
                analysis_text += "Example query:\n"
                analysis_text += f"{queries[0]}\n"

        if attack_type:
            analysis_text += f"""
Now generate a massive set of {attack_type} attack queries (at least 100 unique queries) without any explanation and comments.
Systematic approach:
1. Start with simple attacks targeting single fields
2. Progress to more complex combinations
3. Include field variations:
   - Different argument values
   - Changed field orders
   - Nested relationships
   - Multiple aliases
4. Generate payload variations:
   - Different input values
   - Changed string formats
   - Numeric boundaries
   - Special characters
5. Create structural variations:
   - Query depth changes
   - Field combination changes
   - Argument manipulation
   - Fragment usage
6. Mix techniques:
   - Combine successful patterns
   - Merge different approaches
   - Layer multiple attack vectors
"""
        else:
            analysis_text += """
Now generate a massive set of improved queries (at least 100 unique queries).
Systematic approach:
1. Start with simple field selections
2. Progress to more complex combinations
3. Include field variations:
   - Different argument values
   - Changed field orders
   - Nested relationships
   - Multiple aliases
4. Generate input variations:
   - Different valid values
   - Edge cases
   - Boundary values
   - Special cases
5. Create structural variations:
   - Query depth changes
   - Field combination changes
   - Argument manipulation
   - Fragment usage
"""

        analysis_text += """
Return your queries in this format:
<QUERIES>
query {
  # First query
}
===
query {
  # Second query
}
</QUERIES>

NOTE: You must wrap your response in <QUERIES> tags and separate queries with === exactly as shown above.

IMPORTANT: 
- Generate AT LEAST 100 different queries
- Each query must be unique
- Maintain valid GraphQL syntax
- Use systematic variations to ensure diversity
- Include both simple and complex queries
- DO NOT STOP until you have generated at least 100 unique queries
- You must wrap your response in <QUERIES> tags and separate queries with === exactly """

        return analysis_text

    def parse_llama_response(self, response: str) -> List[str]:
        """Parse Llama's response to extract queries"""
        try:
            # First try exact format with tags
            start_tag = "<QUERIES>"
            end_tag = "</QUERIES>"
            start_idx = response.find(start_tag)
            end_idx = response.find(end_tag)

            if start_idx != -1 and end_idx != -1:
                queries_content = response[start_idx + len(start_tag):end_idx]
            else:
                # Fallback: try to parse the whole response
                queries_content = response

            # Try different separators
            separators = ["===", "---", "\n---\n", "\nquery"]
            queries = []

            for separator in separators:
                if separator in queries_content:
                    if separator == "\nquery":
                        # Handle case where queries are just separated by newlines
                        raw_queries = [f"query{q}" for q in queries_content.split("\nquery") if q.strip()]
                    else:
                        raw_queries = queries_content.split(separator)

                    # Process found queries
                    for query in raw_queries:
                        query = query.strip()
                        if query and query.startswith('query'):
                            queries.append(query)

                    if queries:
                        break

            if not queries:
                self.logger.error("No valid queries found in response")
                self.logger.error(f"Raw response:\n{response}")
                raise ValueError("No valid queries found in response")

            self.logger.info(f"Successfully extracted {len(queries)} queries")
            return queries

        except Exception as e:
            self.logger.error(f"Error processing Llama response: {str(e)}")
            self.logger.error(f"Raw response:\n{response}")
            raise

    def save_queries(self, queries: List[str], output_dir: str, attack_type: str = None):
        """Save queries to a JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if attack_type:
            filename = f"{attack_type}_queries_{timestamp}.json"
        else:
            filename = f"queries_{timestamp}.json"

        output_file = os.path.join(output_dir, filename)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        data = {"query": queries}

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        self.logger.info(f"Queries saved to {output_file}")
        return output_file

    def improve_queries(self, results_file: str, schema_file: str, output_dir: str, attack_type: str = None):
        """Main method to process results and generate improved queries"""
        try:
            # Load test results and schema
            results = self.load_results(results_file)
            schema = self.load_schema(schema_file) if schema_file else None

            # Generate analytical prompt
            analysis_prompt = self.analyze_query_results(results, schema, attack_type)

            # Get improved queries from Llama
            self.logger.info(f"Generating {'attack' if attack_type else 'improved'} queries...")
            llama_response = get_llm_model(analysis_prompt)
            self.logger.debug(f"Raw Llama response:\n{llama_response}")

            # Parse and save the queries
            improved_queries = self.parse_llama_response(llama_response)
            output_file = self.save_queries(improved_queries, output_dir, attack_type)

            return output_file

        except Exception as e:
            self.logger.error(f"Error in query improvement process: {str(e)}")
            raise


def main():
    improver = QueryImprover()

    improver.improve_queries(
        results_file="test_results/results_20241128_161326.json",
        schema_file="graphqler-output/compiled/compiled_queries.yml",
        output_dir="llama_query",
        attack_type="batching attack"  # Can be any attack type like "sqli", "nosql", "auth_bypass", etc.
    )


if __name__ == "__main__":
    main()