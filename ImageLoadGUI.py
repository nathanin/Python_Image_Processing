'''
GUI interface for extracting any level of image from an SVS file as a new TIFF.
Uses OpenSlide library to extract and decode the image stack.
Tkinter for GUI operations.

Code Quality:
http://xkcd.com/1513/
,
'''

import os
from openslide import OpenSlide, OpenSlideError
from Tkinter import *
import tkFileDialog
import string
import math
from PIL import Image, ImageTk
import matplotlib as mpl
import numpy as np

## ??????????? ##
# class imgOutOfBoundsError(Exception.exception):
#     pass

class ImageRepack():

#### FUNCTIONS ####
    def __init__(self, parent):
        self.parent = parent
        self.CI = None

        # Buttons:
        self.buttonPallet = Frame(parent).grid(row=2, column=1)
        self.New = Button(self.buttonPallet,
            command = self.buttonNew)
        self.New.configure(text='New Image')
        self.New.grid(row=4, column=1)
        self.Crop = Button(self.buttonPallet,
            command = self.buttonCrop)
        self.Crop.configure(text='Crop')
        self.Crop.grid(row=4, column=2)
        self.Close = Button(self.buttonPallet,
            command = lambda
            arg1=self.parent:
            self.buttonClose(arg1))
        self.Close.configure(text='Close')
        self.Close.grid(row=4, column=4)

        # Text Boxes:
        self.textPallet = Frame(parent).grid(row=1, column=1)
        self.formatlabel = Label(self.textPallet, text='Format')
        self.formatlabel.grid(row=2, column=1, sticky=W)
        self.format = Text(self.textPallet,
            height=15, width=20, bg='Aquamarine')
        self.format.config(state=DISABLED)
        self.format.grid(row=3, column=1)

        self.formatlabel = Label(self.textPallet, text='Levels')
        self.formatlabel.grid(row=2, column=2, sticky=W)
        self.levels = Text(self.textPallet,
            height=15, width=20, bg='NavajoWhite')
        self.levels.config(state=DISABLED)
        self.levels.grid(row=3, column=2)

        self.formatlabel = Label(self.textPallet, text='Dimensions')
        self.formatlabel.grid(row=2, column=3, sticky=W)
        self.dimensions = Text(self.textPallet,
            height=15, width=20, bg='LightSteelBlue')
        self.dimensions.config(state=DISABLED)
        self.dimensions.grid(row=3, column=3)

        self.filenamebox = Entry(self.textPallet, bg='Linen')
        self.filenamebox.grid(row=1,column=1,columnspan=4,sticky=W+E)

    def buttonNew(self):
        
        pathname = tkFileDialog.askopenfilename()

        self.CI = SVSImage(pathname)

        if self.CI.success:
            self.showMeta()
            self.CI.showPreview()
        else:
            print "Failed to load image."

    def showMeta(self):
        # Populate the text fields
        nLevels = self.CI.metadata['levels']

        self.format.config(state=NORMAL)
        self.levels.config(state=NORMAL)
        self.dimensions.config(state=NORMAL)

        self.format.delete('1.0',END)
        self.levels.delete('1.0',END)
        self.dimensions.delete('1.0',END)

        self.format.insert(END, self.CI.metadata['format'])
        for n in range(0,nLevels):
            self.levels.insert(END, str(n)+'\n\n')
            self.dimensions.insert(END,
                str(self.CI.metadata['dimensions'][n])+'\n\n')
        
        self.filenamebox.delete(0, END)
        self.filenamebox.insert(INSERT, self.CI.pn)
        self.filenamebox.xview_moveto(0.5)
        self.filenamebox.icursor(END)

        self.format.config(state=DISABLED)
        self.levels.config(state=DISABLED)
        self.dimensions.config(state=DISABLED)

    def buttonCrop(self):
        # Check all settings and selections for validity.
        ''' 
        - Compare the file path and basename in the entry box against the
        original. They must be different.
        - Check any custom ROI boundaries for validity
        - LATER: Check if output file exits and suggest a solution

        - Create a new UI box with (2), (2), (1), (1) entry widgets
        '''
        try:
            self.CI.active = True
            fp = self.filenamebox.get()
            sfD = Toplevel()
            frame1 = Frame(sfD)

            (fpBase, finame) = os.path.split(fp)
            finame = finame[0:len(finame)-4]+'.tif'
            xcl = Label(frame1, text='Top X:').grid(row=1, column=1, sticky=E)
            self.xcorner = Entry(frame1, bg='Linen')
            self.xcorner.bind('<Return>', self.updatePVBox)
            self.xcorner.bind('<KP_Enter>', self.updatePVBox)
            self.xcorner.insert(END, 0)
            self.xcorner.grid(row=1, column=2)
            ycl = Label(frame1, text='Top Y:').grid(row=2, column=1, sticky=E)
            self.ycorner = Entry(frame1)
            self.ycorner.bind('<Return>', self.updatePVBox)
            self.ycorner.bind('<KP_Enter>', self.updatePVBox)
            self.ycorner.insert(END, 0)
            self.ycorner.grid(row=2, column=2)

            xsl = Label(frame1, text='X size:').grid(row=3, column=1)
            self.xsize = Entry(frame1)
            self.xsize.bind('<Return>', self.updatePVBox)
            self.xsize.bind('<KP_Enter>', self.updatePVBox)
            self.xsize.insert(END, 1200)
            self.xsize.grid(row=3, column=2)
            ysl = Label(frame1, text='Y size:').grid(row=4, column=1)
            self.ysize = Entry(frame1)
            self.ysize.bind('<Return>', self.updatePVBox)
            self.ysize.bind('<KP_Enter>', self.updatePVBox)
            self.ysize.insert(END, 1200)
            self.ysize.grid(row=4, column=2)

            lvl = Label(frame1, text='Level:').grid(row=5, column=1)
            self.level = Entry(frame1)
            self.level.bind('<Return>', self.scaleBoxSize)
            self.level.bind('<KP_Enter>', self.scaleBoxSize)
            self.level.insert(END, 0)
            self.level.grid(row=5, column=2)

            nfnl = Label(frame1, text='Out name:').grid(row=6, column=1)
            self.nfn = Entry(frame1)
            self.nfn.grid(row=6, column=2)
            self.nfn.insert(END, finame)

            self.CI.cropPropPane = [self.xcorner, self.ycorner, self.xsize, self.ysize, self.level, self.nfn]

            # Lets you control output folder from the "main" window
            (fpBase, temp) = os.path.split(self.filenamebox.get())

            buttonOK = Button(frame1, text='OK',
                command = self.buttonCropOK)
            buttonOK.grid(row=7, column=1)
            buttonClose2 = Button(frame1, text='Done',
                command = lambda
                arg1 = sfD:
                self.buttonClose(arg1))
            buttonClose2.grid(row=7, column=3)

            frame1.pack()
        except AttributeError:
            print "Open an image first"


    def updatePVBox(self, event):
        properties = self.pullCropSets()
        if self.allLegal(properties):

            targetLvl = int(self.level.get()) 
            factor = self.CI.metadata['downsamples'][targetLvl]

            # w.r.t. Level0:
            rawx1 = int(self.xcorner.get())
            rawy1 = int(self.ycorner.get())
            rawx2 = rawx1+(int(self.xsize.get())*factor)
            rawy2 = rawy1+(int(self.ysize.get())*factor)

            print 'raw: ', rawx1, rawy1, rawx2, rawy2, ' fact:', factor

            # w.r.t. Preview level & scale
            x1 = int(rawx1/self.CI.dispLvlfact)
            y1 = int(rawy1/self.CI.dispLvlfact)
            x2 = int(rawx2/self.CI.dispLvlfact)
            y2 = int(rawy2/self.CI.dispLvlfact)

            print 'disp: ', x1, y1, x2, y2, 'scl:', self.CI.dispLvlfact

            self.CI.canvas.delete(self.CI.activebox)
            B = self.CI.canvas.create_rectangle(x1,y1,x2,y2)
            self.CI.activebox = B

            self.writeProps(properties)

    def scaleBoxSize(self, event):
        try:
            newlvl = int(self.level.get())
            oldlvl = self.CI.cropProps['lvl']
            old = self.CI.SVS.level_downsamples[oldlvl]
            new = self.CI.SVS.level_downsamples[newlvl]

            factor = old/new

            print 'old:', oldlvl, ' new:', newlvl, ' old fact:', old,' fact:', new

            oldx = int(self.xsize.get())
            oldy = int(self.ysize.get())

            print 'oldx:', oldx, ' oldy', oldy

            scx = int(math.floor(oldx*factor))
            scy = int(math.floor(oldy*factor))

            print 'scaledx:', scx, ' scaledy:', scy

            self.xsize.delete(0,END)
            self.xsize.insert(END, scx)
            self.ysize.delete(0,END)
            self.ysize.insert(END, scy)

            properties = self.pullCropSets() #Now cropProps are up-to-date and we can use them.
            if self.allLegal(properties):
                self.writeProps(properties)
        except KeyError:
            print 'New Level out of bounds.'

    def pullCropSets(self):
        '''
        Populate a dictionary with crop box, new level, 
        and filename from the Entry boxes
        '''
        (fpBase, temp) = os.path.split(self.filenamebox.get())

        xcotemp = int(self.xcorner.get())
        ycotemp = int(self.ycorner.get())
        xstemp = int(self.xsize.get())
        ystemp = int(self.ysize.get())
        lvltemp = int(self.level.get())

        ## now "writeProps" function
        # self.CI.cropProps['xco'] = int(self.xcorner.get())
        # self.CI.cropProps['yco'] = int(self.ycorner.get())
        # self.CI.cropProps['xs'] = int(self.xsize.get())
        # self.CI.cropProps['ys'] = int(self.ysize.get())
        # self.CI.cropProps['lvl'] = int(self.level.get())

        outname = self.nfn.get()
        fptemp = fpBase+os.sep+outname

        return {'xco': xcotemp,
            'yco': ycotemp,
            'xs': xstemp,
            'ys': ystemp,
            'lvl': lvltemp,
            'fp': fptemp}

    def allLegal(self, properties):
        '''
        To be executed before writing to cropProps.
        '''
        imgprops = self.CI.metadata
        cp = properties

        # pull the level. two-tuple (x,y)
        lv0dims = imgprops['dimensions'][0]
        imgdims = imgprops['dimensions'][cp['lvl']]
        if cp['xco'] < 0 or cp['xco'] > lv0dims[0]:
            print 'x out of bounds'
            return False
        if cp['yco'] < 0 or cp['yco'] > lv0dims[1]:
            print 'y out of bounds'
            return False
        if cp['xs']-cp['xco'] > imgdims[0]:
            print 'x size too large'
            return False
        if cp['ys']-cp['yco'] > imgdims[1]:
            print 'y size too large'
            return False
        if cp['fp']==self.CI.pn: # There's a better way to compare str
            print 'Invalid file name.'
            return False

        return True # default to true...? good idea?

    def writeProps(self, properties):
        self.CI.cropProps['xco'] = properties['xco']
        self.CI.cropProps['yco'] = properties['yco']
        self.CI.cropProps['xs'] = properties['xs']
        self.CI.cropProps['ys'] = properties['ys']
        self.CI.cropProps['lvl'] = properties['lvl']
        self.CI.cropProps['fp'] = properties['fp']

    def buttonCropOK(self):
        properties = self.pullCropSets()
        if self.allLegal(properties):
            self.writeProps(properties)
            self.SaveImg()
            print 'Section saved ', self.CI.cropProps['fp']

    def buttonClose(self, target):
        self.CI.canvas.delete(self.CI.activebox)
        target.destroy()

    def SaveImg(self):
        # Save the image
        #temp:
        corner = (self.CI.cropProps['xco'], 
            self.CI.cropProps['yco'])
        size = (self.CI.cropProps['xs'], 
            self.CI.cropProps['ys'])
        fp = self.CI.cropProps['fp']
        level = self.CI.cropProps['lvl']

        print 'Cropping...'
        print 'From Level ', level
        print corner, ' to ', size
        print 'Destination: \n', fp
        out = self.CI.SVS.read_region(corner, level, size)
        out.save(fp)

