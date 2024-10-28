import copy

import requests
import json



def llm_model(ep):
    print("endpoint url = ", ep)
    url = "http://localhost:11434/api/chat"
    prompt = (f"Please generate 100 single words without about schema of {ep} as a python list. "
              f"The returned list must follow the format like this: ['xx', 'xx', 'xx', ...] "
              f"Return only full word list for me, no more extra explanation.")
    print(prompt)
    data = {
        "model": "llama3",
        "messages": [
            {
                "role": "user",
                "content": prompt

            }
        ],
        "stream": False,
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()["message"]["content"]
    return data



def wordlist_gen(ep, file_save_path, filename):
    exist_words = []
    word_num = 0
    round = 0

    while word_num < 1000 or round < 10:
        round += 1
        try:
            print("word_num = ", word_num)
            data = llm_model(ep)
            print("response data:\n", data)
            idx_l = data.index("[")
            idx_r = data.index("]")
            lpart = data[idx_l : idx_r+1]
            round_words = eval(lpart)
            fname = file_save_path + "/" + filename
            for w in round_words:
                if w not in exist_words:
                    exist_words.append(w)
                    word_num += 1
                    with open(fname, "a") as file:
                        file.write(w + "\n")
        except:
            continue


    return exist_words



if __name__ == "__main__":
    endpoint = "https://countries.trevorblades.com/"
    llama_words = wordlist_gen(endpoint, "wordlist", "llama_wordlist.txt")