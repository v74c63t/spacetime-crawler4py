from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# we get a set of stopwords from nltk.corpus which will be used to help 
# filter out any stop words in the words list
stop_words = set(stopwords.words('english'))

def tokenizeCount(words, freq):
    '''
    words: a list of words obtained from using word_tokenize on text of the page
    freq: a defaultdict(int) {key: word, value: word count} that will be updated with the frequency of each word

    this function goes through the words list and updates the count in the dictionary for the word
    as long as it is a valid word

    it returns back the updated dictionary
    '''

    # we go through and add 1 to the count for each word as long as the word is 
    # valid meaning it is not a stopword and it is alphanumeric
    for word in words:
        if word not in set(stopwords.words('english')) and word.isalnum():
            freq[word] += 1
    return freq

def remove_stop_words(words):
    '''
    words: a list of words obtained from using word_tokenize on text of the page
    we return a list of words that is filtered to not contain any stop words (and words that are not alphanumeric)
    '''
    filter = []
    for word in words:
        # words that are stopwords or are not alphanumeric are added to the filter list
        if word not in set(stopwords.words('english')) and word.isalnum():
            filter.append(word)
    return filter
