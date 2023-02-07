from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# import pdb

stop_words = set(stopwords.words('english'))

# def printFreq(frequenciesDict):
#     iterator = iter(frequenciesDict.items())
#     for i in range(50):
#         print(next(iterator))

def tokenizeCount(words, freq):
    # this function takes in a response and a dictionary and parses through
    # the content of the response and counts the frequecy that each word appears
    # given that it is not a stop word
    # word_freq: defaultdict(int)
    # we are assuming that wDict is a defaultdictionary of integers
    #if resp.raw_response != None:
    #words = word_tokenize(text)
    for word in words:
        if word not in set(stopwords.words('english')) and word.isalnum():
            # if the word is not a stop word and it is alphanumeric
            # we will turn the word into lower case and add 1 to the count 
            # in the defaultdictionary for said word
            freq[word] += 1
    return freq
    # sorting dictionaries dont rly work/do anything
    # wDict is a defaultdict so this might cause problems so ill just return the updated dict
    # return dict(sorted(wDict.items(), key = lambda x:(x[1] * -1, x[0])))

def remove_stop_words(words):
    #words = word_tokenize(resp_text.lower())
    filter = []
    for word in words:
        if word not in set(stopwords.words('english')) and word.isalnum():
            filter.append(word)
    return filter
