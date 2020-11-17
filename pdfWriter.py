from comicGetter import comicGetter
from generateHeader import generateHeader
import os
from PIL import Image, ImageFile
import shutil
import subprocess
from imageProcessing.split import splitFile
from imageProcessing.removeTransparency import remove_transparency
from imageProcessing.shrinkImage import shrinkImage, getImageDims

ImageFile.LOAD_TRUNCATED_IMAGES = True

def escapeString(toEscape):
	return toEscape.translate(
		str.maketrans({
			"\\": "\\\\",
			"^": "\\^",
			"$": "\\$",
			"*": "\\*",
			"%": "\\%",
			"{": "\\{",
			"}": "\\}",
			"#": "",
			"&": "\\&",
			"_": "\\_",
			"|": "\\|"
			}))


MARGIN = 20

class pdfWriter:
	def __init__(self, name, author, pageColor, textColor, optionalHeight, optionalWidth, jpgQuality):
		self.title = name


		self.pageHeight = int(optionalHeight) if optionalHeight else 1200
		self.pageWidth = int(optionalWidth) if optionalWidth else 800
		self.jpgQuality = jpgQuality if jpgQuality else 95

		self.workWidth = self.pageWidth - (2 * MARGIN)
		self.workHeight = self.pageHeight - (2 * MARGIN)
		self.comicNumber = 0

		self.lastChapterName = ""

		self.bodyFile = "body.txt"
		self.headerFile = "header.txt"

		self.pageColor = pageColor

		self.addTitle = True

		self.indexFilename = ".index"
		if(os.path.isfile(self.indexFilename)):
			indexFile = open(self.indexFilename, 'r')
			self.comicNumber = int(indexFile.readline())
			self.lastChapterName = indexFile.readline()
			indexFile.close()

		generateHeader(name, author, pageColor, textColor, self.pageWidth, self.pageHeight, MARGIN)

		if not os.path.exists('images'):
			os.makedirs('images')

	def addComic(self, comic):
		for image in comic.imageFiles:
			self._addComic(comic, image)
	
	def _stripUnicode(self, string):
		return escapeString(string.encode('ascii', "xmlcharrefreplace").decode('ascii'))
	
	def _getTitle(self, comic):
		return self._stripUnicode(comic.title) if comic.title else ""

	def _getMouseover(self, comic):
		return self._stripUnicode(comic.titleText)

	def _addComic(self, comic, image):
		self.comicNumber += 1
		width, height = getImageDims(image)
		widthFactor = 1.3

		self._addChapterName(comic)

		if width >= self.workWidth * widthFactor and height < self.workHeight:
			images = splitFile(image, self.workWidth, axis=1)
			for i in range(len(images)):
				self._addComicFullWidth(height, comic, images[i], suffix="h" + str(i))
		else:
			self._addComicFullWidth(height, comic, image)

	def _addComicFullWidth(self, height, comic, image, suffix=""):
		if height < self.workHeight:
			image = self._getComicImage(image, suffix)
			self._addComicInfo(self._getTitle(comic), image, self._getMouseover(comic))
		else:
			splitHeight = min(1, getImageDims(image)[0] / self.workWidth) * (self.workHeight + MARGIN)
			images = splitFile(image, splitHeight)
			for i in range(len(images)):
				image = self._getComicImage(images[i], suffix="p" + str(i))
				self._addComicInfo(self._getTitle(comic) if i == 0 else "",
					image,
					self._getMouseover(comic) if i is len(images) - 1 else "")
				os.remove(images[i])
	
	def _addChapterName(self, comic):
		name = escapeString(comic.chapterName)
		if name != "" and name != self.lastChapterName:
			if self.comicNumber == 1:
				with open(self.bodyFile,'a') as comics:
					comics.write("\t\\begingroup\\let\\cleardoublepage\\clearpage\\tableofcontents\\endgroup\n")
		 
			self.lastChapterName = name

			with open(self.bodyFile,'a') as comics:
				comics.write("""\t\\newpage
					\\begin{{center}}
						\\vspace*{{\\fill}}
						\\section{{{0}}}
						\\vspace*{{\\fill}}
					\\end{{center}}
					\\newpage\n""".format(name))
			

	def finish(self):
		finalFilename = 'result.latex'
		with open(finalFilename,'w') as finalFile:
			for f in [self.headerFile, self.bodyFile]:
				with open(f,'r') as currentFile:
					shutil.copyfileobj(currentFile, finalFile)
			finalFile.write("\\end{document}")

		subprocess.run(["rubber", "-d", finalFilename])

		os.remove("result.latex")
		os.remove("result.aux")
		os.remove("result.log")
		if self.lastChapterName != "":
			os.remove("result.toc")

	def _getComicImage(self, comic, suffix=""):
		title = ''.join(e for e in self.title if e.isalnum())
		return shrinkImage(comic, self.workWidth, title, self.comicNumber, self.pageColor, self.jpgQuality, suffix)
	
	def _addComicInfo(self, title, image, mouseover):
		with open(self.bodyFile,'a') as comics:
			comics.write("\t\\comic{{{0}}}{{{1}}}{{{2}}}\n".format(title, image, mouseover))

	def save(self):
		indexFile = open(self.indexFilename, 'w')
		indexFile.write(str(self.comicNumber) + "\n") 
		indexFile.write(self.lastChapterName) 
		indexFile.close()