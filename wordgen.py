import copy

import requests
import json

from numba.typed.listobject import new_list


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

def word_compare(list1, list2):
    llama_wordlist = []
    with open(list1, encoding='utf-8') as f:
        for line in f:
            w = line.strip('\n').split(',')[0]
            w.replace('_', '').replace('-', '')
            llama_wordlist.append(w.lower())
    print("base word list :\n", len(llama_wordlist))

    test_wordlist = []
    with open(list2, encoding='utf-8') as f:
        for line in f:
            w = line.strip('\n').split(',')[0]
            w.replace('_', '').replace('-', '')
            test_wordlist.append(w.lower())
    print("official word list :\n", len(test_wordlist))

    llama_set = set(llama_wordlist)
    test_set = set(test_wordlist)
    print("base set number:\n", len(llama_set))
    print("official set number:\n", len(test_set))
    same_word = test_set.intersection(llama_set)
    print("the number of same words = {}, percentage = {}".format(len(same_word), len(same_word)/len(test_set)))


def wordlist_gen(ep):
    exist_words = []
    word_num = 0

    while word_num < 1000:
        try:
            print("word_num = ", word_num)
            data = llm_model(ep)
            print("response data:\n", data)
            idx_l = data.index("[")
            idx_r = data.index("]")
            lpart = data[idx_l : idx_r+1]
            round_words = eval(lpart)
            for w in round_words:
                if w not in exist_words:
                    exist_words.append(w)
                    word_num += 1
                    with open("llama_country.txt", "a") as file:
                        file.write(w + "\n")
        except:
            continue


    return exist_words



if __name__ == "__main__":
    # endpoint = "https://countries.trevorblades.com/"
    # llama_words = wordlist_gen(endpoint)
    word_compare("llama_country.txt", "country_keywords.txt")