'''
Child class to the OpenSlide object, which has methods for reading and parsing information from SVS images.
Includes attributes:
    metadata
    cropProps - a Dictionary holding the active settings for a crop
    active - Boolean indicating if this instance is active and interfacing to the crop diologue window.
    pvScale - Integer to downsample the lowest level image for preview
    etc.
'''
class SVSImage(OpenSlide):
# Holds an OpenSlide object, with image properties in a dictionary
    def __init__(self, pn):
        self.metadata = {}
        self.cropProps = {'xco':0, 'yco':0, 'xs':0, 'ys':0, 'lvl':0, 'fp':''}
        self.active = False
        self.pvScale = 3
        self.cropPropPane = None

        self.activebox = 0

        self.pn = pn
        self.fn = os.path.basename(self.pn)

        self.preview = Toplevel()

        try:
            self.SVS = OpenSlide(pn)
            self.success = True
        except OpenSlideError:
            print 'Caught file type exception!'
            self.preview.destroy()
            self.success = False
        else:
            self.metadata['format'] = self.SVS.detect_format(pn)
            self.metadata['levels'] = self.SVS.level_count
            self.metadata['dimensions'] = self.SVS.level_dimensions
            self.metadata['downsamples'] = self.SVS.level_downsamples
            self.dispLvlfact = self.SVS.level_downsamples[self.SVS.level_count-1]*self.pvScale

    def showPreview(self):
        # Create a new window, draw on it the lowest level image, scaled down
        self.dispLvl = self.metadata['levels'] - 1
        (x,y) = self.metadata['dimensions'][self.dispLvl]
        xx = int(math.floor(x/self.pvScale))
        yy = int(math.floor(y/self.pvScale))

        i = self.SVS.read_region((0,0), self.dispLvl, (x,y)).resize((xx,yy))
        self.preview.title(self.fn+' Level '+str(self.dispLvl))
        self.canvas = Canvas(self.preview, width=xx, height=yy)
        self.canvas.pack()

        # self.PVImage = self.canvas.create_image(0,0)
        self.canvas.bind("<ButtonPress-1>", self.clickPress)
        self.canvas.bind("<B1-Motion>", self.clickMotion)
        self.canvas.bind("<ButtonRelease-1>", self.clickRelease)
        self.canvas.myIm = ImageTk.PhotoImage(i)
        self.PVImage = self.canvas.create_image(xx/2,yy/2, image=self.canvas.myIm)
        # self.PVImage.config(image=self.canvas.myIm)
        # self.PVImage.pack(fill=BOTH)

    def clickPress(self, event):
        if self.active:
            self.x0 = event.x
            self.y0 = event.y
        else:
            print 'not active ', event.x, event.y

    def clickMotion(self, event):
        # Use this function to live draw the selection rectangle Not needed now.
        ''' 
        Must un-draw any existing rectangle before drawing the next one.
        '''
        if self.active:
            # box = self.getBox(event.x-self.x0, event.y-self.y0, scaled=False)
            # print box
            dx = event.x-self.x0
            dy = event.y-self.y0
            # box = (self.x0, self.y0, self.x0+dx, self.y0+dy)
            # print box
            self.canvas.delete(self.activebox)
            self.activebox = self.canvas.create_rectangle(self.x0, self.y0, self.x0+dx, self.y0+dy)

    def clickRelease(self,event):
        '''Use this function to update the Entry widgets showing x and y 
        for the upper corner and x and y size. Here check if the mouse has
        passed the image boundary, and also scale the pixels to the proper 
        scale pulled from the Level entry widget, and using the property
        (self.level_downsamples).'''

        if self.active:
            self.xf = event.x
            self.yf = event.y
            dx = self.xf - self.x0
            dy = self.yf - self.y0

            boundingbox = self.getBox(dx, dy)
            self.cropPropPane[0].delete(0,END)
            self.cropPropPane[0].insert(INSERT, boundingbox[0])
            self.cropPropPane[1].delete(0,END)
            self.cropPropPane[1].insert(INSERT, boundingbox[1])
            self.cropPropPane[2].delete(0,END)
            self.cropPropPane[2].insert(INSERT, boundingbox[2])
            self.cropPropPane[3].delete(0,END)
            self.cropPropPane[3].insert(INSERT, boundingbox[3])
        else:
            print 'not active ', event.x, event.y

    def getBox(self, dx, dy):
        '''1=TOP-LEFT to BOTTOM-RIGHT
           2=BOTTOM-LEFT to TOP-RIGHT
           3=TOP-RIGHT to BOTTOM-LEFT
           4=BOTTOM-RIGHT to TOP-LEFT
        Also handle if dx and/or dy = 0, which is a line

        Here, do the scaling to whatever the selected level is.
        The top-left corner is always in the Level0 reference scale.
        Returns a box: [x, y, height, width]

        Input scaled: return scaled or un-scaled box.
        '''
        targetLvl = int(self.cropProps['lvl'])
        cornerfactor = int(self.SVS.level_downsamples[self.dispLvl]*self.pvScale)
        factor = int(cornerfactor/self.SVS.level_downsamples[targetLvl])
        # print 'dx:', dx, ' dy:', dy, ' target:', targetLvl, ' scale:', factor,' cornerscale:', cornerfactor
        if dx>0 and dy>0: #1
            result = [self.x0, self.y0, dx, dy]
        elif dx>0 and dy<0: #2
            result = [self.x0, self.y0+dy, dx, -1*dy]
        elif dx<0 and dy>0: #3
            result = [self.x0+dx, self.y0, -1*dx, dy]
        elif dx<0 and dy<0: #4
            result = [self.x0+dx, self.y0+dy, -1*dx, -1*dy]
        elif 0 in (dx,dy):
            return [0, 0, 0, 0]

        for i in range(0,2):
            result[i] = int(math.floor(result[i]*cornerfactor))
        for i in range(2,4):
            result[i] = int(math.floor(result[i]*factor))
        return result

    def killPreview(self):
        self.preview.destroy()



class messageBox():

    def __init__(self):
        self.window = Toplevel()
        pass

    def killWindow(self):
        self.window.destroy()


class ImageAnalyzer():
    '''
    WHWHHHHHAAAATTTT?????
    '''
    def __init__(self):

        pass

print '\n'*5
root = Tk()
root.wm_title('SVS Repack GUI')
IV = ImageRepack(root)
root.mainloop()