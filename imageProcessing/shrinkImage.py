def getResizedDims(width, image):
	percentSmaller = min(width / float(image.size[0]), 1)
	newHeight = max(int(image.size[1] * percentSmaller), 1)
	newWidth = max(int(image.size[0] * percentSmaller), 1)
	return newWidth, newHeight

def getImageDims(filename):
	image = Image.open(filename)
	return image.size

def shrinkImage(filename, width, name, number, bgColor, quality, suffix=""):
	image = Image.open(filename)

	newWidth, newHeight = getResizedDims(width, image) 

	image = image.resize((newWidth, newHeight), Image.ANTIALIAS)
	image = remove_transparency(image, bgColor)
	newFilename = "images/" + name + "-" + str(number) + suffix + ".jpg"
	image.save(newFilename, quality=quality)

	return newFilename