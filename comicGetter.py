import requests
from requests_html import HTML
import urllib.request
from urllib.parse import urlparse
import os
import re

from htmlSearch.CSSSearch import CSSSearch
from htmlSearch.RegexSearch import RegexSearch

# gets comic info
class comicGetter:
	def __init__(self, info):
		self.hasTitleText = info["mouseover"]
		self.url = ""
		self.next = ""
		self.imageFiles = []
		self.baseURL = ""
		self.basePath = ""
		self.titleText = ""
		self.title = ""
		self.urlFilename = ".url"

		self.chapterName = ""
		self.noQueryURL = ""

		imgSelect = info["comicSelect"]
		titleSelect = info["titleSelect"]
		chapters = info["chapters"]
		chapterElement = info["chapterElement"] if chapters else None
		chapterGet = info["chapterRegex"] if chapters else None
		useCSS = info.get("useCSS")
		runJavascript = info.get("runJavascript")
		nextSelect = info["nextSelect"]

		if useCSS is None or useCSS:
			self.htmlSearch = CSSSearch(imgSelect, titleSelect, nextSelect, chapterElement, chapterGet)
		else:
			self.htmlSearch = RegexSearch(imgSelect, titleSelect, nextSelect, chapterElement, chapterGet)
		
		self.runJavascript = False if runJavascript is None or runJavascript is False else True

		self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.118 Safari/537.36"
		opener = urllib.request.build_opener()
		opener.addheaders = [('User-agent', self.userAgent)]
		urllib.request.install_opener(opener)

	# PRIVATE
	def _downloadImage(self, imageTag):
			imageURL = self._getFullURL(imageTag.strip().replace(' ', '%20'))
			local_filename = urllib.request.urlretrieve(imageURL)[0]
		
			return local_filename


	def _getImage(self):
		imageTags = self.htmlSearch.getImages()

		self.imageFiles = []
		for (imageURL, titleText) in imageTags:
			if (imageURL is not None):
				self.imageFiles.append(self._downloadImage(imageURL))
			else:
				raise IndexError()

			if (self.hasTitleText):
				self.titleText = titleText

	def _getTitle(self):
		self.title = self.htmlSearch.getTitle()

	def _getNext(self):
		self.next = self._getFullURL(self.htmlSearch.getNext())

	def _getHTML(self):
		text = requests.get(self.url, headers={"User-agent": self.userAgent}).text
		if self.runJavascript:
			html = HTML(html=text)
			html.render(timeout=60)
			text = html.html
		self.htmlSearch.setBody(text)

	def _updateBaseURL(self):
		info = urlparse(self.url)
		self.baseURL = info.scheme + "://" + info.netloc
		self.basePath = os.path.dirname(self.url)
		if ('?' in self.url):
			self.noQueryURL = self.url[:self.url.index('?')]

	def _getFullURL(self, path):
		if path == "":
			return path
		elif path[0] == '/':
			return self.baseURL + path
		elif path[0] == '?':
			return self.noQueryURL + path
		elif path[:2] == '..':
			return re.sub(r"/[^/]*/\.\./", "/", self.noQueryURL + '/' + path)
		elif path[:4] != "http":
			return self.basePath + '/' + path
		return path
	
	def _getChapter(self):
		self.chapterName = self.htmlSearch.getChapter()

	#PUBLIC

	# gets all necessary data from given URL
	def setURL(self, url):
		if url == self.url:
			self.url = ""
			return

		self.url = url
		self._updateBaseURL()
		try:
			self._getHTML()
			self._getNext()
			self._getImage()
			self._getTitle()
			self._getChapter()
		except (requests.exceptions.RequestException, urllib.error.HTTPError):
			self.url = ""
		except IndexError:
			self.advance()

	# same as set URL, but will prioritize an existing file conatining a URL if it exists.
	# this allows the script to maintain state if ran in multiple sessions.
	def setURLorPast(self, URL):
		if(os.path.isfile(self.urlFilename)):
			urlFile = open(self.urlFilename, 'r')
			self.setURL(urlFile.readline())
			urlFile.close()
			self.advance()
		else:
			self.setURL(URL)

	# sets the current comic to the next comic.
	def advance(self):
		try:
			for file in self.imageFiles:
				os.remove(file)
		except OSError:
			pass
		self.setURL(self.next)

	# save data to the file
	def save(self):
		urlFile = open(self.urlFilename, 'w')
		urlFile.write(self.url) 
		urlFile.close()

	# returns true if the current URL is valid.
	def validURL(self):
		return self.url != ""

