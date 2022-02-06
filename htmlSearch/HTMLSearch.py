import re

class HTMLSearch:
	def __init__(self, imgSelect: str, titleSelect: str, nextSelect: str, chapterSelect: str, chapterGet: str):
		self.imgSelect = None
		self.titleSelect = None
		self.nextSelect = None
		self.chapterSelect = None
		self.chapterGet = self._getRegex(chapterGet)

	def getImages(self):
		imageTags = self._getElements(self.imgSelect)
		return self.getImageInfo(imageTags)

	def getNext(self) -> str:
		nextTags = self._getElements(self.nextSelect)
		if len(nextTags) == 0:
			return ""  
		return nextTags[len(nextTags) - 1].get('href') or ""

	def getChapter(self) -> str:
		if not self.chapterSelect:
			return ""

		text = self._getElements(self.chapterSelect)[0].text
		if not text:
			return ""

		return re.findall(self.chapterGet, text)[0]

	def getTitle(self) -> str:
		if not self.titleSelect:
			return ""

		return self._getElements(self.titleSelect)[0].text or ""

	def _getRegex(self, selector: str):
		if not selector or len(selector) < 1:
			return None
		return re.compile(selector, re.IGNORECASE)

	def getImageInfo(self, images):
		result = []
		for image in images:
			if (image.get('src')):
				result.append((image.get('src'), image.get('title')))
			else:
				raise IndexError()
		return result

	def setBody(self, html: str):
		self.html = self._getBody(html)

	def _getElements(self, selector):
		raise NotImplementedError

	def _getBody(self, html):
		return html
	

	