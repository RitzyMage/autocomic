import os
import re

from htmlSearch.CSSSearch import CSSSearch
from htmlSearch.RegexSearch import RegexSearch
from webpageGetter.webpageGetter import webpageGetter

import requests
import urllib.request

# gets comic info
class comicGetter:
	def __init__(self, info):
		self.hasTitleText = info["mouseover"]
		self.url = ""
		self.next = ""
		self.imageFiles = []
		self.titleText = ""
		self.title = ""
		self.chapterName = ""

		self.urlFilename = ".url"


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
		
		self.webpageGetter = webpageGetter(runJavascript)

	#PUBLIC

	def setURLifUnset(self, URL):
		if(os.path.isfile(self.urlFilename)):
			urlFile = open(self.urlFilename, 'r')
			self._setURL(urlFile.readline())
			urlFile.close()
			self.advance()
		else:
			self._setURL(URL)

	def advance(self):
		try:
			for file in self.imageFiles:
				os.remove(file)
		except OSError:
			pass
		self._setURL(self.next)

	def save(self):
		urlFile = open(self.urlFilename, 'w')
		urlFile.write(self.url) 
		urlFile.close()

	def validURL(self):
		return self.url != ""

	# PRIVATE

	def _setURL(self, url):
		if url == self.url:
			self.url = ""
			return

		self.url = url
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

	def _getImage(self):
		imageTags = self.htmlSearch.getImages()

		self.imageFiles = []
		for (imageURL, titleText) in imageTags:
			if (imageURL is not None):
				self.imageFiles.append(self.webpageGetter.downloadFile(imageURL))
			else:
				raise IndexError()

			if (self.hasTitleText):
				self.titleText = titleText

	def _getTitle(self):
		self.title = self.htmlSearch.getTitle()

	def _getNext(self):
		self.next = self.webpageGetter.getFullURL(self.htmlSearch.getNext())

	def _getHTML(self):
		self.htmlSearch.setBody(self.webpageGetter.getPage(self.url))
	
	def _getChapter(self):
		self.chapterName = self.htmlSearch.getChapter()

	

