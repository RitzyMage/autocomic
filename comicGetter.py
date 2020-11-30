import os
import re

from htmlSearch.CSSSearch import CSSSearch
from htmlSearch.RegexSearch import RegexSearch
from webpageGetter.webpageGetter import webpageGetter

import requests
import urllib.request

class NoImageError(Exception):
	def __init__(self, *args):
		self.message = args[0]

	def __str__(self):
		return '< No Image Error: {0} >'.format(self.message)

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
		javascriptTimeout = (info.get("javascriptTimeout") or 60) if runJavascript else None

		nextSelect = info["nextSelect"]

		if useCSS is None or useCSS:
			self.htmlSearch = CSSSearch(imgSelect, titleSelect, nextSelect, chapterElement, chapterGet)
		else:
			self.htmlSearch = RegexSearch(imgSelect, titleSelect, nextSelect, chapterElement, chapterGet)
		
		self.webpageGetter = webpageGetter(runJavascript, javascriptTimeout)

	#PUBLIC

	def setURLifUnset(self, URL):
		if(os.path.isfile(self.urlFilename)):
			urlFile = open(self.urlFilename, 'r')
			self._setURL(urlFile.readline())
			print("set URL from file to", self.url)
			urlFile.close()
			self.advance()
		else:
			self._setURL(URL)
			print("starting with url", self.url)

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
			print("next URL was", url, "which is the same URL as last. Finishing...")
			self.url = ""
			return

		self.url = url
		try:
			self._getHTML()
			self._getNext()
			self._getImage()
			self._getTitle()
			self._getChapter()
		except (requests.exceptions.RequestException, urllib.error.HTTPError) as e:
			print("could not get url, details:", e)
			self.url = ""
		except NoImageError as e:
			print("expected exeption", e,  "encountered, advancing")
			self.advance()

	def _getImage(self):
		imageTags = self.htmlSearch.getImages()
		if len(imageTags) == 0:
			raise NoImageError("found no images")
		print("found images", imageTags)

		self.imageFiles = []
		for (imageURL, titleText) in imageTags:
			if not imageURL:
				raise NoImageError("found image with no src")
			self.imageFiles.append(self.webpageGetter.downloadFile(imageURL))

			if (self.hasTitleText):
				self.titleText = titleText

	def _getTitle(self):
		self.title = self.htmlSearch.getTitle()

	def _getNext(self):
		self.next = self.webpageGetter.getFullURL(self.htmlSearch.getNext())
		if self.next:
			print("got next link", self.next)
		else:
			print("no next link found")

	def _getHTML(self):
		self.htmlSearch.setBody(self.webpageGetter.getPage(self.url))
	
	def _getChapter(self):
		self.chapterName = self.htmlSearch.getChapter()

	

