# Running Instructions
    Use one of the following commands (where <> brackets represent a placeholder, and [] brackets represent optional arguments)
        1. python photoTools.py rename <photo_directory_name>
        2. python photoTools.py pad <photo_directory_name> [black]
        3. python photoTools.py neg <photo_directory_name>
        4. python photoTools.py merge <photo_directory_name> [1 row]

# Renaming:
## Problem:
    When digitizing film negatives, the resulting image files are not properly indexed.
    This happens for two reasons:
        1. Multiple reels are scanned at the same time, so subsequent reels start above 1
        2. Multiple scans are made of the same negative, so subsequent negatives start beyond where they normally would.

## Solution:
    Reindex all of the images based on the total number of images, rather than their current names.


# Padding:
## Problem:
    When uploading to Instagram, they only accept square photos
## Solution:
    Pad the shorter sides of the image to make all dimensions equal (by default, this is done with white)


# Negating:
## Problem:
    Some scanners won't invert the image's colour, and it must be done digitally.
## Solution:
    Batch colour inversion


# Merging:
## Problem:
    Sprite sheet maintenance.
## Solution:
    Flexible merging (based on the number of rows)