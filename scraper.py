import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import lxml

# crawled = []

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    if resp.status != 200:
        print(resp.error)
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    #if it is permitted to crawl the url, parse resp.raw_response.content for links
    urls = list()
    if is_valid(resp.raw_response.url):
        # parse resp.raw_response.content look into BeautifulSoup, lxml
        urls.append(...)
    #the urls in the list have to be defragmented which can be done with urlparse.urldefrag
    #make sure to change relative urls to absolute urls (look into urljoin)
    return urls

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        # parse the hostname to check if the domain is ics.uci.edu, cs.uci.edu, informatics.uci.edu, stat.uci.edu
        # consider splitting by . and checking the last 3 elems in the list to see if it is a valid domain
        # may consider parsing in a different way later
        hostname_parse = parsed.hostname.split('.')
        domain = hostname_parse[-3:]
        if domain != ['ics', 'uci', 'edu'] or domain != ['cs', 'uci', 'edu'] \
            or domain != ['informatics', 'uci', 'edu'] or domain != ['stat', 'uci', 'edu']:
            return False
        #check the robots.txt file (does the website permit the crawl)
        parsed.replace(path='robots.txt')
        # access the file
        file = open(parsed, "r")
        line = file.readline()
        check_for_disallow = False
        while line:
            if(check_for_disallow == False):
                index = line.find("User-agent: ")
                if index != -1:
                    robot = line[len("User-agent: "):]
                if robot == USERAGENT or '*': # dk if correct check later
                    #look at disallow statements
                    disallow = True
                    #maybe set a boolean to true so we know to check?
                ...
            line = file.readline()
        
        # parse it by splitting? (find a different way later)
        # check user agent and disallow
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
