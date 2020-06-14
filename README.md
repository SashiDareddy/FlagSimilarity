# Flag Similarity Search


Each of the 200+ flags available in Wikipedia's [gallery of sovereign state flags](https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags) 
have been featurised using pre-trained models such as **`DenseNet201`**, **`InceptionV3`**, 
**`ResNet152V2`**, **`VGG16`**, and **`Xception`**. The featurisation process allows us to represent 
each flag as an n-dimensional vector and perform cosine similarity searches to find most 
similar flags given a query flag."),

Start by selecting a territory name from the dropdown list - The flags are returned
in decreasing order of similarity. You can see the cosine distance (1-cosine similarity
displayed next to the territory's name. The first flag in the returned results is the query flag you selected.

More to follow...

![Flag Similarity Search App Demo](FlagsApp.gif)