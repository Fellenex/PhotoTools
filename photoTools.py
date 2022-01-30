#Written by Casey Keeler, 2019/2022
#Should be run as "python photoTools.py <pathToInputDirectory> {rename, pad, neg}"
    #Choosing rename will allow you to reindex properly ordered but non-sequential file names
    #Choosing pad will make each image square by padding the shorter sides
    #Choosing neg will invert each image's colour

#Current limitations:
    #Only operates on .JPGs
    #Only operates on RGB images
    #Padding does not leave images properly rotated

import glob
import os               #TODO: do we need to import it in imageOps and photoTools?
import sys
import re

#File containing the actual image operations
from imageOps import *


#Takes a directory name and returns all of the image files contained within.
#
#Parameters: String; specifies the directory in which to look
#Return value: List of strings; each a filepath
def getFolderImages(_dirName):
    fileNames = []
    for ext in IMAGE_SUFFIXES:
        print(_dirName+ext)
        print(glob.glob(_dirName+ext))
        fileNames += glob.glob(_dirName+ext)
    return fileNames


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


def informUserBeforeOperation(_inputImageDir, _outputImageDir, _commandName):
    if _commandName == RENAMING_COMMAND:
        print("Moving files from %s to %s" % (_inputImageDir, _outputImageDir))
    elif _commandName == PADDING_COMMAND:
        print("Padding files from %s and putting them in %s" % (_inputImageDir, _outputImageDir))
    elif _commandName == NEGATIVE_COMMAND:
        print("Turning files from %s negative and putting them in %s" % (_inputImageDir, _outputImageDir))
    elif _commandName == MERGE_COMMAND:
        print("Merging files from %s and putting them in %s (assumes images are the same size)" % (_inputImageDir, _outputImageDir))


#Counts the number of files in two directories and informs the user as a human-visible soft correctness check
#
#Parameters: String, and string
#Return value: None
def informUserAfterOperation(_inputImageDir, _outputImageDir, _commandName):
    numOldFiles = len(glob.glob(_inputImageDir+'*'))
    numNewFiles = len(glob.glob(_outputImageDir+'*'))
    print("%s successful: %d files in %s have been copied over to %d files in %s" % (_commandName, numOldFiles, _inputImageDir, numNewFiles, _outputImageDir))


def printHelp():
    print("You haven't supplied a proper command argument.")
    print("Use 'python photoTools.py <directory_name> {"+str(DISPLAY_COMMANDS)+"}'")



def chooseImageCommand(_inputImagePaths, _outputImageDir, _commandName, _auxilliaryArgument=None):

    print("yes")
    print(_inputImagePaths)
    print(_outputImageDir)
    print("no")

    #The files are in the proper order, but their file names aren't sequential
    if _commandName == RENAMING_COMMAND:
        renameImages(_inputImagePaths, _outputImageDir)


    #The images need to be squared off with padding
    elif _commandName == PADDING_COMMAND:
        if _auxilliaryArgument == "black":
            paddingColour = BLACK_COLOUR
        elif _auxilliaryArgument == "white":
            paddingColour = WHITE_COLOUR
        else:
            paddingColour = DEFAULT_PAD_COLOUR
        padImages(_inputImagePaths, _outputImageDir, paddingColour)


    #The images need to have their colours inverted
    elif _commandName == NEGATIVE_COMMAND:
        negativeImages(_inputImagePaths, _outputImageDir)


    #The images will be merged into one image, with a specified number of rows
    elif _commandName == MERGE_COMMAND:
        if re.search(ONLY_INTEGERS_REGEX, _auxilliaryArgument):
            numRows = int(_auxilliaryArgument)
        else:
            numRows = DEFAULT_MERGE_ROW_COUNT
        mergeImages(_inputImagePaths, _outputImageDir, numRows)

    else:
        print("Error: Incorrect command supplied")
        assert(False) #should never get here - commandName was already validated


if __name__ == "__main__":
    #Ensure the user supplied a correct command word and number of arguments
    if len(sys.argv) < 2:
        print("111")
        printHelp()

    elif not(sys.argv[2] in VALID_COMMANDS):
        print("222")
        printHelp()

    elif not(len(sys.argv) == MAP_COMMAND_TO_NUM_ARGS[sys.argv[2]]):
        print("333")
        printHelp()

    else:
        #Get the input file paths and make sure there aren't too many
        inputImageDir = sys.argv[1]

        #add a trailing slash to the input directory if one wasn't given
        if not(inputImageDir[-1] == '/'):
            inputImageDir += '/'

        #Make sure there aren't too many images to process
        inputImagePaths = getFolderImages(inputImageDir)

        print("Image paths:")
        print(inputImagePaths)

        if len(inputImagePaths) > MAX_FILES:
            print("There are %s files in %s - there can be at most %s files" % (len(inputImagePaths), inputImageDir, MAX_FILES))

        else:

            #Define the output directory based on the input directory's name
            #Don't capture the directory-slash before adding the relevant suffix
            outputImageDir = inputImageDir[:-1] + MAP_COMMAND_TO_SUFFIX[sys.argv[2]]

            #Make sure we can write to the directory
            ensureDir(outputImageDir)

            #Inform the user what is going to happen to the images
            informUserBeforeOperation(inputImageDir, outputImageDir, sys.argv[2])

            #Now that we have prepared everything, we can start performing the actual requested function
            #Send over the auxilliary argument if one is needed
            if MAP_COMMAND_TO_NUM_ARGS[sys.argv[2]] == 4:
                chooseImageCommand(inputImagePaths, outputImageDir, sys.argv[2], sys.argv[3])
            else:
                chooseImageCommand(inputImagePaths, outputImageDir, sys.argv[2])

            #Inform the user what happened to the images
            informUserAfterOperation(inputImageDir, outputImageDir, sys.argv[2])
