import os

from graphqler.core import compile_and_fuzz


class GetGraphqlerResults():
    def __init__(self, url):
        self.url = url
        self.config = {
            "DEBUG": True
        }
        path = os.getcwd()
        filepath = os.path.join(path, "graphqler_results")
        self.results = compile_and_fuzz(filepath, url, self.config)


    def get_object_buckets(self):
        object_bucket = self.results["objects_bucket"]
        objects_dict = object_bucket.objects
        scalars_dict = object_bucket.scalars
        object_results = {
            "objects": objects_dict,
            "scalars": scalars_dict
        }
        return object_results


    # Get Stats info
    def get_stats_info(self):
        stats_obj = self.results["stats"]
        stats_total_queries = stats_obj.number_of_queries
        stats_total_mutations = stats_obj.number_of_mutations
        stats_total_objects = stats_obj.number_of_objects
        stats_vulnerabilities = stats_obj.vulnerabilities

    # Get compiled results
    def get_compiled_results(self):
        api_obj = self.results["api"]
        compiled_queries = api_obj.queries
        compiled_objects = api_obj.objects
        compiled_mutations = api_obj.mutations
        compiled_results = {
            "queries": compiled_queries,
            "mutations": compiled_mutations,
        }
        return compiled_results


    # Get extracted results
    def get_extracted_results(self):
        api_obj = self.results["api"]
        query_parameters = api_obj.input_objects
        mutation_parameters = api_obj.mutations
        parameters_results = {
            "query": query_parameters,
            "mutation": mutation_parameters
        }
        return parameters_results



    def get_endpoint_results(self):
        stats_results = self.results["results"]


if __name__ == '__main__':
    url = "http://localhost:4000/graphql"
    get_graphqler = GetGraphqlerResults(url)
    compiled_results = get_graphqler.get_compiled_results()
    parameters_results = get_graphqler.get_extracted_results()