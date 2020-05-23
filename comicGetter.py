import requests
import lxml.html
from lxml.cssselect import CSSSelector
import urllib.request
from urllib.parse import urlparse
import os
import re


# gets comic info
class comicGetter:
    def __init__(self, imgSelect: str, titleSelect: str, titleText: bool, nextSelect: str):
        self.imgSelect = CSSSelector(imgSelect)
        if len(titleSelect) is not 0: 
            self.titleSelect = CSSSelector(titleSelect)
        else:
            self.titleSelect = None
        self.hasTitleText = titleText
        self.nextSelect = CSSSelector(nextSelect)
        self.url = ""
        self.next = ""
        self.imageFiles = []
        self.baseURL = ""
        self.basePath = ""
        self.titleText = ""
        self.title = ""
        self.urlFilename = ".url"
        self.chapterElement = ""
        self.chapterGet = ""
        self.chapterName = ""
        self.noQueryURL = ""

        self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.118 Safari/537.36"
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', self.userAgent)]
        urllib.request.install_opener(opener)

    # PRIVATE
    def _downloadImage(self, imageTag):
            imageURL = self._getFullURL(imageTag.get('src').strip().replace(' ', '%20'))
            filename = imageURL.split('/')[-1].split('?')[0]
            urllib.request.urlretrieve(imageURL, filename)
            return filename


    def _getImage(self, html):
        imageTags = self.imgSelect(html)
        self.imageFiles = []
        for imageTag in imageTags:
            if (imageTag.get('src') is not None):
                self.imageFiles.append(self._downloadImage(imageTag))
            else:
                raise IndexError()

            if (self.hasTitleText):
                self.titleText = imageTag.get('title')

    def _getTitle(self, html):
        if self.titleSelect:
            titleTag = self.titleSelect(html)[0]
            self.title = titleTag.text

    def _getNext(self, html):
        nextTag = self.nextSelect(html)
        if len(nextTag) is 0 or nextTag[0].get('href') is None:
            self.next = ""
        else:   
            self.next = self._getFullURL(nextTag[len(nextTag) - 1].get('href'))

    def _getHTML(self):
        return lxml.html.fromstring(requests.get(self.url, 
        headers={"User-agent":self.userAgent}).text)

    def _updateBaseURL(self):
        info = urlparse(self.url)
        self.baseURL = info.scheme + "://" + info.netloc
        self.basePath = os.path.dirname(self.url)
        if ('?' in self.url):
            self.noQueryURL = self.url[:self.url.index('?')]

    def _getFullURL(self, path):
        if path == "":
            return path
        elif path[0] is '/':
            return self.baseURL + path
        elif path[0] is '?':
            return self.noQueryURL + path
        elif path[:4] != "http":
            return self.basePath + '/' + path
        return path
    
    def _getChapter(self, html):
        if self.chapterElement != "":
            text = self.chapterElement(html)[0].text
            if text is not None and text != "": 
                self.chapterName = re.findall(self.chapterGet, text)[0]

    #PUBLIC

    # gets all necessary data from given URL
    def setURL(self, url):
        if url == self.url:
            self.url = ""
            return

        self.url = url
        self._updateBaseURL()
        try:   
            html = self._getHTML()
            self._getNext(html)
            self._getImage(html)
            self._getTitle(html)
            self._getChapter(html)
        except requests.exceptions.RequestException:
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
    
    # tells the comicGetter to get chapter information
    def setChapters(self, chapterElement, chapterGet):
        self.chapterElement = CSSSelector(chapterElement)
        self.chapterGet = re.compile(chapterGet)
