"""A set of functions for manipulating batches of images"""
from math import floor
import os
from PIL import Image
import PIL.ImageOps

from constants import *


def rename_images(_input_image_paths, _output_image_dir):
    #Starts at 0 to account for incrementing when seeing a non-alternative
    #   (the 1st image can never be an alternative take)
    new_index = 0

    #For each image, rename based on the new indices
    for image in _input_image_paths:
        flag = is_alternative_take(image)

        #increment the index if this was not an alternative-take image
        if not flag:
            new_index += 1

        #Create the new file name based off of the current index
        destination = _output_image_dir + get_updated_index_filename(image, new_index, flag)
        print(f"Saving {image} to {destination}")

        image_object = Image.open(image)
        image_object.save(destination)


def pad_images(_input_image_paths, _output_image_dir, _pad_colour):
    for image in _input_image_paths:
        y_additive = x_additive = 0
        image_object = Image.open(image)
        old_x,old_y = image_object.size
        bigger = max(old_x,old_y)

        #Figure out how much extra should be added to each of the four sides
        if old_x > old_y:
            y_additive = int((old_x - old_y)/2.0)
        elif old_y > old_x:
            x_additive = int((old_y - old_x)/2.0)

        #Create a new, larger image with the requested padding colour,
        #   and then paste the original image overtop in the correct position
        new_canvas = Image.new("RGB", (bigger,bigger), _pad_colour)
        new_canvas.paste(image_object, (x_additive, y_additive))
        new_canvas.save(_output_image_dir + os.path.basename(image))


def negative_images(_input_image_paths, _output_image_dir):
    for image in _input_image_paths:
        image_object = Image.open(image)
        image_object = PIL.ImageOps.invert(image_object)

        print(_output_image_dir + os.path.basename(image))
        image_object.save(_output_image_dir + os.path.basename(image))


def merge_images(_input_image_paths, _output_image_dir, _num_rows):
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





#Takes an image path name and returns boolean indicating whether or not it's an
#   "alternative" take of another photo. e.g., for files 114.png and file 118b.png,
#   both images are of the same negative (with potentially different scanning settings)
#
#Parameters: String
#Return value: Either string (the alternative letter), or empty string
def is_alternative_take(_image_path):
    image_name = os.path.basename(_image_path)
    image_ext = os.path.splitext(_image_path)[1]
    image_extless = image_name[:-1*len(image_ext)]
    alternative = ''

    try:
        #If we are able to cast the final character to an int,
        #   then there is no alternative-take flag.
        int(image_extless[-1])
        #this above line functions as a cut when there is no flag

    except ValueError:
        #If we weren't able to cast this to an int, then it is an alternative take flag.
        alternative = image_extless[-1]

    return alternative


"""
All functions that follow are used only for rename_images().
Probably a better way to factor this all, since none of the other operations utilize any helper functions.
"""
#Takes a number and pads it with a sufficient number of prefixing '0's
#
#Parameters: String
#Return value: String
def get_formatted_index(_index):
    return "0" * (INDEX_LENGTH - len(str(_index))) + str(_index)


#Takes an image file path and removes indices and alternative flags
#
#Parameters: String
#Return value: String
def image_base_name(_image_path):
    image_name = os.path.basename(_image_path)
    image_ext = os.path.splitext(_image_path)[1]

    #cut off the extension
    image_extless = image_name[:-1*len(image_ext)]

    #cut off the alternative flag, if it exists
    if is_alternative_take(_image_path):
        image_extless = image_extless[:-1]

    #cutt off the index
    image_indexless = image_extless[:-1*INDEX_LENGTH]

    return image_indexless


#Takes an image file, an index, and (possibly) an alternative take letter,
#   and creates a new properly formatted file name.
#
#Parameters: String, integer, and string
#Return value: String
def get_updated_index_filename(_old_image_path, _new_index, _alt_letter=''):
    assert 0 < len(str(_new_index)) < 5
    extension = os.path.splitext(_old_image_path)[1]
    return image_base_name(_old_image_path) + get_formatted_index(_new_index) + \
        _alt_letter + extension
