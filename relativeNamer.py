#Written by Chris Keeler, 2019

#Should be run as "python relativeNamer.py <pathToInputDirectory>/"

"""
Descriptive overview

Problem:
    When digitizing film negatives, the resulting image files are not properly indexed.
    This happens for two reasons:
        1. Multiple reels are scanned at the same time, so subsequent reels start above 1
        2. Multiple scans are made of the same negative, so subsequent negatives start beyond where they normally would.

Solution:
For each file within a folder:
    for each photo
        Create new name (use current conventions but with fixing indices)
        save renamed image in relative folder
"""

import glob
import os
import sys
import shutil

IMAGE_SUFFIX_REGEX = "*.JPG"
RELATIVE_SUFFIX = "_(relative)/"
MAX_FILES = 9999
INDEX_LENGTH = 4


#Takes a directory name and returns all of the image files contained within.
#
#Parameters: String; specifies the directory in which to look
#Return value: List of strings; each a filepath
def getFolderImages(_dirName):
    filesRegex = _dirName+IMAGE_SUFFIX_REGEX
    fileNames = glob.glob(filesRegex)
    return fileNames


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


#Takes a number and pads it with a sufficient number of prefixing '0's
#
#Parmeters: String
#Return value: String
def getFormattedIndex(_index):
    return "0"*(INDEX_LENGTH - len(str(_index)))+str(_index)



#Takes an image file path and removes indices and alternative flags
#
#Parameters: String
#Return value: String
def imageBaseName(_imagePath):
    imageName = os.path.basename(_imagePath)
    imageExt = os.path.splitext(_imagePath)[1]

    imageExtless = imageName[:-1*len(imageExt)]

    if alternativeTake(_imagePath):
        imageExtless = imageExtless[:-1] #cut off the alternative flag

    imageIndexless = imageExtless[:-1*INDEX_LENGTH]

    return imageIndexless



#Takes an image file, an index, and (possibly) an alternative letter, and creates a new properly formatted file name.
#
#Parameters: String, integer, and string
#Return value: String
def getFormattedName(_oldImagePath, _newIndex, _altLetter=''):
    assert(0 < len(str(_newIndex)) < 5)

    extension = os.path.splitext(_oldImagePath)[1]

    return imageBaseName(_oldImagePath) + getFormattedIndex(_newIndex) + _altLetter + extension



def main():
    #Define the output images' directory, relative to the input images' directory
    OLD_IMAGE_DIR = sys.argv[1]
    if OLD_IMAGE_DIR[-1] == '/':
        OLD_IMAGE_DIR = OLD_IMAGE_DIR[:-1]  #cut off the trailing slash
    NEW_IMAGE_DIR = OLD_IMAGE_DIR + RELATIVE_SUFFIX
    OLD_IMAGE_DIR = OLD_IMAGE_DIR + '/'     #add the slash back on now that we've defined the relative directory.
    print("Moving files from %s to %s" % (OLD_IMAGE_DIR, NEW_IMAGE_DIR))


    #Get the files to be renamed
    imagePaths = getFolderImages(OLD_IMAGE_DIR+'/')
    assert(len(imagePaths) < MAX_FILES)

    #Ensure that the output directory exists
    if not(os.path.isdir(NEW_IMAGE_DIR)):
        try: os.mkdir(NEW_IMAGE_DIR)
        except OSError:
            print("Directory does not exist, and could not create it.")
            exit()

    #Starts at 0 to account for incrementing when seeing a non-alternative (the 1st image can never be an alternative take)
    newIndex = 0

    #For each image, rename based on the new indices
    for image in imagePaths:
        flag = alternativeTake(image)

        #increment the index if this was not an alternative-take image
        if not(flag): newIndex += 1

        destination = NEW_IMAGE_DIR+getFormattedName(image, newIndex, flag)
        print("Saving %s to %s" % (str(image), str(destination)))
        shutil.copy2(image, destination)

    numOldFiles = len(glob.glob(OLD_IMAGE_DIR+'*'))
    numNewFiles = len(glob.glob(NEW_IMAGE_DIR+'*'))
    print("%d files have been copied over to %d files" % (numOldFiles, numNewFiles))

main()
