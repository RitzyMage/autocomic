
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

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
	if (isinstance(image, str)):
		image = Image.open(image)
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

	image = image.resize((newWidth, newHeight), Image.LANCZOS)
	image = remove_transparency(image, bgColor)
	newFilename = "images/" + name + "-" + str(number) + suffix + ".jpg"
	image.save(newFilename, quality=quality)

	return newFilename
