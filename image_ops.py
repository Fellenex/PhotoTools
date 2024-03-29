"""A set of functions for manipulating batches of images"""
import os
import re
import math

from typing import Tuple
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
    debug(f"Base name ({base_name}) and index({base_index})")

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
        with Image.open(image) as image_object:

            #Rotate the image based on the EXIF data's orientation tag.
            #Ensures that images taller than they are wide are kept as such when padding
            image_object = PIL.ImageOps.exif_transpose(image_object)

            old_x,old_y = image_object.size
            bigger_dimension = max(old_x,old_y)

            #Figure out how much extra should be added to each of the four sides
            x_additive = y_additive = 0
            if old_x > old_y:
                y_additive = (old_x - old_y)//2

            elif old_y > old_x:
                x_additive = (old_y - old_x)//2

            #Create a new, larger image with the requested padding colour,
            #   and then paste the original image overtop in the correct position
            new_canvas = Image.new("RGB", (bigger_dimension,bigger_dimension), _pad_colour)
            new_canvas.paste(image_object, (x_additive, y_additive))
            new_canvas.save(_output_image_dir + os.path.basename(image))


def negative_images(_input_image_paths : list[str], _output_image_dir : str) -> None:
    """
    Takes a set of images and makes them negative.

    Saves the negative images in a new directory, defined by NEGATIVE_SUFFIX
    """
    for image in _input_image_paths:

        with Image.open(image) as image_object:

            #Rotate the image based on the EXIF data's orientation tag.
            #Ensures that images taller than they are wide are kept as such when padding
            image_object = PIL.ImageOps.exif_transpose(image_object)

            #Invert the image to make it negative, then save it.
            image_object = PIL.ImageOps.invert(image_object)
            image_object.save(_output_image_dir + os.path.basename(image))


def merge_images(_input_image_paths : list[str], _output_image_dir : str, \
    _constraint_amount : int, _constraint_type : Direction, _fill_direction : Direction) -> None:
    #_num_rows : int, ) -> None:
    """
        _fill_direction determines whether the images are placed column-wise or row-wise.
        _constraint_type determines whether the number of rows or columns has been constrained.
        _constraint_amount is the fixed number of rows or columns given by the user.

    Note that while the user has the option to constrain the number of rows or columns,
        different commands can result in the same file.
    e.g., If you have 7 images, then the following two commands
            python photo_tools.py d/ merge 2 row row
            python photo_tools.py d/ merge 4 column row
        will have the same output, since
            2 rows and 7 images --> 4 columns, and
            4 columns and 7 images --> 2 rows.

        (However, in this case,
            python photo_tools.py d/ merge 2 row column
        would yield a different image, since here the images are being filled by column.)
    """
    #Find the largest x/y sizes of all input images to ensure the resulting merged image
    #   will conform to some amount of regularity
    image_x_sizes = []
    image_y_sizes = []
    for image in _input_image_paths:
        with Image.open(image) as image_object:
            image_x_sizes.append(image_object.size[0])
            image_y_sizes.append(image_object.size[1])
    largest_x = max(image_x_sizes)
    largest_y = max(image_y_sizes)

    #Since the user fixed the number of images and rows, we can decide the number of columns
    if _constraint_type == Direction.ROW:
        num_rows = _constraint_amount
        num_columns = math.ceil(len(_input_image_paths) / _constraint_amount)

    #Since the user fixed the number of images and columns, we can decide the number of rows
    elif _constraint_type == Direction.COLUMN:
        num_columns = _constraint_amount
        num_rows = math.ceil(len(_input_image_paths) / _constraint_amount)

    else:
        sys.exit("Merge dimension constraint error")

    #Generate the coordinates for each of the images, based on how many rows/coulmns
    #   the user specified, and whether the images are being placed filling row by row
    #   or filling column by column
    coordinates = generate_image_coordinates(_fill_direction, len(_input_image_paths), \
        num_rows, num_columns, largest_x, largest_y)

    #Set up the new image, whose dimensions accommodate all input images (and maybe a
    #   bit of extra blank space, depending on how evenly the images fit)
    with Image.new("RGBA", (largest_x * num_columns, largest_y * num_rows), \
        WHITE_COLOUR_ALPHA) as new_canvas:

        #Paste all of the input images to the new canvas
        image_count = 0
        for image in _input_image_paths:
            with Image.open(image) as image_object:
                new_canvas.paste(image_object, coordinates[image_count])
                image_count += 1

        #Once all the images have been pasted in, then save the image.
        new_canvas.save(f"{_output_image_dir}({num_rows}x{num_columns})_"
            f"{direction_to_string(_fill_direction)}-merged.PNG")


def generate_image_coordinates(direction : Direction, _num_images : int, \
    _num_rows : int, _num_cols : int, _x : int, _y : int) -> list[Tuple[int,int]]:
    """
    Generates coordinates for a grid where either:
        i) a column is filled to a specified number of rows before moving on to the next column, or
        ii) a row is filled to a specified number of columns before moving on to the next row.
    """
    coordinates = []
    image_counter = 0
    if direction == Direction.COLUMN:
        column_counter = 0
        #using a "do-while" loop to get the increment in just before the final mod check
        #    (this avoids havging the column counter increment on the first run when 0 % 0 == 0)
        while image_counter < _num_images:
            coordinates.append( (column_counter * _x, (image_counter % _num_rows) * _y) )
            #Every _num_rows images, we move on to the next column
            image_counter += 1
            if image_counter % _num_rows == 0:
                column_counter += 1

    elif direction == Direction.ROW:
        row_counter = 0
        while image_counter < _num_images:
            coordinates.append( ((image_counter % _num_cols) * _x, row_counter * _y) )
            #Every _num_cols images, we move on to the next row
            image_counter += 1
            if image_counter % _num_cols == 0:
                row_counter += 1

    else:
        sys.exit("Coordinate direction error")

    return coordinates


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


def get_image_base_name_and_index(_image_path : str) -> Tuple[str, str]:
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
