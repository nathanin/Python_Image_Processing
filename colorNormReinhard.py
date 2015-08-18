''' 
Python implementation Reinhard's method for
H&E normalization.. 
'''
import matplotlib
import numpy as np
import numpy.ma as ma
from skimage import io, color
import skimage as ski
import math

def bcg_func(image):
    image2 = ski.img_as_uint(color.rgb2gray(image))

    bcg = image2>55275
    
    return bcg

def customRGB2LAB(image):
#     print 'From RGB 2 LAB:'
    # Vectorize
    imgV = np.transpose(np.reshape(image, (image.shape[0]*image.shape[1], 3)))
    
    # Transform matrix:
    rgb2LMS = np.array(([0.3811, 0.5783, 0.0404], 
        [0.1967, 0.7244, 0.0782], 
        [0.0241, 0.1288, 0.8444]))

    LMS = np.dot(rgb2LMS, imgV)

    lms2LAB1 = np.array(([1/math.sqrt(3), 0, 0], 
        [0, 1/math.sqrt(6), 0], 
        [0, 0, 1/math.sqrt(2)]))
    lms2LAB2 = np.array(([1, 1, 1], 
        [1, 1, -2], 
        [1, -1, 0]))

    lms2LAB = np.dot(lms2LAB1, lms2LAB2)
    LABV = np.dot(lms2LAB, LMS)

    LAB = np.reshape(np.transpose(LABV), (image.shape[0], image.shape[1], 3))
    return LAB

def customLAB2RGB(image):
    
    M = image.shape[0]
    N = image.shape[1]
    
    lab2LMS1 = np.array(([1, 1, 1], [1, 1, -1], [1, -2, 0]))
    lab2LMS2 = np.array(([1/math.sqrt(3), 0, 0], 
        [0, 1/math.sqrt(6), 0], 
        [0, 0, 1/math.sqrt(2)]))
    lab2LMS = np.dot(lab2LMS1, lab2LMS2)
    
    labV = np.transpose(np.reshape(image, (M*N, 3)))
    LMSV = np.dot(lab2LMS, labV)
    
    lms2rgb = np.array(([4.4679, -3.5873, 0.1193], 
        [-1.2186, 2.3809, -0.1624], 
        [0.0497, -0.2439, 1.2045]))
    RGBV = np.dot(lms2rgb, LMSV)
    
    RGB = np.reshape(np.transpose(RGBV), (M, N, 3))
    return RGB

def colorNormReinhard(image):
    #Takes image as a float64 values in range [0,1]
    
    mst = np.array(([77.5121, 270.5718], [8.9287, -23.6535], [2.9664, 8.3857]))
    M = image.shape[0]
    N = image.shape[1]
    
    lab = customRGB2LAB(image)
    bcg = bcg_func(image)
    bcg_inverse = (bcg-1)*-1
    
    bcgvect = np.reshape(bcg, (M*N))
    bcgv_i = np.reshape(bcg_inverse, (M*N))
    labvect = np.transpose(np.reshape(lab, (M*N,3)))
    
    labL = ma.MaskedArray(labvect[0,:], mask=bcgvect)
    labA = ma.MaskedArray(labvect[1,:], mask=bcgvect)
    labB = ma.MaskedArray(labvect[2,:], mask=bcgvect)
    
#     labL_inv = ma.MaskedArray(labvect[0,:], mask=bcgv_i)
#     labA_inv = ma.MaskedArray(labvect[1,:], mask=bcgv_i)
#     labB_inv = ma.MaskedArray(labvect[2,:], mask=bcgv_i)

    labLm = labL.mean()
    labAm = labA.mean()
    labBm = labB.mean()
    
    labLs = labL.std()
    labAs = labA.std()
    labBs = labB.std()

    labLn = ((labvect[0,:]-labLm)/labLs)*mst[0,0]+mst[0,1]
    labAn = ((labvect[1,:]-labAm)/labAs)*mst[1,0]+mst[1,1]
    labBn = ((labvect[2,:]-labBm)/labBs)*mst[2,0]+mst[2,1]
    
    labL = np.multiply(labLn, bcgv_i)/255 + np.multiply(labL, bcgvect)
    labA = np.multiply(labAn, bcgv_i)/255 + np.multiply(labA, bcgvect)
    labB = np.multiply(labBn, bcgv_i)/255 + np.multiply(labB, bcgvect)
    
#     labL = ((labL-labLm)/labLs)*mst[0,0]+mst[0,1]
#     labA = ((labA-labAm)/labAs)*mst[1,0]+mst[1,1]
#     labB = ((labB-labBm)/labBs)*mst[2,0]+mst[2,1]
    
    labnorm = np.array((labL, labA, labB))
    
    labnorm = np.reshape(np.transpose(labnorm), (M, N, 3))
    rgbnorm = customLAB2RGB(labnorm)
    return rgbnorm


def NR_main():
    filepath = raw_input('File: ')
    image = io.imread(filepath)

    n = colorNormReinhard(image)
    filepath_out = raw_input("save name: ")
    io.imsave(filepath_out, n)

NR_main()


