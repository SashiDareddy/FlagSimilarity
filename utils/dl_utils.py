import os
from typing import Tuple, Any
import logging
import numpy as np
import math
from tensorflow.keras.utils import Sequence
from PIL import Image
from urllib.parse import unquote
from tqdm import tqdm
import pandas as pd

def get_stylised_name_from_fpath(fpath:str)-> Tuple[str,str]:
    """
    Takes the filepath of a flag and returns an cleansed version of the country name like so:
    i.e.,
    ('Flag_of_Australia_%28converted%29.jpg', 'Australia')
    ('Flag_of_Belgium_%28civil%29.jpg', 'Belgium')
    ('Flag_of_C%C3%B4te_d%27Ivoire.jpg', "Côte D'Ivoire")
    ('Flag_of_Canada_%28Pantone%29.jpg', 'Canada')
    ('Flag_of_the_Democratic_Republic_of_the_Congo.jpg', 'Democratic Republic Of The Congo'))
    :param fpath:
    :return:
    """

    # below we use unquote to get proper name of the country:
    # eg: "C%C3%B4te_d%27Ivoire' ->"Côte D'Ivoire"
    base_name = os.path.basename(fpath)
    unquoted_filename = unquote(os.path.splitext(base_name)[0]).split("_(")[0]

    # replace underscores in name with single-space & capitalise each word
    territory_name = unquoted_filename.replace("Flag_of_","").replace("_", " ").title()

    # for countries that start with "The ..." replace the "The " at the beginning
    if territory_name.startswith("The "):
        territory_name = territory_name[len("The "):]

    return base_name, territory_name

class MySequence(Sequence):
    """
    Custom sequence class to feed images to models
    """

    def __init__(self, img_fpaths_list: str ,batch_size: int =8, target_size: Tuple[int, int] = (256,256)
                ,return_filenames: bool =False):
        self.img_fpaths_list = img_fpaths_list
        self.batch_size = batch_size
        self.target_size=target_size
        self.return_filenames = return_filenames
        self.n_images = len(img_fpaths_list)
        logging.info(f"Found {self.n_images:,} images...")


    def __len__(self):
        return math.ceil(self.n_images/self.batch_size)

    def on_epoch_end(self):
        pass

    def __getitem__(self, idx:int, return_file_names: bool =False):
        img_fpaths_batch = self.img_fpaths_list[idx * self.batch_size : (idx + 1) * self.batch_size]

        X = []
        filenames_list=[]

        for img_file in img_fpaths_batch:
            img = Image.open(img_file).resize(self.target_size)
            X.append(np.array(img))

            filenames_list.append(get_stylised_name_from_fpath(img_file))

        if self.return_filenames:
            return filenames_list, np.asarray(X)
        else:
            return np.asarray(X)


def get_bottleneck_features(datqSeq: MySequence, model: Any) -> pd.DataFrame:
    """
    Helper function to extract features from a model and return them as pd.DataFrame

    If your input has a large number of images whose resulting features might not fit in memory
    then the following approach will result in out of memory errors.

    In that case you'd have to modify the following function to "yield" rather than return
    the full concatenated dataframe.
    By turning this into a generator - you can take one batch of images at a time - get their features
    , write the resulting batch to disk - via appends to file, and process the next batch. This way
    you can work with limited memory
    :param datqSeq:
    :param model:
    :return:
    """
    df_list=[]
    for filename_list, img_Xs in tqdm(datqSeq, total = datqSeq.__len__()):
        pd_index = pd.MultiIndex.from_tuples(filename_list, names=("filename", "territory_name"))
        bottleneck_features = model(img_Xs)

        X_df = pd.DataFrame(bottleneck_features.numpy()
                            , index=pd_index
                            , columns = [f"F_{i:06d}" for i in range(bottleneck_features.shape[1])])
        df_list.append(X_df)

    return pd.concat(df_list)



