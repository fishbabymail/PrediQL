import os


def save_results(results, fuzztype, base_path = None, refine=False):
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
    if refine:
        filename = fuzztype + "_improved_results.txt"
    else:
        filename = fuzztype + "_results.txt"
    filepath = os.path.join(filedir, filename)
    with open(filepath, 'w') as f:
        f.write("-------------Results-------------\n")
    for query, resp in results.items():
        # query = ast.literal_eval(query)
        with open(filepath, 'a') as f:
            f.write("------------------" + flag + ":-------------------\n")
            f.write(f"{query}\n")
            f.write("------------------Response:-------------------\n")
            f.write(f"{resp}\n")
    return filepath