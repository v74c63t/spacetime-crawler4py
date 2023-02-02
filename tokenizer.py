import requests
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

def tokenizeCount(url, wDict):
    soup = BeautifulSoup(requests.get(url).content, "lxml")
    unfiltered = word_tokenize(soup.get_text())
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