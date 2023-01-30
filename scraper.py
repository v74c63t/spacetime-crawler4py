import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
import lxml
import urllib.robotparser


def scraper(url, resp):
    # maybe add a check for text content here and if there isnt much just dont call extract_next_link
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
        # check if there is actually data associated with the url (make sure it is not a dead url)
        if len(resp.raw_response.content) == 0:
            return list()
        # parse resp.raw_response.content look into BeautifulSoup, lxml
        # resp.raw_response.content should be html content
        # we want all the a tags that have href attributes
        soup = BeautifulSoup(resp.raw_response.content, lxml)
        # we are using BeautifulSoup lxml to find all the a tags in the html file that also has a
        # href attribute which is used to contain links that link to different pages or sites
        # we then use get to get the link associated with the href attribute
        links = [a.get('href') for a in soup.findall('a', href=True)]
        for link in links:
            #the urls in the list have to be defragmented which can be done with urlparse.urldefrag
            #make sure to change relative urls to absolute urls (look into urljoin)
            #these two steps need to be done before adding it to the url list
            url = urldefrag(link)[0] # defrag link
            base = urldefrag(resp.url)[0] # not sure if need to defrag base
            url = urljoin(base, url) # join the base to link that is found/ check if this is working correctly if not add / to beginning of url
            # it essentially ensures that we will have the absolute url and not the relative url
    return urls

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        # parse the hostname to check if the domain is ics.uci.edu, cs.uci.edu, informatics.uci.edu, stat.uci.edu
        # consider splitting by . and checking the last 3 elems in the list to see if it is a valid domain
        # may consider parsing in a different way later
        netloc_parse = parsed.netloc.split('.')
        domain = netloc_parse[-3:]
        if domain != ['ics', 'uci', 'edu'] or domain != ['cs', 'uci', 'edu'] \
            or domain != ['informatics', 'uci', 'edu'] or domain != ['stat', 'uci', 'edu']:
            return False
        #check the robots.txt file (does the website permit the crawl)
        robot = urljoin(url, '/robots.txt')
        # access the file
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robot)
        if rp.can_fetch('*', url) or rp.can_fetch(self.config.useragent, url): return True
        else: return False
        # return not re.match(
        #     r".*\.(css|js|bmp|gif|jpe?g|ico"
        #     + r"|png|tiff?|mid|mp2|mp3|mp4"
        #     + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
        #     + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
        #     + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
        #     + r"|epub|dll|cnf|tgz|sha1"
        #     + r"|thmx|mso|arff|rtf|jar|csv"
        #     + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
