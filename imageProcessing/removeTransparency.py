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