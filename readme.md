# Running Instructions
    Use one of the following commands (where <> brackets represent a placeholder,
        and [] brackets represent optional arguments)
        1. python photo_tools.py rename <photo_directory_name>
        2. python photo_tools.py pad <photo_directory_name> [black, white]
        3. python photo_tools.py neg <photo_directory_name>
        4. python photo_tools.py merge <photo_directory_name> [# rows]

# Renaming:
## Problem:
    When digitizing film negatives, the resulting image files are not properly indexed.
    This happens for two reasons:
        1. Multiple reels are scanned at the same time, so subsequent reels' first image
            starts at an index greater than 1
        2. Multiple scans are made of the same negative, so subsequent negatives start
            beyond where they normally would.

## Solution:
    Reindex all of the images based on the total number of images, rather than their current names.
    Incorporate "alternative takes", which are denoted by having a letter flag at the end of their filename.
    For example, PICT0006 and PICT0009b could represent alternative takes of the same negative.


# Padding:
## Problem:
    The most common format for uploading to Instagram is with square photos, and
        35mm negatives are a 2:3 format.
    This means that up to 1/3 of the image can be lost by squaring off the sides.
## Solution:
    Pad the shorter sides of the image to make all dimensions equal.
    By default, this is done with grey, but can be done with black/white per user arguments.


# Negating:
## Problem:
    Some scanners won't invert the image's colour, and so it must be done digitally.
## Solution:
    Batch colour inversion


# Merging:
## Problem:
    Sprite sheet maintenance.
## Solution:
    Flexible merging (based on the number of rows)
