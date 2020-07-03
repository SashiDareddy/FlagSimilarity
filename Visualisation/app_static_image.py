import base64
import logging
from io import BytesIO
from pprint import pprint

import dash
import dash_core_components as dcc
import dash_html_components as html

from resize_images import THUMBNAIL_SIZE
from viz_utils import SimilaritySearch, get_image_grid

# set-up state for performing similarity searches
IMAGE_DATA_DIR = r"./thumbnails"
FONT_FILE = r"./Fonts/UbuntuMono-Regular.ttf"
FEATURE_DATA_DIR = "..\FeatureExtraction\data\*.csv"
IMG_GRID_SPACING= 5 # in px
N_ITEMS_TO_RETRIEVE = 10
SIMILARITY_METHOD = "knn" # one of "knn" or "cosine"
sim_state = SimilaritySearch(FEATURE_DATA_DIR, N_ITEMS_TO_RETRIEVE)

# get the list of territory names
list_of_models = list(sim_state.feature_dfs.keys())
N_MODELS=len(list_of_models)
featureset_name = list_of_models[0] #pick the first feature set - we can use any featureset
territories = sim_state.feature_dfs[featureset_name].index.to_list()
territories = sorted(territories, key=lambda country: country[1]) # sorts by proper country name
territories_dict= dict(territories)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                assets_folder=IMAGE_DATA_DIR,
                assets_url_path='/')

app.layout = html.Div([
    html.Header(
        html.H1("Flag Similarity Search App")
                ),
    dcc.Markdown("Each of the 200+ flags available in Wikipedia's "
                 "[gallery of sovereign state flags](https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags) "
                 "have been featurised using pre-trained models such as **`DenseNet201`**, **`InceptionV3`**, "
                 "**`ResNet152V2`**, **`VGG16`**, and **`Xception`**. The featurisation process allows us to represent "
                 "each flag as an n-dimensional vector and perform cosine similarity searches to find most "
                 "similar flags given a query flag."),
    dcc.Markdown("Start by selecting a territory name from the dropdown list - The flags are returned "
                 "in decreasing order of similarity. You can see the cosine distance (1-cosine similarity"
                 "displayed next to the territory's name. The first flag in the returned results is the query flag you"
                 " selected."
                 ),
    html.Br(),
    html.Label('Select Territory:'),
    dcc.Dropdown(
        id='territory-dropdown',
        options=[
            *[{"label": country_name, "value": filename } for filename, country_name in territories]
        ],
        value='Flag_of_France.jpg'
    ),
    html.Br(),
    html.Img(



     id='dd-output-container', style={'columnCount': 1}
    )



], style={'columnCount': 1})


@app.callback(
    dash.dependencies.Output('dd-output-container', 'src'),
    [dash.dependencies.Input('territory-dropdown', 'value')])
def update_output(value):
    search_results = sim_state.search(territories_dict[value], SIMILARITY_METHOD)
    pprint(search_results)
    flag_grid = get_image_grid(search_results, IMAGE_DATA_DIR, FONT_FILE, THUMBNAIL_SIZE, IMG_GRID_SPACING)
    buffered_flag_grid = BytesIO()
    flag_grid.save(buffered_flag_grid, format="PNG")

    img_str = base64.b64encode(buffered_flag_grid.getvalue())

    result = 'data:image/png;base64,{}'.format(img_str.decode("ascii"))

    return result



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    app.run_server(debug=True)