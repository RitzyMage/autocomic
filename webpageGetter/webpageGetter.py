import urllib.request
from urllib.parse import urlparse
import re
import os
import requests
from requests_html import HTML

class webpageGetter:
	def __init__(self, runJavascript, javascriptTimeout):
		self.baseURL = ""
		self.basePath = ""
		self.noQueryURL = ""

		self.timeout = javascriptTimeout

		self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.118 Safari/537.36"
		opener = urllib.request.build_opener()
		opener.addheaders = [('User-agent', self.userAgent)]
		urllib.request.install_opener(opener)


		self.runJavascript = False if not runJavascript else True

	def getFullURL(self, path):
		if path == "":
			return path
		elif path[0] == '/':
			return self.baseURL + path
		elif path[0] == '?':
			return self.noQueryURL + path
		elif path[:2] == '..':
			return re.sub(r"/[^/]*/\.\./", "/", (self.noQueryURL or self.basePath) + '/' + path) 
		elif path[:4] != "http":
			return self.basePath + '/' + path
		return path

		
	def _updateBaseURL(self, url):
		info = urlparse(url)
		self.baseURL = info.scheme + "://" + info.netloc
		self.basePath = os.path.dirname(url)
		if ('?' in url):
			self.noQueryURL = url[:url.index('?')]
	

	def getPage(self, url):
		url = self.getFullURL(url)
		self._updateBaseURL(url)
		print("getting", url)
		text = requests.get(url, headers={"User-agent": self.userAgent}).text
		print("got page from URL", url, "with length", len(text))
		if self.runJavascript:
			print("\trunning javascript...")
			html = HTML(html=text)
			html.render(timeout=self.timeout)
			text = html.html
			print("\tdone.")
		return text

	def downloadFile(self, fileURL):
		fullURL = self.getFullURL(fileURL.strip().replace(' ', '%20'))
		local_filename = urllib.request.urlretrieve(fullURL)[0]
		
		return local_filename