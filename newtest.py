import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urldefrag
from scraper import is_valid
import pdb
def main():
	domain = ['ics', 'uci', 'edu']
	domain2 = ['ics', 'uci', 'edu']
	if domain == domain2:
		print ("Yes!")
	url = "https://www.ics.uci.edu/"
	r = requests.get(url)
	html = r.text

	soup = BeautifulSoup(html, "html5lib")

	links = {a.get('href') for a in soup.findAll('a') if a.get('href') != "#"}
	urls = list()
	for link in links:
		cleanurl = urldefrag(link)[0]
		base = urldefrag(url)[0]
		parsed = urlparse(cleanurl)
		if (parsed.netloc) == "":
			cleanurl = urljoin(base, cleanurl)
		urls.append(cleanurl)
	print("\n\n Here's the list \n")
	breakpoint()
	for example in urls:
		if (is_valid(example)):
			print(example, sep = "\n")
if __name__ == "__main__":
    main()
