from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# import pdb

stop_words = set(stopwords.words('english'))

def printFreq(frequenciesDict):
    iterator = iter(frequenciesDict.items())
    for i in range(50):
        print(next(iterator))

def tokenizeCount(resp, wDict):
    # this function takes in a response and a dictionary and parses through
    # the content of the response and counts the frequecy that each word appears
    # given that it is not a stop word
    # wDict: defaultdict(int)
    # we are assuming that wDict is a defaultdictionary of integers
    soup = BeautifulSoup(resp.raw_response.content, "lxml")
    unfiltered = word_tokenize(soup.get_text())
    #cleaned = list()
    for w in unfiltered:
        if w not in stop_words and w.isalnum():
            # cleaned.append(w)
            # if the word is not a stop word and it is alphanumeric
            # we will turn the word into lower case and add 1 to the count 
            # in the defaultdictionary for said word
            wDict[w.lower] += 1
    # cleaned.sort()
    # for i in list(map(str.lower, cleaned)):
    #     if i not in wDict:
    #         wDict[i] = 1
    #     else:
    #         wDict[i] += 1
    # i was thinking maybe we could sort the dictionary at the end?
    # or maybe we could have another variable that has a list of the
    # 50 most common words at that time not too sure
    sort = sorted(wDict.items(), key=lambda x: x[1], reverse=True)
    return wDict
    # return dict(sorted(wDict.items(), key = lambda x:(x[1] * -1, x[0])))