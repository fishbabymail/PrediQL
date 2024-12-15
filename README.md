# PrediQL

## Acknowledgements

### This project leverages the following tool：
#### - [GraphQLer](https://github.com/omar2535/GraphQLer): The only dependency-aware GraphQL API testing tool!

We thank the developers of this tool for their contributions to the open-source community.

--------------------------
### Usage

* prerequisite: LLaMa 3 is running    
* Usage:  `python main.py --url http://localhost:4000/graphql --sqli True --dos True --batching True --refine True`
* Get help info: `python main.py -h`

--------------------------
### Functions Explanation


#### `llama_initiator.py`
* description: initiate llama object, using llama 3.1


#### `get_results_from_graphqler.py`
* get objects_bucket, compiled queries, etc from Graphqler.


#### `parse_endpoint_results.py`
* Read results in `graphqler-output/endpoint_results`
* Save queries and responses as dict

#### `llama_get_valid_query.py`
* Read results from `parse_endpoint_results.py`
* Prompt Llama to generate some possible valid queries based on the queries and responses in `graphqler-output/endpoint_results`
* Temporarily save results in `llama_query/llama_queries.json`

#### `identify_valid_query.py`
* read `llama_query/llama_queries.json`
* send request to the endpoint to identify the valid queries
* Temporarily save results to `llama_query/valid_query.json`

#### `llama_sqli_query.py`
* read `llama_query/valid_query.json`
* prompt llama with these queries to generate some possible sql injection queries
* Temporarily save results to `llama_query/sqli_queries.json`

#### `fuzzing_sqli.py`
* read `llama_query/sqli_queries.json`
* fuzzing the endpoint with these sqli queries
* Results saved to `fuzzing_results/Sqli_results.txt`

#### `fuzzing.py`
* description: send queries to endpoint, save responses
* output: save results to `test_results/results_<timestamp>`

