"""Phototools.py constants"""
import enum
import sys

from typing import Optional

class Error(enum.Enum):
    """Special values for different kinds of execution errors"""
    TOO_FEW_ARGUMENTS = 1
    WRONG_NUM_ARGUMENTS = 2
    INVALID_COMMAND = 3
    TOO_MANY_FILES = 4

def print_help(_error_code : Error, _extra_arg : Optional[str] = None) -> None:
    """
    Prints a helpful string to the user, for when they have run the program incorrectly.
    """
    if _error_code == Error.TOO_FEW_ARGUMENTS:
        print("You haven't supplied enough arguments.")
    elif _error_code == Error.INVALID_COMMAND:
        print("f{_command_name} is not a valid command.")
    elif _error_code == Error.WRONG_NUM_ARGUMENTS:
        print("You have supplied the wrong number of arguments."
            f"{_extra_arg} needs {MAP_COMMAND_TO_NUM_ARGS[_extra_arg]} arguments")
    elif _error_code == Error.TOO_MANY_FILES:
        print(f"There are too many files for this operation ({_extra_arg}/{MAX_FILES} files)")
    else:
        print(f"Unknown error code: {_error_code}")

    print(f"Use 'python photo_tools.py <directory_name> {str(DISPLAY_COMMANDS)}'")
    sys.exit(_error_code)

def debug(_arg : str) -> None:
    """
    Prints _arg if the global DEBUG flag has been set to true.
    """
    if DEBUG:
        print(_arg)

DEBUG = True

MAX_FILES = 1000

IMAGE_SUFFIXES = ["*.JPG", "*.JPEG", "*.PNG"]
ONLY_INTEGERS_REGEX = "^\\d+$"
ONLY_CHARACTERS_REGEX = "^[a-zA-Z._-]+$"

BLACK_COLOUR = (0,0,0)
WHITE_COLOUR = (255,255,255)
BLACK_COLOUR_ALPHA = (0,0,0,255)
WHITE_COLOUR_ALPHA = (255,255,255,255)


RENAMING_COMMAND = "rename"
RENAMING_SUFFIX = "_(renamed)/"

PADDING_COMMAND = "pad"
PADDING_SUFFIX = "_(padded)/"
DEFAULT_PAD_COLOUR = (127,127,127)

NEGATIVE_COMMAND = "neg"
NEGATIVE_SUFFIX = "_(negative)/"

MERGE_COMMAND = "merge"
MERGE_SUFFIX = "_(merged)/"
DEFAULT_MERGE_ROW_COUNT = 1

MAP_COMMAND_TO_SUFFIX = {
    RENAMING_COMMAND : RENAMING_SUFFIX,
    PADDING_COMMAND : PADDING_SUFFIX,
    NEGATIVE_COMMAND : NEGATIVE_SUFFIX,
    MERGE_COMMAND : MERGE_SUFFIX,
    }

MAP_COMMAND_TO_NUM_ARGS = {
    RENAMING_COMMAND : 3,
    PADDING_COMMAND : 3,        #final 4th argument (pad colour) is optional
    NEGATIVE_COMMAND : 3,
    MERGE_COMMAND : 3,          #final 4th argument (num rows) is optional
}

#commands that a user can enter to execute part of the code from the command-line
VALID_COMMANDS = [RENAMING_COMMAND, PADDING_COMMAND, NEGATIVE_COMMAND, MERGE_COMMAND]

#the display version of the commands to be presented to the user when they need help
DISPLAY_COMMANDS = [RENAMING_COMMAND,
                    PADDING_COMMAND + " <black,white>",
                    NEGATIVE_COMMAND,
                    MERGE_COMMAND + " <numRows>"]
