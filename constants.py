"""Phototools.py constants"""
import enum

class Error(enum.Enum):
    """Special values for different kinds of execution errors"""
    TOO_FEW_ARGUMENTS = 1
    WRONG_NUM_ARGUMENTS = 2
    INVALID_COMMAND = 3

def debug(_string_arg):
    """
    Prints _string_arg if the global DEBUG flag has been set to true.
    """
    if DEBUG:
        print(_string_arg)

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
    PADDING_COMMAND : 4,
    NEGATIVE_COMMAND : 3,
    MERGE_COMMAND : 4,
}

#commands that a user can enter to execute part of the code from the command-line
VALID_COMMANDS = [RENAMING_COMMAND, PADDING_COMMAND, NEGATIVE_COMMAND, MERGE_COMMAND]

#the display version of the commands to be presented to the user when they need help
DISPLAY_COMMANDS = [RENAMING_COMMAND,
                    PADDING_COMMAND + "[black,white]",
                    NEGATIVE_COMMAND,
                    MERGE_COMMAND + "<numRows>"]
