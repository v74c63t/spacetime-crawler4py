from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# import pdb

stop_words = set(stopwords.words('english'))

# def printFreq(frequenciesDict):
#     iterator = iter(frequenciesDict.items())
#     for i in range(50):
#         print(next(iterator))

def tokenizeCount(resp, freq):
    # this function takes in a response and a dictionary and parses through
    # the content of the response and counts the frequecy that each word appears
    # given that it is not a stop word
    # word_freq: defaultdict(int)
    # we are assuming that wDict is a defaultdictionary of integers
    if resp.raw_response != None:
        soup = BeautifulSoup(resp.raw_response.content.decode('utf-8','ignore'), "lxml")
        text = soup.get_text()
        words = word_tokenize(text.encode('utf-8', errors='ignore'))
        for word in words:
            if word not in stop_words and word.isalnum():
                # if the word is not a stop word and it is alphanumeric
                # we will turn the word into lower case and add 1 to the count 
                # in the defaultdictionary for said word
                freq[word.lower] += 1
    return freq
    # sorting dictionaries dont rly work/do anything
    # wDict is a defaultdict so this might cause problems so ill just return the updated dict
    # return dict(sorted(wDict.items(), key = lambda x:(x[1] * -1, x[0])))

def remove_stop_words(resp_text):
    words = word_tokenize(resp_text)
    filter = []
    for word in words:
        if word not in stop_words and word.isalnum():
            filter.append(word)
    return filter
