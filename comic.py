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
	firstURL = info["firstURL"]

	height = info.get("optionalHeight")
	width = info.get("optionalWidth")
	jpgQuality = info.get("jpgQuality")

pdf = pdfWriter(name, author, pageColor, textColor, height, width, jpgQuality)
comic = comicGetter(info)

comic.setURLifUnset(firstURL)

try:
	while comic.validURL() and not killed:
		pdf.addComic(comic)
		comic.save()
		pdf.save()

		print("\n")
		print(pdf.comicNumber + 1)
		print("****\t****\t****")
		comic.advance()
except RuntimeError:
	print("Warning: pressing ^C when running javascript could have unintended consequences")
	
if not killed:
	print("finishing")

pdf.finish()