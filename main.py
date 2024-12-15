import argparse

import identify_valid_query
import refiner
from fuzzing_sqli import SqliFuzzing
from llama_get_valid_query import LlamaGetValidQuery
from llama_sqli_query import LlamaGetSQLIQuery


def main():
    parser = argparse.ArgumentParser(description="Please provide proper arguments")

    parser.add_argument("--url", type=str, help="GraphQL endpoint url")
    parser.add_argument("--sqli", type=str, help="true/false, generate sqli queries to fuzz endpoint")
    parser.add_argument("--dos", type=str, help="true/false, generate dos queries to fuzz endpoint")
    parser.add_argument("--batching", type=str, help="true/false, generate batching queries to fuzz endpoint")
    parser.add_argument("--refine", type=str, help="true/false to enable/disable refinement after fuzzing")

    args = parser.parse_args()

    url = args.url
    sqli = bool(args.sqli)
    dos = bool(args.dos)
    batching = bool(args.batching)
    refine = bool(args.refine)

    # Prompt LLaMA to generate valid queries
    llama_query = LlamaGetValidQuery(url)
    llama_query.run()

    # Identify valid queries
    identify_valid_query.run(url)

    # Generate malicious queries
    llama_query = LlamaGetSQLIQuery()
    llama_query.run(sqli=sqli, dos=dos, batching=batching)

    # Fuzzing
    sqlifuzz = SqliFuzzing(url)
    sqlifuzz.run(sqli=sqli, dos=dos, batching=batching)

    # Refine
    if refine:
        refiner.refine_engine()
        sqlifuzz.run(sqli=sqli, dos=dos, batching=batching, refine=True)



if __name__ == "__main__":
    main()
