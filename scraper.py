import re
from urllib.parse import urlparse, urljoin, urldefrag, urlunparse
from bs4 import BeautifulSoup
import lxml
import urllib.robotparser
import nltk
import configparser
from collections import defaultdict
import simhash
import tokenizer
from difflib import SequenceMatcher

config = configparser.ConfigParser()
config.read("config.ini")
userAgent = config['IDENTIFICATION']['USERAGENT']
default_time = float(config['CRAWLER']['POLITENESS'])
polite_time = default_time # used to honor politeness delay per site, if not found defaults to config
sub_domains = defaultdict(int) #{key: subdomain, value: # of unique pages}
largest_pg = ('',0) #(resp.url, word count) 
unique_links = set() 
prev_urls = []
word_freq = defaultdict(int) #{key: word, value: word count}
prev_simhashes = [] # list of simhashes of previous urls which are used for near duplicate detections

def output_report():
    # we use this function to write information for the report to an output file
    with open("output.txt", "w") as output_file:
        output_file.write(f"Number of unique pages: {len(unique_links)}.\n")
        output_file.write(f"The longest page is {largest_pg[0]} with {largest_pg[1]} words.\n")
        output_file.write(f"The 50 most common words: {sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[0:50]}.\n")
        output_file.write(f"Number of subdomains in ics.uci.edu: {sum(sub_domains.values())}\n")
        for k, v in sorted(sub_domains.items(), key=lambda x: x[0]):
            output_file.write(f"    {k}, {v}\n")


