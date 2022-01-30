from PIL import Image
from math import floor
import PIL.ImageOps
import os

from constants import *


def renameImages(_inputImagePaths, _outputImageDir):
    #Starts at 0 to account for incrementing when seeing a non-alternative (the 1st image can never be an alternative take)
    newIndex = 0

    #For each image, rename based on the new indices
    for image in _inputImagePaths:
        flag = alternativeTake(image)

        #increment the index if this was not an alternative-take image
        if not(flag): newIndex += 1

        #Create the new file name based off of the current index
        destination = _outputImageDir + getIndexUpdatedName(image, newIndex, flag)
        print("Saving %s to %s" % (str(image), str(destination)))

        imObj = Image.open(image)
        imObj.save(destination)


def padImages(_inputImagePaths, _outputImageDir, _padColour):
    for image in _inputImagePaths:
        yAdditive = xAdditive = 0
        imObj = Image.open(image)
        oldX,oldY = imObj.size
        bigger = max(oldX,oldY)

        #Figure out how much extra should be added to each of the four sides
        if oldX > oldY: yAdditive = int((oldX - oldY)/2.0)
        elif oldY > oldX: xAdditive = int((oldY - oldX)/2.0)

        #Create a new, larger image with the requested padding colour, and then paste the original image overtop in the correct position
        newCanvas = Image.new("RGB", (bigger,bigger), _padColour)
        newCanvas.paste(imObj, (xAdditive, yAdditive))
        newCanvas.save(_outputImageDir + os.path.basename(image))


def negativeImages(_inputImagePaths, _outputImageDir):
    for image in _inputImagePaths:
        imObj = Image.open(image)
        imObj = PIL.ImageOps.invert(imObj)

        print(_outputImageDir + os.path.basename(image))
        imObj.save(_outputImageDir + os.path.basename(image))


def mergeImages(_inputImagePaths, _outputImageDir, _numRows):
    #Determine the size of the merged image
    imagesPerRow = len(_inputImagePaths)/_numRows
    canvasX,canvasY = Image.open(_inputImagePaths[0]).size
    canvasY = canvasY * _numRows

    if not(floor(imagesPerRow) == imagesPerRow):
        imagesPerRow = int(imagesPerRow)
        #if we can't split the rows up evenly, then make the first rows have the extras
        numOverfilledRowsRemaining = len(_inputImagePaths) % _numRows -1
        colCounter = -1
        canvasX = canvasX * (imagesPerRow + 1)
    else:
        #it'll be a nice, even image!
        imagesPerRow = int(imagesPerRow)
        numOverfilledRowsRemaining = 0
        colCounter = 0
        canvasX = canvasX * imagesPerRow

    newCanvas = Image.new("RGBA", (canvasX, canvasY), WHITE_COLOUR_ALPHA)

    #keep track of the position at which to paste
    currX = 0
    currY = 0
    for image in _inputImagePaths:
        imObj = Image.open(image)

        newCanvas.paste(imObj, (currX,currY))

        colCounter += 1
        if colCounter == imagesPerRow:
            if numOverfilledRowsRemaining > 0:
                #give the next row an extra image
                colCounter = -1
                numOverfilledRowsRemaining -= 1
            else:
                colCounter = 0

            #Start the next row
            currX = 0
            currY += imObj.size[1]
        else:
            currX += imObj.size[0]

    #defaults to PNG for transparency things
    newCanvas.save(_outputImageDir + "(" + str(_numRows) + "-merged)" + ".PNG")





#Takes an image path name and returns true/false as to whether or not it's an "alternative" take of another photo
#
#Parameters: String
#Return value: Either string (the alternative letter), or empty string
def alternativeTake(_imagePath):
    imageName = os.path.basename(_imagePath)
    imageExt = os.path.splitext(_imagePath)[1]
    imageExtless = imageName[:-1*len(imageExt)]
    alternative = ''

    try:
        #If we are able to cast the final character to an int, then there is no alternative-take flag.
        int(imageExtless[-1])
        #this above line functions as a cut when there is no flag

    except ValueError:
        #If we weren't able to cast this to an int, then it is an alternative take flag.
        alternative = imageExtless[-1]

    return alternative


"""
All functions that follow are used only for renameImages().
Probably a better way to factor this all, since none of the other operations utilize any helper functions.
"""

#Takes a number and pads it with a sufficient number of prefixing '0's
#
#Parameters: String
#Return value: String
def getFormattedIndex(_index):
    return "0" * (INDEX_LENGTH - len(str(_index))) + str(_index)


#Takes an image file path and removes indices and alternative flags
#
#Parameters: String
#Return value: String
def imageBaseName(_imagePath):
    imageName = os.path.basename(_imagePath)
    imageExt = os.path.splitext(_imagePath)[1]

    #cut off the extension
    imageExtless = imageName[:-1*len(imageExt)]

    #cut off the alternative flag, if it exists
    if alternativeTake(_imagePath):
        imageExtless = imageExtless[:-1]

    #cutt off the index
    imageIndexless = imageExtless[:-1*INDEX_LENGTH]

    return imageIndexless


#Takes an image file, an index, and (possibly) an alternative letter, and creates a new properly formatted file name.
#
#Parameters: String, integer, and string
#Return value: String
def getIndexUpdatedName(_oldImagePath, _newIndex, _altLetter=''):
    assert(0 < len(str(_newIndex)) < 5)
    extension = os.path.splitext(_oldImagePath)[1]
    return imageBaseName(_oldImagePath) + getFormattedIndex(_newIndex) + _altLetter + extension
