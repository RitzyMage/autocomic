#!/usr/bin/env python3
from comicGetter import comicGetter
from pdfWriter import pdfWriter
import json
import yaml
import signal
import os.path

# so that if ^C is pressed, the script can clean up
killed = False
def signalHandler(signum, frame):
	global killed
	if killed:
		exit()
	print('stopped; cleaning up...')
	killed = True
signal.signal(signal.SIGINT, signalHandler)

filename = 'comic.json' if os.path.isfile('comic.json') else 'comic.yml'
with open(filename, 'r') as file:
	info = json.load(file) if filename == 'comic.json' else yaml.safe_load(file)
	name = info["name"]
	author = info["author"]
	pageColor = info["pageColor"]
	textColor = info["textColor"]
	comicSelect = info["comicSelect"]
	titleSelect = info["titleSelect"]
	mouseover = info["mouseover"]
	nextSelect = info["nextSelect"]
	firstURL = info["firstURL"]
	chapters = info["chapters"]

	chapterElement = info["chapterElement"]
	chapterRegex = info["chapterRegex"]
	height = info.get("optionalHeight")
	width = info.get("optionalWidth")
	jpgQuality = info.get("jpgQuality")
	useCss = info.get("useCSS")

pdf = pdfWriter(name, author, pageColor, textColor, height, width, jpgQuality)
comic = comicGetter(comicSelect, titleSelect, mouseover, nextSelect, useCss)

if chapters:
	comic.setChapters(chapterElement, chapterRegex)

comic.setURLorPast(firstURL)

while comic.validURL() and not killed:
	print("getting comic", pdf.comicNumber + 1)
	pdf.addComic(comic)
	comic.save()
	pdf.save()
	comic.advance()

pdf.finish()