def report_info(text, url):
    # text: the text obtained from BeautifulSoup.get_text() using resp.raw_response.content
    words = nltk.tokenize.word_tokenize(text.lower())

    # word_freq is a default dictionary of integers with the keys being the word and the values being the word count
    # that is used to record how frequent words that are not considered stop words appear in each of the webpages 
    # we use tokenizeCount with the words list of the current page to update the global dictionary accordingly
    # this is used in output_report to generate the 50 most common words found during the crawl
    global word_freq 
    word_freq = tokenizer.tokenizeCount(words, word_freq)

    # largest_pg is a tuple containing an url and the number of words of that page
    # we compare the amount of words of the current url to the amount of words of the current largest page
    # largest page will be replaced if the current url has more words
    global largest_pg 
    if len(words) > largest_pg[1]: largest_pg = (url, len(words))

    # we check for any unique pages that belongs to a subdomain of ics.uci.edu
    global sub_domains
    parsed = urlparse(url)
    url = urldefrag(url)[0]
    if parsed.netloc[-12:] == '.ics.uci.edu' and parsed.netloc != 'www.ics.uci.edu':
        # we check if the url is a subdomain of ics.uci.edu by looking at netloc
        sub_domain =  parsed._replace(fragment="", params="", query="",path="")
        # if the url is not in unique links, we have not found it so far so it can be counted as a unique page
        if url not in unique_links:
            # we parse out the subdomain using ._replace and urlunparse so it can be used as a key
            # we use the key in the global default dictionary so we can add to the count to indicate 
            # we found a unique page for this subdomain
            sub_domain = urlunparse(sub_domain)
            sub_domains[sub_domain] += 1


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    urls = list()

    # we reject any pages that do not have a 200 status
    # we will not crawl the page and therefore return an empty list
    if resp.status != 200:
        print(resp.error)
        return urls

    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    
    # we check if a response is given or if there is any content in the page to see if there 
    # is any data associated with the url/basically checking if it's a dead url 
    # if that is the case, we will not crawl the page and return an empty list                        
    if resp.raw_response == None or len(resp.raw_response.content) == 0:
        return list()   

    # we check if we visited the url before or if they are similar to previous urls
    parsed = urlparse(resp.url)
    global prev_urls
    for prev_url in prev_urls:
        # we compare the current url to the global list of all the previous urls 
        # we crawled to see if there is a match, an empty list is returned if there is a 
        # match because we will not crawl the page
        if resp.url == prev_url:return urls
        prev_parsed = urlparse(prev_url)
        # we then compare the paths of the current url to the paths of the previous urls
        # this is to make sure we do not end up in a trap where we are crawling a url
        # that has repeating paths and ultimately leads to a page that we have seen/crawled before
        if parsed.netloc == prev_parsed.netloc:
            # if netlocs of the urls are the same, we imported SequenceMatcher to check the 
            # similarities of the paths and if the two urls are similar by 90% or more, we 
            # will not crawl the page
            if SequenceMatcher(None, parsed.path, prev_parsed.path).ratio() >= .90:
                return urls

    # we used BeautifulSoup to get the text content of the page from resp.raw_response.content
    # we used .decode so it would ignore utf-8 errors
    soup = BeautifulSoup(resp.raw_response.content.decode('utf-8','ignore'), "lxml")
    resp_text = soup.get_text()
    resp_text_words = nltk.tokenize.word_tokenize(resp_text.lower())

    # we choose to not crawl any pages that are considered large files, but have low information value and return an empty list
    # we consider any files that exceed 2000 words to be a large file because pages on average are below or
    # around that word count
    if len(resp_text_words) > 2000:
        # we reject any pages with more than 20000 words because we believe that with how large the page is
        # it is very unlikely for it to not have low information value
        if len(resp_text_words) > 20000:
            return urls
        # if the page has between 2000 and 20000 words, we need more information to check if it has low information value
        # to do so, we take the words of the page and filter out any stop words and see how many words are left
        # if there are fewer that 100 words left, that means a large part of the page is filled with stop words
        # and therefore should be considered to have low information value and will be rejected.
        if len(tokenizer.remove_stop_words(resp_text_words)) < 100: # considered low info
            return urls

    
    # simhash code obtained from here: https://github.com/1e0ng/simhash
    # we imported the simhash library to determine whether two pages are near duplicates or not
    # if the distance between the two simhashes (it essentially looks at the difference between 
    # the two pages) is less than the threshold the two pages are considered near duplicates
    global prev_simhashes
    curr_simhash = simhash.Simhash(resp_text)
    for prev_simhash in prev_simhashes: 
        # we check if the current page is a near duplicate of any page we have seen before by comparing
        # its simhash to the simhashes of previous urls kept in a global list
        # if the current page is a near duplicate with any of the previous pages, we will not crawl the page
        # and return an empty list
        if prev_simhash.distance(curr_simhash) < 10:
            return urls
    prev_simhashes.append(curr_simhash)
    
    report_info(resp_text, resp.url)

    base = urldefrag(resp.url)[0]

    # we are using BeautifulSoup with lxml to find all the a tags in the html file (resp.raw_response.content
    # contains the html content) that also has a href attribute which is used to contain links that link to 
    # different pages or sites 
    # we then use get to get the link associated with the href attribute as long as it is not '#' which means
    # the page links back to itself
    links = {a.get('href') for a in soup.find_all('a') if a.get('href')!="#"}
    for link in links:
        # the urls in the list have to be defragmented which can be done with urlparse.urldefrag
        # we have make sure to change relative urls to absolute urls 
        # these two steps need to be done before adding the url to the url list
        defrag = urldefrag(link)[0] # defrag link
        parsed = urlparse(defrag)
        
        # if the link does not have a netloc, it is most likely a relative url so we use urljoin to join it 
        # with resp.url to turn it into an absolute url
        if parsed.netloc == "":
            defrag = urljoin(base, defrag) 

        urls.append(defrag)

    prev_urls.append(resp.url)

    global unique_links
    unique_links.add(base) 
    # If page is crawled successfully, it is added to the set of unique links
    
    return urls

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        # if these phrases are found in the query, it either leads to external
        # sites or traps so we return false for urls containing them
        query = parsed.query
        if "share=" == query[0:6] or "ical=" == query[0:5]:
            return False
        if '?share=' in parsed.query or 'date=' in parsed.query: return False

        # this regular expression checks are to make sure that we only look
        # at webpages/that the url actually points to a webpage
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|apk|war"
            + r"|thmx|mso|arff|rtf|jar|csv|img|jpeg|jpg|png"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|pps|ova)$", parsed.path.lower()):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|apk|war"
            + r"|thmx|mso|arff|rtf|jar|csv|img|jpeg|jpg|png"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|pps|ova)$", parsed.query.lower()):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|apk|war"
            + r"|thmx|mso|arff|rtf|jar|csv|img|jpeg|jpg|png"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|pps|ova).*$", parsed.query.lower()):
            return False
        if re.match(
            r".*/(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv|img|jpeg|jpg|png"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|pps|ova)/?.*$", parsed.path.lower()):
            return False
        if re.match(
            r".*/(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv|img|jpeg|jpg|png"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|pps|ova)/?.*$", parsed.query.lower()):
            return False
       
        # the domain of the url has to be one of the four valid domains (ics.uci.edu, cs.uci.edu
        # stat.uci.edu, informatics.uci.edu)
        # we check this by looking at the netloc of the url
        netloc_parse = parsed.netloc.split('.')
        domain = netloc_parse[-3:]
        if (domain[-2:] != ['uci','edu'] or (domain[0] not in ['ics', 'cs', 'stat', 'informatics'])):
            return False

        # a calendar is considered an infinite trap because it can generate an infinite amount of pages
        # if you continue to press the next button to a calendar you will never reach an end point
        # since pages keep getting generated therefore it is a trap
        # to avoid encountering them we used several checks to detect if the url leads to a calendar
        # page or not and if it does it will be considered invalid
        if ('calendar' in url.lower()): return False 
        if 'events' in parsed.path.lower(): return False
        # this regular expression check checks to see if there is anything that resembles a date
        # format ####(year)-##(month)-##(day) in the url so we can reject it because it likely
        # points to a calendar
        if re.match(
            r".*/[0-9][0-9][0-9][0-9]\-[0-1][0-9]\-[0-3][0-9]/?.*$", parsed.path.lower()):
            return False

        # we imported robotparser so we can use RobotFileParser to parse the robots.txt file of the 
        # site so we can figure out if the site permits the crawl from our user agent and to also
        # figure out the crawl delay for that site
        robot = urljoin(url, '/robots.txt')
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robot)
        rp.read()

        # we use this to figure out the crawl delay for the site so we can adjust the politeness appropriately
        if (rp.crawl_delay(userAgent)): polite_time = rp.crawl_delay(userAgent)

        # if can_fetch returns true, the url is valid because the robots.txt file permits 
        # our user agent from crawling that particular url
        # if it does not, we are prohibited from crawling that url
        if rp.can_fetch(userAgent, url): return True
        else: return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise
    # this error occurs if there is no robots.txt associated with said url and thus we are unable 
    # to determine if the site permits the crawl so we choose not to crawl in that scenario
    except urllib.error.URLError:
        return False
