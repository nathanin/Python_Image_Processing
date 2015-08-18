import os
from openslide import OpenSlide, OpenSlideError, ImageSlide
from Tkinter import *
from PIL import Image, ImageTk

class ImageViewer():
	def __init__(self, root):

		pn = '/Users/nathaning/Documents/Python/Image Processing/B2 H&E 20X_001.svs'
		level = 1
		i = OpenSlide(pn) # Load an SVS file
		# dims = i.level_dimensions[level]
		# k = i.read_region((0,0), level, dims) #Extract the level 1 image as a PIL.Image Object
		k = i.get_thumbnail(size=(600, 600))

		# k.show()

		self.pi = ImageTk.PhotoImage(k)
		disp = Label(root, image=self.pi)
		disp.pack()

		print 'done'

print '\n'*10
root = Tk()
new = Toplevel()
IV = ImageViewer(new)
root.mainloop()

# read_region(self, location, level, size) method of openslide.OpenSlide instance
#     Return a PIL.Image containing the contents of the region.
    
#     location: (x, y) tuple giving the top left pixel in the level 0
#               reference frame.
#     level:    the level number.
#     size:     (width, height) tuple giving the region size.
    
#     Unlike in the C interface, the image data returned by this
#     function is not premultiplied.


# save(self, fp, format=None, **params) method of PIL.Image.Image instance
#     Saves this image under the given filename.  If no format is
#     specified, the format to use is determined from the filename
#     extension, if possible.