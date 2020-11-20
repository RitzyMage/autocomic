from comicGetter import comicGetter
from generateHeader import generateHeader
import os
import shutil
import subprocess
from imageProcessing.split import splitFile
from imageProcessing.shrinkImage import shrinkImage, getImageDims


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
INDEX_FILENAME = ".index"
BODY_FILE = "body.txt"
HEADER_FILE = "header.txt"

MAX_WIDTH = 1.3


class pdfWriter:
    def __init__(self, name, author, pageColor, textColor, optionalHeight, optionalWidth, jpgQuality):
        self.title = name

        self.pageHeight = int(optionalHeight) if optionalHeight else 1200
        self.pageWidth = int(optionalWidth) if optionalWidth else 800
        self.workWidth = self.pageWidth - (2 * MARGIN)
        self.workHeight = self.pageHeight - (2 * MARGIN)

        self.jpgQuality = jpgQuality if jpgQuality else 95
        self.pageColor = pageColor

        self.lastChapterName = ""
        self.comicNumber = 0
        self._restoreState()

        generateHeader(name, author, pageColor, textColor,
                       self.pageWidth, self.pageHeight, MARGIN)

        if not os.path.exists('images'):
            os.makedirs('images')

    # PUBLIC
    def addComic(self, comic):
        print("adding comic", self.comicNumber + 1, "to pdf")
        for image in comic.imageFiles:
            print("adding image", image, "to pdf")
            self._addComic(comic, image)

    def save(self):
        indexFile = open(INDEX_FILENAME, 'w')
        indexFile.write(str(self.comicNumber) + "\n")
        indexFile.write(self.lastChapterName)
        indexFile.close()

    def finish(self):
        escapedName = self.title.replace(' ', '')
        finalFilename = escapedName + '.latex'
        with open(finalFilename, 'w') as finalFile:
            for f in [HEADER_FILE, BODY_FILE]:
                with open(f, 'r') as currentFile:
                    shutil.copyfileobj(currentFile, finalFile)
            finalFile.write("\\end{document}")

        subprocess.run(["rubber", "-d", finalFilename])

        os.remove(finalFilename)
        os.remove(escapedName + ".aux")
        os.remove(escapedName + ".log")
        if self.lastChapterName != "":
            os.remove(escapedName + ".toc")

    # PRIVATE
    def _restoreState(self):
        if (os.path.isfile(INDEX_FILENAME)):
            print("restoring state of pdf")
            indexFile = open(INDEX_FILENAME, 'r')
            self.comicNumber = int(indexFile.readline())
            self.lastChapterName = indexFile.readline()
            print("set comic number to", self.comicNumber)
            if (self.lastChapterName):
                print("set chapter name to", self.lastChapterName)
            indexFile.close()

    def _stripUnicode(self, string):
        return escapeString(string.encode('ascii', "replace").decode('ascii'))

    def _getTitle(self, comic):
        return self._stripUnicode(comic.title) if comic.title else ""

    def _getMouseover(self, comic):
        return self._stripUnicode(comic.titleText)

    def _addComic(self, comic, image):
        self.comicNumber += 1
        width, height = getImageDims(image)

        self._addChapterName(comic)

        if width >= self.workWidth * MAX_WIDTH and height < self.workHeight:
            print("image", image, "is too wide; splitting...")
            images = splitFile(image, self.workWidth, axis=1)
            for i in range(len(images)):
                self._addComicFullWidth(comic, images[i], "h" + str(i))
        else:
            self._addComicFullWidth(comic, image)

    def _addComicFullWidth(self, comic, image, suffix=""):
        height = getImageDims(image)[1]
        title = self._getTitle(comic)
        mouseover = self._getMouseover(comic)

        if height < self.workHeight:
            image = self._getComicImage(image, suffix)
            self._addComicInfo(title, image, mouseover)
        else:
            print("image", image, "is too tall; splitting")
            shrinkFactor = min(1, height / self.workWidth)
            splitHeight = shrinkFactor * (self.workHeight + MARGIN)
            images = splitFile(image, splitHeight)
            self._addSplitImages(images, title, mouseover, suffix)

    def _addSplitImages(self, images, title, mouseover, suffix=""):
        for i in range(len(images)):
            _suffix = suffix + "p" + str(i)
            image = self._getComicImage(images[i], suffix)
            _title = title if i == 0 else ""
            _mouseover = mouseover if i is len(images) - 1 else ""
            self._addComicInfo(_title, image, _mouseover)
            os.remove(images[i])

    def _addChapterName(self, comic):
        name = escapeString(comic.chapterName)

        if name != "" and name != self.lastChapterName:
            with open(BODY_FILE, 'a') as comics:
                if self.comicNumber == 1:
                    comics.write(
                        "\t\\begingroup\\let\\cleardoublepage\\clearpage\\tableofcontents\\endgroup\n")

                comics.write("""\t\\newpage
					\\begin{{center}}
						\\vspace*{{\\fill}}
						\\section{{{0}}}
						\\vspace*{{\\fill}}
					\\end{{center}}
					\\newpage\n""".format(name))

            self.lastChapterName = name

    def _getComicImage(self, comic, suffix=""):
        title = ''.join(e for e in self.title if e.isalnum())
        return shrinkImage(comic, self.workWidth, title, self.comicNumber, self.pageColor, self.jpgQuality, suffix)

    def _addComicInfo(self, title, image, mouseover):
        print("adding comic info", title, "-", image, "-", mouseover)
        with open(BODY_FILE, 'a') as comics:
            comics.write("\t\\comic{{{0}}}{{{1}}}{{{2}}}\n".format(
                title, image, mouseover))
