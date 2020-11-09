from lxml.cssselect import CSSSelector
import lxml.html
from .HTMLSearch import HTMLSearch

class CSSSearch(HTMLSearch):
	def __init__(self, imgSelect: str, titleSelect: str, nextSelect: str, chapterSelect: str, chapterGet: str):
		super().__init__(imgSelect, titleSelect, nextSelect, chapterSelect, chapterGet)
		self.imgSelect = self._css(imgSelect)
		self.titleSelect = self._css(titleSelect)
		self.nextSelect = self._css(nextSelect)
		self.chapterSelect = self._css(chapterSelect)

	def _css(self, selector):
		if not selector:
			return None
		return CSSSelector(selector)

	def _getBody(self, html):
		return lxml.html.fromstring(html)

	def _getElements(self, selector):
		return selector(self.html)