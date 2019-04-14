#Written by Chris Keeler, 2019
#Should be run as "python photoTools.py <pathToInputDirectory> {rename, pad, neg}"
    #Choosing rename will allow you to reindex properly ordered but non-sequential file names
    #Choosing pad will make each image square by padding the shorter sides
    #Choosing neg will invert each image's colour

#Current limitations:
    #Only operates on .JPGs
    #Only operates on RGB images
    #Padding does not leave images properly rotated


import glob
import os
import sys
from PIL import Image
import PIL.ImageOps

IMAGE_SUFFIX_REGEX = "*.JPG"
RENAMING_SUFFIX = "_(relative)/"
PADDING_SUFFIX = "_(padded)/"
NEGATIVE_SUFFIX = "_(negative)/"
MAX_FILES = 9999
INDEX_LENGTH = 4

VALID_COMMANDS = ["rename", "pad", "neg"]


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

    if sys.argv[2] in VALID_COMMANDS:
        #Get the files to be renamed
        imagePaths = getFolderImages(OLD_IMAGE_DIR)
        assert(len(imagePaths) < MAX_FILES)

        #Now that we have prepared everything, we can start performing the actual requested function

        #The files are in the proper order, but their file names aren't sequential
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

                #Create the new file name based off of the current index
                destination = NEW_IMAGE_DIR + getIndexUpdatedName(image, newIndex, flag)
                print("Saving %s to %s" % (str(image), str(destination)))

                imObj = Image.open(image)
                imObj.save(destination)

            informUser(OLD_IMAGE_DIR, NEW_IMAGE_DIR)

        #The files need to be squared off with padding
        elif sys.argv[2] == "pad":
            if sys.argv[3] == "black": PADDING_COLOUR = (0,0,0)
            else: PADDING_COLOUR = (255,255,255)

            #Don't capture the directory-slash before adding the relative suffix
            NEW_IMAGE_DIR = OLD_IMAGE_DIR[:-1] + PADDING_SUFFIX
            print("Padding files from %s and putting them in %s" % (OLD_IMAGE_DIR, NEW_IMAGE_DIR))
            ensureDir(NEW_IMAGE_DIR)

            for image in imagePaths:
                yAdditive = xAdditive = 0
                imObj = Image.open(image)
                oldX,oldY = imObj.size
                bigger = max(oldX,oldY)

                #Figure out how much extra should be added to each of the four sides
                if oldX > oldY: yAdditive = int((oldX - oldY)/2.0)
                elif oldY > oldX: xAdditive = int((oldY - oldX)/2.0)

                #Create a new, larger image with the requested padding colour, and then paste the original image overtop in the correct position
                newCanvas = Image.new("RGB", (bigger,bigger), PADDING_COLOUR)
                newCanvas.paste(imObj, (xAdditive, yAdditive))
                newCanvas.save(NEW_IMAGE_DIR + os.path.basename(image))

            informUser(OLD_IMAGE_DIR, NEW_IMAGE_DIR)

        #The files need to have their colours inverted
        elif sys.argv[2] == "neg":
            NEW_IMAGE_DIR = OLD_IMAGE_DIR[:-1] + NEGATIVE_SUFFIX
            print("Turning files from %s negative and putting them in %s" % (OLD_IMAGE_DIR, NEW_IMAGE_DIR))
            ensureDir(NEW_IMAGE_DIR)

            for image in imagePaths:
                imObj = Image.open(image)
                imObj = PIL.ImageOps.invert(imObj)

                imObj.save(NEW_IMAGE_DIR + os.path.basename(image))

            informUser(OLD_IMAGE_DIR, NEW_IMAGE_DIR)

        else: assert(False) #should never get here

    else:
        print("You haven't supplied a proper command argument.")
        print("Use 'python photoTools.py <directory_name> {rename, pad}'")

main()
