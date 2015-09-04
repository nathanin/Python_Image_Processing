#!/Users/IngN/AppData/Local/Continuum/Anaconda/python

# Color Deconvolution from 3-channel - to - 3-channel images
# Original MATLAB code by Zhaoxuan.Ma@cshs.org
#
# Reference: Ruifrok, A.C., et al. "Quantification of histochemical staining by color deconvolution"

import numpy as np
from skimage import io
import math as m


def initializeMatrices():
    MODx = np.array([0.644211, 0.092789, 0.6359544])
    MODy = np.array([0.716556, 0.954111, 0.0010])
    MODz = np.array([0.266844, 0.283111, 0.7717266])

    cosx = np.array([0,0,0])
    cosy = np.array([0,0,0])
    cosz = np.array([0,0,0])
    l = np.array([0,0,0])

    for i in (0,1,2):
    	cosx[i] = 0
    	cosy[i] = 0
    	cosz[i] = 0
    	l[i] = m.sqrt( MODx[i]**2 + MODy[i]**2 + MODz[i]**2 )
    	if l[i] != 0.0:
    		cosx[i] = MODx[i]/l[i]
    		cosy[i] = MODy[i]/l[i]
    		cosz[i] = MODz[i]/l[i]

	if cosx[1]+cosy[1]+cosy[1] == 0:
		cosx[1] = cosz[1]
		cosy[1] = cosx[1]
		cosz[1] = cosy[1]

	if cosx[2]+cosy[2]+cosy[2] == 0:
		if cosx[0]**2 + cosx[1]**2 > 1:
			cosx[2] = 0
		else:
			cosx[2] = m.sqrt(1.0 - (cosx[0]**2 - cosx[1]**2))

		if cosy[0]**2 + cosy[1]**2 > 1:
			cosy[2] = 0
		else:
			cosy[2] = m.sqrt(1.0 - (cosy[0]**2 - cosy[1]**2))

		if cosz[0]**2 + cosz[1]**2 > 1:
			cosz[2] = 0
		else:
			cosz[2] = m.sqrt(1.0 - (cosz[0]**2 - cosz[1]**2))

	leng = m.sqrt(cosx[2]**2 + cosy[2]**2 + cosz[2]**2)

	cosx[2] /= leng
	cosy[2] /= leng
	cosz[2] /= leng

	for i in (0,1,2):
		if cosx[i] == 0:
			cosx[i] = 0.001
		if cosy[i] == 0:
			cosy[i] = 0.001
		if cosz[i] == 0:
			cosz[i] = 0.001

	q = np.zeros(9)
	A <- cosy[1] - cosx[1] * cosy[0] / cosx[0]
	V <- cosz[1] - cosx[1] * cosz[0] / cosx[0]
	C <- cosz[2] - cosy[2] * V/A + cosx[2] * (V/A * cosy[0]/cosx[0] - cosz[0]/cosx[0])
	q[2] <- (-cosx[2] / cosx[0] - cosx[2] / A * cosx[1] / cosx[0] * cosy[0] / cosx[0] + cosy[2] / A * cosx[1] / cosx[0]) / C
	q[1] <- -q[2] * V / A - cosx[1] / (cosx[0] * A)
	q[0] <- 1 / cosx[0] - q[1] * cosy[0] / cosx[0] - q[2] * cosz[0] / cosx[0]
	q[5] <- (-cosy[2] / A + cosx[2] / A * cosy[0] / cosx[0]) / C
	q[4] <- -q[5] * V / A + 1 / A
	q[3] <- -q[4] * cosy[0] / cosx[0] - q[5] * cosz[0] / cosx[0]
	q[8] <- 1 / C
	q[7] <- -q[8] * V / A
	q[6] <- -q[7] * cosy[0] / cosx[0] - q[8] * cosz[0] / cosx[0]

	return q


def transformation(image, q):
	imagesize = image.shape
	newpixels = np.zeros(imagesize)

	Rlog = -((255.0*m.log(image[1,:,:]+1)/255.0)/m.log(255.0))
	Glog = -((255.0*m.log(image[2,:,:]+1)/255.0)/m.log(255.0))
	Blog = -((255.0*m.log(image[3,:,:]+1)/255.0)/m.log(255.0))

	for i in (0,1,2):
		Rscaled = Rlog*q[(i-1)*3+1]
		Gscaled = Glog*q[(i-1)*3+2]
		Bscaled = Blog*q[i*3]

		output = m.exp(-((Rscaled+Gscaled+Bscaled)-255)*m.log(255)/255)
		output [output > 255] = 255

		newpixels[i,:,:] = floor(output+0.5)

	return newpixels

def colorDeconvolution(image):
   	q = initializeMatrices()
   	decon = transformation(image, q)


if __name__ == '__main__':
	# filepath = raw_input('File: ')
	filepath = 'D:/Nathan/test2.tif'
	# filepath_out = raw_input("save name: ")
	filepath_out = 'D:/Nathan/test2d.tif'
	image = io.imread(filepath)
	n = colorDeconvolution(image)
	io.imsave(filepath_out, n)