from .HTMLSearch import HTMLSearch
import re
import lxml.html

class RegexSearch(HTMLSearch):
	def __init__(self, imgSelect: str, titleSelect: str, nextSelect: str, chapterSelect: str, chapterGet: str):
		super().__init__(imgSelect, titleSelect, nextSelect, chapterSelect, chapterGet)
		self.imgSelect = self._getRegex(imgSelect)
		self.titleSelect = self._getRegex(titleSelect)
		self.nextSelect = self._getRegex(nextSelect)
		self.chapterSelect = self._getRegex(chapterSelect)

	def _getElements(self, selector):
		elements = re.findall(selector, self.html)
		return list(map(lambda tag: lxml.html.fromstring(tag), elements))