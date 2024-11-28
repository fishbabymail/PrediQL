import os


def save_results(results, fuzztype, base_path = None):
    if fuzztype == "valid_queries":
        flag = "Valid Query"
    else:
        flag = "Payload"
    # Make results directory
    if not base_path:
        base_path = os.getcwd()
    filedir = os.path.join(base_path, "fuzzing_results")
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    filename = fuzztype + "_" + "results" + ".txt"
    filepath = os.path.join(filedir, filename)
    if not os.path.isfile(filepath):
        with open(filepath, 'w') as f:
            pass
    for query, resp in results.items():
        # query = ast.literal_eval(query)
        with open(filepath, 'a') as f:
            f.write("------------------" + flag + ":-------------------\n")
            f.write(f"{query}\n")
            f.write("------------------Response:-------------------\n")
            f.write(f"{resp}\n")
    return filepath