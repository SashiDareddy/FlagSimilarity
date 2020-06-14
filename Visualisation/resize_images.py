"""
Resize images to have the same short-side for use in Dash app
"""
import os
import math
import logging
from tqdm import tqdm
from PIL import Image
from glob import glob

THUMBNAIL_SIZE= 192

def thumbnail(img: Image, size: int) -> Image:
    """
    This function is adapted from Dan D.'s answer at
    https://stackoverflow.com/questions/4321290/how-do-i-make-pil-take-into-account-the-shortest-side-when-creating-a-thumbnail
    :param img:
    :param size:
    :return:
    """

    img = img.copy()

    width, height = img.size

    if width == height:
        img.thumbnail((size, size))

    elif height > width:
        ratio = float(width) / float(height)
        newwidth = ratio * size
        img = img.resize((int(math.floor(newwidth)), size))

    elif width > height:
        ratio = float(height) / float(width)
        newheight = ratio * size
        img = img.resize((size, int(math.floor(newheight))))

    return img

if __name__ == "__main__":
    # config:
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    JPG_DIR= r"../DataDownloader/flags/cropped_jpgs/*.jpg"
    OUTDIR = "./thumbnails"

    os.makedirs(OUTDIR, exist_ok=True)
    jpg_flags = glob(JPG_DIR)


    for p in tqdm(jpg_flags):
        filename = os.path.basename(p)

        image = Image.open(p)
        thumb = thumbnail(image, THUMBNAIL_SIZE)
        thumb.save(os.path.join(OUTDIR, filename), quality=100)