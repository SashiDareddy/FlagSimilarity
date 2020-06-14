import os
import logging
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from skimage.io import imread
import PIL
from utils.dl_utils import MySequence, get_bottleneck_features
from glob import glob

IMG_HEIGHT=256
IMG_WIDTH=256
CHANNELS=3
IMG_SHAPE=(IMG_WIDTH, IMG_HEIGHT, CHANNELS)


# we will using the following pre-trained models along with their respective input preprocessors
model_list = {
    "DenseNet201": ["tf.keras.applications.DenseNet201(include_top=False, input_shape=IMG_SHAPE, pooling=\"avg\")"
                    ,"tf.keras.applications.densenet.preprocess_input"]
    ,"InceptionV3": ["tf.keras.applications.InceptionV3(include_top=False, input_shape=IMG_SHAPE, pooling=\"avg\")"
                     ,"tf.keras.applications.inception_v3.preprocess_input"]
    ,"ResNet152V2": ["tf.keras.applications.ResNet152V2(include_top=False, input_shape=IMG_SHAPE, pooling=\"avg\")"
                     ,"tf.keras.applications.resnet_v2.preprocess_input"]
    ,"VGG16": ["tf.keras.applications.VGG16(include_top=False, input_shape=IMG_SHAPE, pooling=\"avg\")"
               ,"tf.keras.applications.vgg16.preprocess_input"]
    ,"Xception": ["tf.keras.applications.Xception(include_top=False, input_shape=IMG_SHAPE,pooling=\"avg\")"
                ,"tf.keras.applications.xception.preprocess_input"]
}




if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    img_list = glob(r"C:\Users\sashi\PycharmProjects\SearchDeep\DataDownloader\flags\cropped_jpgs\*.jpg")

    # create a folder to store the bottleneck features as csv files
    output_dir = os.path.join("data")
    os.makedirs(output_dir, exist_ok=True)

    # set up a Sequence to generate images from disk and feed to the model
    data_seq = MySequence(img_list,batch_size=8, target_size = (256,256),return_filenames=True)

    # iterate over each pre-trained model and extract features.
    for (model_name, (_model, _preproc)) in model_list.items():
        logging.info(f"Extracting Bottleneck Features using {model_name}...")
        model = eval(_model)
        preproc = eval(_preproc)

        i = tf.keras.layers.Input([None, None, 3], dtype=tf.uint8)
        x = tf.cast(i, tf.float32)
        x = preproc(x)
        core = model
        x = core(x)

        featuriser_model = tf.keras.Model(inputs=[i], outputs=[x])

        features_df = get_bottleneck_features(data_seq, featuriser_model)
        features_df.to_csv(os.path.join(output_dir, f"{model_name}.csv"), header=True, index=True)




