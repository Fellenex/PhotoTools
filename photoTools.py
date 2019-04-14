#Written by Chris Keeler, 2019

#Should be run as "python photoTools.py <pathToInputDirectory> {rename, pad}"

"""
Renaming:
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

Padding:
    Problem:
        When uploading to Instagram, they only accept square photos
    Solution:
        Add black borders to the shorter sides of the image to make all dimensions equal
"""

import glob
import os
import sys
import shutil
from PIL import Image

IMAGE_SUFFIX_REGEX = "*.JPG"
RENAMING_SUFFIX = "_(relative)/"
PADDING_SUFFIX = "_(padded)/"
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


#Ensures that the requested directory exists, and exits if it cannot exist for some reason.
#
#Parameters: String
#Return value: None
def ensureDir(_dirToTest):
    if not(os.path.isdir(_dirToTest)):
        try: os.mkdir(_dirToTest)
        except OSError:
            print("Directory does not exist, and could not create it.")
            exit()
        else: return


#Counts the number of files in two directories and informs the user as a human-visible soft correctness check
#
#Parameters: String, and string
#Return value: None
def informUser(_oldDirectory, _newDirectory):
    numOldFiles = len(glob.glob(_oldDirectory+'*'))
    numNewFiles = len(glob.glob(_newDirectory+'*'))
    print("%d files in %s have been copied over to %d files in %s" % (numOldFiles, _oldDirectory, numNewFiles, _newDirectory))
    return


def main():
    #Define the output images' directory, relative to the input images' directory
    OLD_IMAGE_DIR = sys.argv[1]
    if not (OLD_IMAGE_DIR[-1] == '/'):
        OLD_IMAGE_DIR += '/' #add a trailing slash if there wasn't one.

    if sys.argv[2] in ["rename", "pad"]:
        #Get the files to be renamed
        imagePaths = getFolderImages(OLD_IMAGE_DIR)
        assert(len(imagePaths) < MAX_FILES)

        #Now that we have prepared everything, we can start performing the actual requested function
        if sys.argv[2] == "rename":
            #Don't capture the directory-slash before adding the relevant suffix
            NEW_IMAGE_DIR = OLD_IMAGE_DIR[:-1] + RENAMING_SUFFIX
            print("Moving files from %s to %s" % (OLD_IMAGE_DIR, NEW_IMAGE_DIR))
            ensureDir(NEW_IMAGE_DIR)

            #Starts at 0 to account for incrementing when seeing a non-alternative (the 1st image can never be an alternative take)
            newIndex = 0

            #For each image, rename based on the new indices
            for image in imagePaths:
                flag = alternativeTake(image)

                #increment the index if this was not an alternative-take image
                if not(flag): newIndex += 1

                destination = NEW_IMAGE_DIR+getIndexUpdatedName(image, newIndex, flag)
                print("Saving %s to %s" % (str(image), str(destination)))
                shutil.copy2(image, destination)

            informUser(OLD_IMAGE_DIR, NEW_IMAGE_DIR)

        elif sys.argv[2] == "pad":
            if sys.argv[3] == "black": PADDING_COLOUR = (0,0,0)
            else: PADDING_COLOUR = (255,255,255)

            #Don't capture the directory-slash before adding the relative suffix
            NEW_IMAGE_DIR = OLD_IMAGE_DIR[:-1] + PADDING_SUFFIX
            print("Padding files from %s and putting them in %s" % (OLD_IMAGE_DIR, NEW_IMAGE_DIR))
            ensureDir(NEW_IMAGE_DIR)

            index = 1
            for image in imagePaths:
                yAdditive = xAdditive = 0
                imObj = Image.open(image)
                oldX,oldY = imObj.size
                bigger = max(oldX,oldY)

                #Figure out how much extra should be added to each of the four sides
                if oldX > oldY: yAdditive = int((oldX - oldY)/2.0)
                elif oldY > oldX: xAdditive = int((oldY - oldX)/2.0)

                newCanvas = Image.new("RGB", (bigger,bigger), PADDING_COLOUR)

                newCanvas.paste(imObj, (xAdditive, yAdditive))

                newCanvas.save(NEW_IMAGE_DIR + os.path.basename(image))

                #Image.crop() will add black boxes if the values are negative.
#                imObj = imObj.crop((0 - xAdditive, 0 - yAdditive, oldX + xAdditive, oldY + yAdditive))

                #imObj.save(NEW_IMAGE_DIR + os.path.basename(image))

            informUser(OLD_IMAGE_DIR, NEW_IMAGE_DIR)

        else: assertion(False) #should never get here

    else:
        print("You haven't supplied a proper command argument.")
        print("Use 'python photoTools.py <directory_name> {rename, pad}'")

main()
