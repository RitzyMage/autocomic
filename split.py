#!/usr/bin/env python3
import matplotlib.image as img
import numpy as np
import sys
import os
from PIL import Image
import imghdr

def getChannelVariation(image, channel):
	channel =  np.copy(image[:,:,channel])

	channel.sort(axis=1)
	numOutliers = 6
	channel = channel[:,numOutliers: channel.shape[1] - numOutliers]

	deviations = np.std(channel, axis=1)
	average = np.average(channel)
	return deviations / average

def getSplitPoints(image, defaultSplit):
	marginWidth = int(len(image[0]) / 6)
	imageCenter = image[:,marginWidth:int(len(image[0]) - marginWidth),:]

	red_variation = getChannelVariation(imageCenter, 0)
	green_variation = getChannelVariation(imageCenter, 1)
	blue_variation = getChannelVariation(imageCenter, 2)

	total_variation = (red_variation + green_variation + blue_variation) / 3
	candidates = (total_variation < 0.1).nonzero()[0]
	ranges = np.split(candidates, np.where(np.diff(candidates) != 1)[0]+1)

	if len(ranges[0]) > 0:
		if ranges[0][0] == 0:
			ranges = ranges[1:]

		end = len(ranges) - 1
		if len(ranges) > 0 and image.shape[0] - ranges[end][len(ranges[end]) - 1] <= 3:
			ranges = ranges[:end]

		for i in range(len(ranges)):
			ranges[i] = int(np.average(ranges[i]))
	else:
		ranges = []
		split = defaultSplit
		while split < image.shape[1]:
			ranges.append(split)
			split += defaultSplit

	return ranges
	
def split(imageFile, defaultSplit, axis=0):
	fileExtensions = ['jpg', 'gif', 'png']
	if not any(s in imageFile for s in fileExtensions):
		imageType = imghdr.what(imageFile)
		newName = imageFile + '.' + imageType
		os.rename(imageFile, newName)
		imageFile = newName
		
	imageInit = Image.open(imageFile).convert('RGB')
	imageInit.save(imageFile)

	image = img.imread(imageFile)
	if axis is not 0:
		image = np.transpose(image, (1, 0, 2))

	lineIndexes = getSplitPoints(image, defaultSplit) 
	last = 0
	images = []
	for i in lineIndexes:
		images.append(image[last:i+1])
		last = i+1
	images.append(image[last:])

	imageNames=[]

	num = 0
	for subImage in images:
		name = "images/" + os.path.splitext(imageFile)[0] + "-" + str(num) + ".png"
		if axis is not 0:
			subImage = np.transpose(subImage, (1, 0, 2))
		img.imsave(name, subImage)
		imageNames.append(name)
		num += 1

	return imageNames