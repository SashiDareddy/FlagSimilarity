import os
import logging
import textwrap
from PIL import Image, ImageFont, ImageDraw
from glob import glob
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import  cosine_similarity

def does_label_needs_to_be_wrapped(font: ImageFont.FreeTypeFont, label_text:str
                                   , label_width:int) -> Tuple[bool, int]:
    """

    :param font:
    :param label_text: single-line text to be checked if it needs to wrapped
    :param label_width:
    :return: True if text needs to be wrapped else False
    """
    w,h = font.getsize(label_text)
    per_char_pixels = w/len(label_text)
    can_fit_n_chars_in_single_line = label_width//per_char_pixels
    return (len(label_text) > can_fit_n_chars_in_single_line, can_fit_n_chars_in_single_line)



def draw_label(fontpath: str, label_text:str, label_width:int, label_height:int, font_size:int=14) ->Image:
    label_box = Image.new("RGB", (label_width, label_height), (0,0,0))
    draw = ImageDraw.Draw(label_box)
    font = ImageFont.truetype(fontpath, size=font_size, encoding='utf-8')

    # check if the label needs to be wrapped to fit in label_box
    do_wrap, single_line_chars= does_label_needs_to_be_wrapped(font, label_text, label_width)
    if do_wrap:
        # wrap the label text
        wrapper = textwrap.TextWrapper(width=single_line_chars)
        word_list = wrapper.wrap(text=label_text)

        label_text_new = ''

        for ii in word_list[:-1]:
            label_text_new = label_text_new + ii + '\n'

        label_text_new += word_list[-1]
        label_text = label_text_new # overwrite prodivded input label_text_new with multiline version
        w, h = font.getsize_multiline(label_text)

    else:
        w, h = font.getsize(label_text)

    draw.multiline_text(((label_width-w)//2,(label_height-h)//2), label_text, font=font, align="center")
    return label_box



def get_image_grid(search_results: Dict[str, List[List]], img_dir: str,font_path: str
                       , thumbnail_size: int=192, spacing:int =5):
    # find how many models we have returned results
    list_of_models = list(search_results.keys())
    n_models = len(list_of_models)

    # find how many results are returned per-model, just check the first model
    n_results_per_model = len(search_results[list_of_models[0]])

    # label_box - this box is where we display the name of the country and similarity score
    label_box_height = 32
    label_box_width = thumbnail_size
    # set up a grid to hold images:

    # each model's result is displayed in a column, with `spacing` spacing between columns
    grid_width = (n_models * thumbnail_size) + (n_models+1)*spacing

    # the height of the grid is determined by how many results are returned per-model
    # we also need to add in the label_box which sits below each image
    # and the extra label_box_height below is to store the model-name at the top of the column
    grid_height = label_box_height+(n_results_per_model*(thumbnail_size+label_box_height))

    grid_img = Image.new("RGB", (grid_width, grid_height), (0,0,0))

    # below we will fill the grid of images one column at a time
    grid_img_px_tracker = spacing
    for model_name, matches in search_results.items():
        column_img = Image.new("RGB", (thumbnail_size, grid_height), (255, 255, 255))
        img_files, proper_names, scores = list(zip(*matches))
        caption_text = [f"{a} [{b:0.3f}]" for a, b in zip(proper_names, scores)]
        column_img_px_tracker = 0
        for idx, (img_to_show, img_caption)  in enumerate(zip(img_files, caption_text)):
            if idx==0:
                # before we add first image to column , set up the column header
                # header img
                label_img = draw_label(font_path, model_name, label_box_width, label_box_height, 18)
                column_img.paste(label_img, (0,column_img_px_tracker))

                # move down the column to paste the 1st flag
                column_img_px_tracker+= label_box_height

                # 1st flag
                label_img = draw_label(font_path, img_caption, label_box_width, label_box_height, 14)
                column_img.paste(label_img, (0, column_img_px_tracker))
                column_img_px_tracker += label_box_height

                flag_img = Image.open(os.path.join(img_dir,img_to_show))
                column_img.paste(flag_img, (0, column_img_px_tracker))
                column_img_px_tracker += thumbnail_size


            else:
                label_img = draw_label(font_path, img_caption, label_box_width, label_box_height, 14)
                column_img.paste(label_img, (0, column_img_px_tracker))
                column_img_px_tracker += label_box_height

                flag_img = Image.open(os.path.join(img_dir, img_to_show))
                column_img.paste(flag_img, (0, column_img_px_tracker))
                column_img_px_tracker += thumbnail_size

        grid_img.paste(column_img, (grid_img_px_tracker,0) )
        grid_img_px_tracker+=(thumbnail_size+spacing)

    return grid_img


class SimilaritySearch:
    def __init__(self, data_dir:str, knn_k: int):
        self.csv_filelist = glob(data_dir)
        self.feature_dfs = {} # contains the bottleneck feature dataframes - one per model
        self.knn = {}
        self.knn_k = knn_k
        self.cosineSimDFs = {} #stores pre-computed cosine-similarity matrix

        for f in self.csv_filelist:
            logging.info(f"Loading features from {f}...")

            featureset_name = os.path.splitext(os.path.basename(f))[0]

            self.feature_dfs[featureset_name] = pd.read_csv(f, index_col=("filename", "territory_name"))

        for featureset_name, X in self.feature_dfs.items():
            logging.info(f"Setting up KNN search using {featureset_name} features...")
            self.knn[featureset_name] = NearestNeighbors(n_neighbors=knn_k, metric="cosine")
            self.knn[featureset_name].fit(self.feature_dfs[featureset_name].values)

        for featureset_name, X in self.feature_dfs.items():
            logging.info(f"Pre-computing Cosine Similarity using {featureset_name} features...")
            sim_X = cosine_similarity(self.feature_dfs[featureset_name].values)
            sim_df = pd.DataFrame(sim_X
                                  ,index = self.feature_dfs[featureset_name].index
                                  ,columns=self.feature_dfs[featureset_name].index.get_level_values("territory_name"))

            self.cosineSimDFs[featureset_name]=sim_df


    def find_knn_items(self, queryPoint: np.ndarray, featureset: str) -> List[List]:
        most_similar_scores, most_similar_indicies = self.knn[featureset].kneighbors(queryPoint, return_distance=True)
        most_similar_item_names = self.feature_dfs[featureset].iloc[most_similar_indicies.squeeze()]\
                                .index.values.tolist()
        result = [[a,b,c] for (a,b),c in zip(most_similar_item_names, most_similar_scores.squeeze())]
        return result

    def find_cosinesimilar_items(self, queryPointName: str, featureset: str) -> List[List]:
        return (1- self.cosineSimDFs[featureset][queryPointName].sort_values(ascending=False).head(self.knn_k))\
            .reset_index()\
            .values\
            .tolist()

    def search(self, queryPointName: str, queryType: str="cosine")-> Dict[str, List[List]]:
        search_results={}
        assert queryType in ["knn", "cosine"], "queryType must be one of \"knn\" or \"cosine\""
        if queryType == "knn":
            for featureset, df in self.feature_dfs.items():
                Q = self.feature_dfs[featureset].loc(axis=0)[pd.IndexSlice[:,queryPointName]].values
                search_results[featureset] = self.find_knn_items(Q, featureset)
        else:
            for featureset, df in self.cosineSimDFs.items():
                search_results[featureset] = self.find_cosinesimilar_items(queryPointName, featureset)

        return search_results

