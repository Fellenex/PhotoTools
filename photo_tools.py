"""A small collection of tools for batch processing image files.
Written by Casey Keeler, 2019/2022

Should be run as
    "python photo_tools.py <pathToInputDirectory> {rename, pad, neg, merge} [extra_arg]"
    -
    rename will allow you to reindex properly ordered but non-sequential file names
    pad will make each image square by padding the shorter sides
    neg will invert each image's colour
    merge will concatenate all of the images together into a grid


Current limitations
    Only operates on .JPGs/.PNGs
    RGB vs RGBA images
    Renaming incorrectly rotates vertical images
    Padding incorrectly rotates vertical images
"""

import glob
import sys
import re
import os

from constants import *

#File containing the actual image operations
from image_ops import rename_images, pad_images, negative_images, merge_images


#Takes a directory name and returns all of the image files contained within.
#
#Parameters: String; specifies the directory in which to look
#Return value: List of strings; each a filepath
def get_folder_images(_dir_name : str) -> list[str]:
    """
    Takes a directory name and returns a list of strings for all of the allowable
        (as defined by IMAGE_SUFFIXES) image files contained within.
    """
    file_names = []
    for ext in IMAGE_SUFFIXES:
        file_names += glob.glob(_dir_name+ext)
    return file_names


def ensure_dir(_dir_to_test : str) -> bool:
    """
    Ensures that either _dir_to_test is already a directory, or that it can be created.
    Exits from the program if it does not exist and cannot be created.
    """
    if not os.path.isdir(_dir_to_test):
        try:
            os.mkdir(_dir_to_test)
        except OSError:
            sys.exit("Directory does not exist, and could not create it.")

    return True


def inform_user_before_operation(_input_image_dir : str, _output_image_dir : str, \
    _command_name : str) -> None:
    """
    Informs the user what operation they have chosen, based on _command_name, and
        gives them a little extra information about what is going to happen.
    """
    if _command_name == RENAMING_COMMAND:
        print(f"Moving files from {_input_image_dir} to {_output_image_dir}")
    elif _command_name == PADDING_COMMAND:
        print(f"Padding files from {_input_image_dir} and "
            f"putting them in {_output_image_dir}")
    elif _command_name == NEGATIVE_COMMAND:
        print(f"Turning files from {_input_image_dir} negative and "
            f"putting them in {_output_image_dir}")
    elif _command_name == MERGE_COMMAND:
        print(f"Merging files from {_input_image_dir} and "
            f"putting them in {_output_image_dir} (assumes images are the same size)")


def get_num_files_in_directory(_directory : str) -> int:
    """
    Takes a directory path and returns an integer indicating how many files are therein contained.
    """
    return len(glob.glob(_directory+'*'))


def inform_user_after_operation(_input_image_dir : str, _output_image_dir : str, \
    _command_name : str, _num_previous_files) -> None:
    """
    Informs the user about the success of their operation, and details how many
        files were created as a result of their operation request.
    Takes into account any files that were previously in the output directory.
    """
    num_old_files = get_num_files_in_directory(_input_image_dir)
    num_new_files = get_num_files_in_directory(_output_image_dir) - _num_previous_files
    print(f"{_command_name} successful: {num_old_files} files in {_input_image_dir} "
        f"have been copied over to {num_new_files} files in {_output_image_dir}")


def choose_image_command(_input_image_paths : list[str], _output_image_dir : str, \
    _command_name : str, _auxilliary_argument : Optional[str] = None) -> None:
    """
    The "switch-case" for all possible image commands.
    Error-handling should have been performed before this function was called.
    """

    #The files are in the proper order, but their file names aren't sequential
    if _command_name == RENAMING_COMMAND:
        rename_images(_input_image_paths, _output_image_dir)

    #The images need to be squared off with padding
    elif _command_name == PADDING_COMMAND:
        if _auxilliary_argument == "black":
            padding_colour = BLACK_COLOUR
        elif _auxilliary_argument == "white":
            padding_colour = WHITE_COLOUR
        else:
            padding_colour = DEFAULT_PAD_COLOUR
        pad_images(_input_image_paths, _output_image_dir, padding_colour)


    #The images need to have their colours inverted
    elif _command_name == NEGATIVE_COMMAND:
        negative_images(_input_image_paths, _output_image_dir)


    #The images will be merged into one image, with a specified number of rows
    elif _command_name == MERGE_COMMAND:
        if re.search(ONLY_INTEGERS_REGEX, _auxilliary_argument):
            num_rows = int(_auxilliary_argument)
        else:
            num_rows = DEFAULT_MERGE_ROW_COUNT
        merge_images(_input_image_paths, _output_image_dir, num_rows)

    else:
        print("Error: Incorrect command supplied")
        assert False #should never get here - commandName was already validated


if __name__ == "__main__":
    #Ensure the user supplied a correct command word and number of arguments
    if len(sys.argv) < 2:
        print_help(Error.TOO_FEW_ARGUMENTS)

    elif not sys.argv[2] in VALID_COMMANDS:
        print_help(Error.INVALID_COMMAND, sys.argv[2])

    elif not len(sys.argv) == MAP_COMMAND_TO_NUM_ARGS[sys.argv[2]]:
        print_help(Error.WRONG_NUM_ARGUMENTS, sys.argv[2])

    else:
        #Get the input file paths and make sure there aren't too many
        inputImageDir = sys.argv[1]

        #add a trailing slash to the input directory if one wasn't given
        if not inputImageDir[-1] == '/':
            inputImageDir += '/'

        #Make sure there aren't too many images to process
        inputImagePaths = get_folder_images(inputImageDir)

        print("Image paths:")
        print(inputImagePaths)

        if len(inputImagePaths) > MAX_FILES:
            print(f"There are {len(inputImagePaths)} files in {inputImageDir} - "
                f"there can be at most {MAX_FILES} files")

        else:

            #Define the output directory based on the input directory's name
            #Don't capture the directory-slash before adding the relevant suffix
            outputImageDir = inputImageDir[:-1] + MAP_COMMAND_TO_SUFFIX[sys.argv[2]]

            #Make sure we can write to the directory
            ensure_dir(outputImageDir)

            #Get the number of files already in the output image directory
            num_previous_files = get_num_files_in_directory(outputImageDir)

            #Inform the user what is going to happen to the images
            inform_user_before_operation(inputImageDir, outputImageDir, sys.argv[2])

            #Now that we have prepared everything, we can start performing the
            #   actual requested function
            #Send over the auxilliary argument if one is needed
            if MAP_COMMAND_TO_NUM_ARGS[sys.argv[2]] == 4:
                choose_image_command(inputImagePaths, outputImageDir, sys.argv[2], sys.argv[3])
            else:
                choose_image_command(inputImagePaths, outputImageDir, sys.argv[2])

            #Inform the user what happened to the images
            inform_user_after_operation(inputImageDir, outputImageDir, sys.argv[2], \
                num_previous_files)
