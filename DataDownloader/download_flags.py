"""
Download images of flags from
https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags
"""

import os
import logging
from tqdm import tqdm
import wikipedia
import requests
from io import open as iopen
from urllib.parse import unquote

def download_svgs(wikipage_name: str, file_pattern: str, output_dir: str) -> None:
    """
    Downloads images from wikipage.

    :param wikipage_name: the name of the Wikipedia page in which to look for image links
                        eg: "Gallery_of_sovereign_state_flags"
    :param file_pattern: the pattern in the image links to look for eg: "Flag_of_"s
    :param output_dir: the path where the downloaded files will stored eg: "./flags/svg"
    :return: None
    """
    wikipage_img_list = wikipedia.page(wikipage_name).images
    # only keep links which have the FLAGFILE_PATTERN
    filtered_img_list = [i for i in wikipage_img_list if file_pattern in i]

    for p in tqdm(filtered_img_list):
        svgfilename = unquote(os.path.basename(p))
        img = requests.get(p)

        local_svgfile=os.path.join(f"./flags/svg/{svgfilename}")
        with iopen(local_svgfile, "wb") as f:
            f.write(img.content)


if __name__ == "__main__":

    # config:
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

    FLAGS_PAGE = "Gallery_of_sovereign_state_flags"
    FLAGFILE_PATTERN = "Flag_of_"
    FLAG_SVG_LOC = "./flags/svg"


    os.makedirs(FLAG_SVG_LOC, exist_ok=True)

    logging.info(f"Downloading SVG images from Wikipage: {FLAGS_PAGE}")

    download_svgs(FLAGS_PAGE,FLAGFILE_PATTERN,FLAG_SVG_LOC )

    logging.info(f"Download complete!")