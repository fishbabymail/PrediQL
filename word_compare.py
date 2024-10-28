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


if __name__ == "__main__":
    word_compare("wordlist/llama_country.txt", "graphql_schema/country_keywords.txt")