from graphqler.core import compile_and_fuzz


def get_graphqler_result(path, url, config):
    results = compile_and_fuzz(path, url, config)

    return results


def get_object_buckets(results):
    object_bucket = results["objects_bucket"]
    print("objects_bucket:\n", object_bucket)


# Get Stats info
def get_stats_info(results):
    stats_obj = results["stats"]
    stats_total_queries = stats_obj.number_of_queries
    stats_total_mutations = stats_obj.number_of_mutations
    stats_total_objects = stats_obj.number_of_objects
    stats_vulnerabilities = stats_obj.vulnerabilities
    # print("total queries = {}, total_mutations = {}, total_objects = {}, "
    #       "total_vulnerabilities = {}".format(stats_total_queries,
    #                                           stats_total_mutations,
    #                                           stats_total_objects,
    #                                           stats_vulnerabilities))


# Get compiled results
def get_compiled_results(results):
    api_obj = results["api"]
    compiled_queries = api_obj.queries
    compiled_objects = api_obj.objects
    compiled_mutations = api_obj.mutations
    # print("=========\ncompiled queries:\n{}\n===========\ncompiled objects:"
    #       "\n{}\n=========\ncompiled mutations:\n{}\n"
    #       "".format(compiled_queries, compiled_objects, compiled_mutations))


# Get extracted results
def get_extracted_results(results):
    api_obj = results["api"]
    extracted_input_objects = api_obj.input_objects
    extracted_enums = api_obj.enums
    extracted_unions = api_obj.unions
    extracted_interfaces = api_obj.interfaces
    # print("========\ninput objects : \n{}\n=========\nenums:\n{}\n========="
    #       "\nunions:\n{}\n=========\ninterfaces:\n{}\n========="
    #       "".format(extracted_input_objects, extracted_enums, extracted_unions, extracted_interfaces))


def get_endpoint_results(results):
    stats_results = results["results"]
    # print("========\nstats_results:\n", stats_results)


def main(path, url):
    config = {
        "DEBUG": True
    }
    results = get_graphqler_result(path, url, config)
    get_object_buckets(results)
    get_stats_info(results)
    get_compiled_results(results)
    get_extracted_results(results)
    get_endpoint_results(results)

if __name__ == '__main__':
    url = "https://rickandmortyapi.com/graphql"
    path = "./graphqler_results/"
    main(path, url)