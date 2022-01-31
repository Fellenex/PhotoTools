"""A set of functions for manipulating batches of images"""
from math import floor
import os
import re

from PIL import Image
import PIL.ImageOps

from constants import *

def rename_images(_input_image_paths : list[str], _output_image_dir : str) -> None:
    """
    Takes a set of images and reindexes them to be sequential, taking into account
        that there might be "alternative takes" for certain images.
    e.g.,
        [".../PICT0006", ".../PICT0009", ".../PICT0011b", ".../PICT0018"]
        becomes
        [".../PICT0001", ".../PICT0002", ".../PICT0002b", ".../PICT0003"]

    Saves the re-indexed images in a new directory, defined by RENAMING_SUFFIX
    """
    #Starts at 0 to account for incrementing when seeing a non-alternative
    #   (the 1st image can never be an alternative take)
    new_index = 0

    #Get the "base name" for the images - e.g., PICT, DCIM, IMG_, etc.
    #Assumes that each image has the same base name as the first one.
    #Also gets the "base index", e.g., 1, 001, 00018, etc.
    base_name, base_index = get_image_base_name_and_index(_input_image_paths[0])
    print(f"Base name ({base_name}) and index({base_index})")

    #Since the first image can't be an alternative take, this lets us
    #   get the proper index length for all of the images
    index_length = len(base_index)

    #For each image, rename based on the new indices
    for image in _input_image_paths:
        flag = get_alternative_flag(image)

        #increment the index if this was not an alternative-take image
        if flag == '':
            new_index += 1

        #Create an index padded with a sufficient number of prefixing '0's
        formatted_index = "0" * (index_length - len(str(new_index))) + str(new_index)

        #Get the file name's extension
        extension = os.path.splitext(image)[1]

        #Create the new file name based off of the current index
        new_filepath = _output_image_dir + base_name + formatted_index + flag + extension
        debug(f"Saving {image} to {new_filepath}")

        #Save the image with the updated path name
        with Image.open(image) as image_object:
            image_object.save(new_filepath)


def pad_images(_input_image_paths : list[str], _output_image_dir : str, \
    _pad_colour : tuple[int,int,int]) -> None:
    """
    Takes a set of images and pads them to be square by adding pixels in _pad_colour
        to the edges of the two shorter sides.
    Places the additional pixels in such a way that the old image is cented in the new image.
    Does not assume that each image will be the same size.

    Saves the padded images in a new directory, defined by PADDING_SUFFIX
    """
    for image in _input_image_paths:

        #Determine whether we shoud pad the left/right or the top/bottom
        y_additive = x_additive = 0
        with Image.open(image) as image_object:
            old_x,old_y = image_object.size

        bigger_dimension = max(old_x,old_y)

        #Figure out how much extra should be added to each of the four sides
        if old_x > old_y:
            y_additive = int((old_x - old_y)/2.0)
        elif old_y > old_x:
            x_additive = int((old_y - old_x)/2.0)

        #Create a new, larger image with the requested padding colour,
        #   and then paste the original image overtop in the correct position
        with Image.new("RGB", (bigger_dimension,bigger_dimension), _pad_colour) as new_canvas:
            new_canvas.paste(image_object, (x_additive, y_additive))
            new_canvas.save(_output_image_dir + os.path.basename(image))


def negative_images(_input_image_paths : list[str], _output_image_dir : str) -> None:
    """
    Takes a set of images and makes them negative.

    Saves the negative images in a new directory, defined by NEGATIVE_SUFFIX
    """
    for image in _input_image_paths:

        with Image.open(image) as image_object:
            image_object = PIL.ImageOps.invert(image_object)
            image_object.save(_output_image_dir + os.path.basename(image))


def merge_images(_input_image_paths : list[str], _output_image_dir : str, _num_rows : int) -> None:
    """
    Takes a set of images and merges them into one image, organized into _num_rows rows.
    Any leftover space will be filled with transparent background.
        (e.g., fitting 8 images into 3 rows)

    Saves the merge image in a new directory, defined by MERGE_SUFFIX
    """
    #Determine the size of the merged image
    images_per_row = len(_input_image_paths)/_num_rows
    canvas_x,canvas_y = Image.open(_input_image_paths[0]).size
    canvas_y = canvas_y * _num_rows

    if not floor(images_per_row) == images_per_row:
        images_per_row = int(images_per_row)
        #if we can't split the rows up evenly, then make the first rows have the extras
        num_overfilled_rows_remaining = len(_input_image_paths) % _num_rows -1
        col_counter = -1
        canvas_x = canvas_x * (images_per_row + 1)
    else:
        #it'll be a nice, even image!
        images_per_row = int(images_per_row)
        num_overfilled_rows_remaining = 0
        col_counter = 0
        canvas_x = canvas_x * images_per_row

    new_canvas = Image.new("RGBA", (canvas_x, canvas_y), WHITE_COLOUR_ALPHA)

    #keep track of the position at which to paste
    curr_x = 0
    curr_y = 0
    for image in _input_image_paths:
        image_object = Image.open(image)

        new_canvas.paste(image_object, (curr_x,curr_y))

        col_counter += 1
        if col_counter == images_per_row:
            if num_overfilled_rows_remaining > 0:
                #give the next row an extra image
                col_counter = -1
                num_overfilled_rows_remaining -= 1
            else:
                col_counter = 0

            #Start the next row
            curr_x = 0
            curr_y += image_object.size[1]
        else:
            curr_x += image_object.size[0]

    #defaults to PNG for transparency things
    new_canvas.save(_output_image_dir + "(" + str(_num_rows) + "-merged)" + ".PNG")



def get_alternative_flag(_image_path : str) -> str:
    """
    #Takes an image path name and returns either an empty string or a character,
    #   depending on whether or not it's an "alternative" take of another photo.
    #   e.g., for files 114.png and file 118b.png, both images are of the same negative
    #   (with potentially different scanning settings), and they are renamed to 001.png and 001b.png
    #
    """
    image_extless = os.path.splitext(os.path.basename(_image_path))[0]

    #if the final character is an integer, then there's no alternative flag
    if re.search(ONLY_INTEGERS_REGEX, image_extless[-1]):
        alternative_flag = ''
    else:
        alternative_flag = image_extless[-1]

    return alternative_flag


def get_image_base_name_and_index(_image_path : str) -> (str, str):
    """
    Takes an image file path and returns the "base name" and index as two parts.
    That is, the file name without any indices or alternative flags.
    e.g., ".../PICT002b.png" as input returns "PICT", "002b".
    e.g., ".../DCIM_0344.png" as input returns "DCIM_", "0344".
    """
    image_extless = os.path.splitext(os.path.basename(_image_path))[0]

    #There should be at least one integer in the string to act as an index.
    assert re.search(ONLY_CHARACTERS_REGEX, image_extless) is None

    #Count forward from the start of the string until we reach an integer,
    #   at which point we will have reached the indexing portion of the filename.
    i=1
    while i < len(image_extless) and re.search(ONLY_CHARACTERS_REGEX, image_extless[:i]):
        i += 1

    #Decrement i by one to account for the final character which was found to
    #   be not a character.
    i -= 1

    return image_extless[:i], image_extless[i:]
