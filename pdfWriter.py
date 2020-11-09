from comicGetter import comicGetter
from generateHeader import generateHeader
import os
from PIL import Image, ImageFile
import shutil
import subprocess
from split import splitFile

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

def remove_transparency(im, bg_color=(255, 255, 255)):
	if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

		alpha = im.convert('RGBA').split()[-1]
		bg = Image.new("RGB", im.size, tuple(bg_color) + (255,))
		bg.paste(im, mask=alpha)
		return bg
	if im.mode != 'RGB':
		return im.convert('RGB')
	else:
		return im

def getResizedDims(width, image):
	percentSmaller = min(width / float(image.size[0]), 1)
	newHeight = max(int(image.size[1] * percentSmaller), 1)
	newWidth = max(int(image.size[0] * percentSmaller), 1)
	return newWidth, newHeight

def getImageDims(filename):
	image = Image.open(filename)
	return image.size #getResizedDims(width, image)

def shrinkImage(filename, width, name, number, bgColor, quality, suffix=""):
	image = Image.open(filename)

	newWidth, newHeight = getResizedDims(width, image) 

	image = image.resize((newWidth, newHeight), Image.ANTIALIAS)
	image = remove_transparency(image, bgColor)
	newFilename = "images/" + name + "-" + str(number) + suffix + ".jpg"
	image.save(newFilename, quality=quality)

	return newFilename

class pdfWriter:
	def __init__(self, name, author, pageColor, textColor, optionalHeight, optionalWidth, jpgQuality):
		self.title = name

		if optionalHeight:
			self.pageHeight = int(optionalHeight)
		else:
			self.pageHeight = 1200

		if optionalWidth: 
			self.pageWidth = int(optionalWidth)
		else:
			self.pageWidth = 800

		if jpgQuality:
			self.jpgQuality = jpgQuality
		else:
			self.jpgQuality = 95

		self.margin = 20
		self.workWidth = self.pageWidth - (2 * self.margin)
		self.workHeight = self.pageHeight - (2 * self.margin)
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

		generateHeader(name, author, pageColor, textColor, self.pageWidth, self.pageHeight, self.margin)

		if not os.path.exists('images'):
			os.makedirs('images')

	def addComic(self, comic):
		self.addTitle = True
		for image in comic.imageFiles:
			self._addComic(comic, image)
			self.addTitle = False
	
	def _addComic(self, comic, image):
		self.comicNumber += 1
		width, height = getImageDims(image)
		widthFactor = 1.3

		self._addChapterName(comic)

		if width >= self.workWidth * widthFactor and height < self.workHeight:
			images = splitFile(image, self.workWidth, axis=1)
			for i in range(len(images)):
				self._addComicFullWidth(height, comic, images[i], suffix="h" + str(i))
				self.addTitle = False
		else:
			self._addComicFullWidth(height, comic, image)

	def _addComicFullWidth(self, height, comic, image, suffix=""):
		if height < self.workHeight:
			image = self._getComicImage(image, suffix)
			self._addComicInfo(comic.title if self.addTitle and comic.title else "", image, comic.titleText if self.addTitle else "")
		else:
			splitHeight = min(1, getImageDims(image)[0] / self.workWidth) * (self.workHeight + self.margin)
			images = splitFile(image, splitHeight)
			for i in range(len(images)):
				image = self._getComicImage(images[i], suffix="p" + str(i))
				self._addComicInfo(comic.title if i == 0 and self.addTitle and comic.title else "", image, comic.titleText if i is len(images) - 1 and self.addTitle else "")
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
		mouseover = escapeString(mouseover if mouseover else "")
		title  = escapeString(title)
		with open(self.bodyFile,'a') as comics:
			comics.write("\t\\comic{{{0}}}{{{1}}}{{{2}}}\n".format(title, image, mouseover))

	def save(self):
		indexFile = open(self.indexFilename, 'w')
		indexFile.write(str(self.comicNumber) + "\n") 
		indexFile.write(self.lastChapterName) 
		indexFile.close()