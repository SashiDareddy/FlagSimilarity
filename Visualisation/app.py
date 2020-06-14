import os
import logging
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_components import Row, Col,Card, CardImg, CardBody, CardGroup, CardDeck
import dash_html_components as html
from pprint import pprint
from  dash_html_components import Label
from Visualisation.utils import SimilaritySearch
import pandas as pd

# set-up state for performing similarity searches
IMAGE_DATA_DIR = r"./thumbnails"
FEATURE_DATA_DIR = "..\FeatureExtraction\data\*.csv"
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




def build_better_cards(search_results):
    cards_list= []
    for model_name, matches in search_results.items():
        img_files, proper_names, scores = list(zip(*matches))

        caption_text = [f"{a} [{b:0.2f}]" for a, b in zip(proper_names, scores)]

        card = dbc.Row([dbc.Col(

                    dbc.Card([dbc.CardImg(src=f"/{img_to_show}", top=True),
                              dbc.CardBody(html.Label(f"{img_caption}", className="card-text"))

                            ],style={"width": "18rem"})
                , align="start",style={"flex-direction": "column"})
                 for img_to_show, img_caption  in zip(img_files, caption_text)
            ],no_gutters =True, style={"flex-direction": "column"}
        )
        cards_list.append(card)


    return dbc.Container(cards_list, fluid=False)


app = dash.Dash(__name__, external_stylesheets=[external_stylesheets],
                assets_folder=IMAGE_DATA_DIR,
                assets_url_path='/')

app.layout = html.Div([
    html.Header(
        html.H1("Flag Similarity Search App")
                ),
    dcc.Markdown("Each of the flags available in Wikipedia's "
                 "[gallery of sovereign state flags](https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags) "
                 "has been featurised using pre-trained models such as DenseNet201, InceptionV3, ResNet152V2, VGG16, "
                 "and Xception. The featurisation process allows us to represent each flag as an n-dimensional vector "
                 "and perform cosine similarity searches against to find most similar flags given a query flag."),
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
    html.Div(


     id='dd-output-container', style={'columnCount': N_MODELS, 'rowCount': N_ITEMS_TO_RETRIEVE}
    )



], style={'columnCount': 1})


@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('territory-dropdown', 'value')])
def update_output(value):
    search_results = sim_state.search(territories_dict[value], SIMILARITY_METHOD)
    pprint(search_results)
    return build_better_cards(search_results)



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    app.run_server(debug=True)