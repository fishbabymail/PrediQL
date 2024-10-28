import requests
import json

from future.backports.urllib.parse import urldefrag


# Introspection query to fetch the schema
def get_official_schema(url):

    # GraphQL query to get the schema
    query = """
        {
          __schema {
            types {
              name
              fields {
                name
                type {
                  name
                }
              }
            }
          }
        }
    """

    # Set up the request headers
    headers = {
        'Content-Type': 'application/json'
    }

    # Send the POST request to the GitHub GraphQL API
    response = requests.post(
        url,
        headers=headers,
        json={'query': query}
    )

    # Check if the request was successful
    if response.status_code == 200:
        schema_data = response.json()
        print(json.dumps(schema_data, indent=2))
    else:
        raise Exception(f"Query failed with status code {response.status_code}")

    # Extract keywords from the schema
    keywords = set()
    for type_info in schema_data["data"]["__schema"]["types"]:
        # Add field names
        if type_info.get("fields"):
            for field in type_info["fields"]:
                if field["name"] and not field["name"].startswith("_"):
                    keywords.add(field["name"])

    # Convert the set to a sorted list and print it
    keyword_list = sorted(keywords)
    print(keyword_list)
    print(len(keyword_list))

    # Optional: Save the keywords to a text file
    with open("rick_keywords.txt", "w") as file:
        for word in keyword_list:
            file.write(word + "\n")

    print("Keywords saved")

    return keyword_list


if __name__ == "__main__":
    endpoint = "https://countries.trevorblades.com/"
    keyword_list = get_official_schema(endpoint)
