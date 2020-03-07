from comicGetter import comicGetter
from generateHeader import generateHeader
import os
from PIL import Image
import shutil
import subprocess
from split import split

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
    newHeight = int(image.size[1] * percentSmaller)
    newWidth = int(image.size[0] * percentSmaller)
    return newWidth, newHeight

def getImageDims(filename, width):
    image = Image.open(filename)
    return getResizedDims(width, image)

def shrinkImage(filename, width, name, number, bgColor, suffix=""):
    image = Image.open(filename)

    newWidth, newHeight = getResizedDims(width, image) 

    image = image.resize((newWidth, newHeight), Image.ANTIALIAS)
    image = remove_transparency(image, bgColor)
    newFilename = "images/" + name + "-" + str(number) + suffix + ".jpg"
    image.save(newFilename, quality=95)

    return newFilename

class pdfWriter:
    def __init__(self, name, author, pageColor, textColor, optionalHeight):
        self.title = name

        self.pageWidth = 780
        if optionalHeight:
            self.pageHeight = optionalHeight
        else:
            self.pageHeight = 1200
        self.margin = 30
        self.workWidth = self.pageWidth - (2 * self.margin)
        self.workHeight = self.pageHeight - (2 * self.margin)
        self.comicNumber = 0

        self.lastChapterName = ""

        self.bodyFile = "body.txt"
        self.headerFile = "header.txt"

        self.pageColor = pageColor

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
        self.comicNumber += 1
        width, height = getImageDims(comic.imageFile, self.workWidth)
        widthFactor = 2
        proportions = 2.5

        self._addChapterName(comic)

        if width >= self.workWidth * widthFactor and width > height * proportions:
            images = split(comic.imageFile, self.workWidth, axis=1)
            for image in images:
                self._addComicFullWidth(height, comic, image)
        else:
            self._addComicFullWidth(height, comic, comic.imageFile)

    def _addComicFullWidth(self, height, comic, image):
        textSize = 20
        if height + textSize < self.workHeight:
            image = self._getComicImage(image)
            self._addComicInfo(comic.title, image, comic.titleText)
        else:
            images = split(image, self.workWidth)
            for i in range(len(images)):
                image = self._getComicImage(images[i], suffix="p" + str(i))
                self._addComicInfo(comic.title if i is 0 else "", image, comic.titleText if i is len(images) - 1 else "")
                os.remove(images[i])
    
    def _addChapterName(self, comic):
        name = escapeString(comic.chapterName)
        if name != "" and name != self.lastChapterName:
            if self.comicNumber is 1:
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
        return shrinkImage(comic, self.workWidth, title, self.comicNumber, self.pageColor, suffix)
    
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