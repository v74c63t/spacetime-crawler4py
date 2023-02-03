from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urldefrag
from scraper import is_valid
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, wordpunct_tokenize
import pdb

stop_words = set(stopwords.words('english'))

def printFreq(frequenciesDict):
    iterator = iter(frequenciesDict.items())
    for i in range(50):
        print(next(iterator))

def tokenize(content, url): 
    # changed requests.get(url).content to content b/c not allowed to use requests library
    soup = BeautifulSoup(content, "lxml")
    unfiltered = word_tokenize(soup.get_text())
    return unfiltered

def filterTokens(unfiltered, wDict)
    # filter out stop words and non-alphanumeric words
    cleaned = list()
    for w in unfiltered:
        if w not in stop_words and w.isalnum():
            cleaned.append(w)
    cleaned.sort()
    for i in list(map(str.lower, cleaned)):
        if i not in wDict:
            wDict[i] = 1
        else:
            wDict[i] += 1
    return dict(sorted(wDict.items(), key = lambda x:(x[1] * -1, x[0])))

    # i was thinking maybe we could sort the dictionary at the end?
    # or maybe we could have another variable that has a list of the
    # 50 most common words at that time not too sure
    # sort = sorted(wDict.items(), key=lambda x: x[1], reverse=True)
    # return wDict
    # return dict(sorted(wDict.items(), key = lambda x:(x[1] * -1, x[0])))

