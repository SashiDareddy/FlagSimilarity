"""
Crop image to content - it is easier in our case since outside of the flag's dimensions the PNG is just a transparent
layer - we use the `autocrop_image` function below to crop out unnecessary pixels from the input image.
"""

import os
import logging
from tqdm import tqdm
from PIL import Image
from glob import glob

def autocrop_image(image: Image) -> Image:
    """
    This function is adapted from https://gist.github.com/odyniec/3470977

    :param image: input png image to crop to content
    :return: cropped Image object in jpg format
    """

    # Get the bounding box
    bbox = image.getbbox()

    # Crop the image to the contents of the bounding box
    image = image.crop(bbox)

    # Determine the width and height of the cropped image
    (width, height) = image.size

    # Create a new image object for the output image
    cropped_image = Image.new("RGBA", (width, height), (0,0,0,0))

    # Paste the cropped image onto the new image
    cropped_image.paste(image)

    # Done!
    return cropped_image.convert("RGB")


if __name__ == "__main__":
    # config:
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    FLAG_SVG_LOC = "./flags/svg/*.png" #glob pattern for png formatted flags
    OUTDIR= "./flags/cropped_jpgs"

    os.makedirs(OUTDIR, exist_ok=True)
    png_flags = glob(FLAG_SVG_LOC)

    for p in tqdm(png_flags):
        filename = os.path.splitext(os.path.basename(p))[0]

        image = Image.open(p)
        image = autocrop_image(image)
        image.save(os.path.join(OUTDIR, f"{filename}.jpg"))