#### Converting SVG files to PNG/JPEG
It is a huge pain in the back to convert SVGs into png/jpg on Windows machine. Much easier in Linux!


##### Node.js app to the rescue.
1. Install [node.js](https://nodejs.org/en/download/) 
2. Install [convert-svg-to-png](https://www.npmjs.com/package/convert-svg-to-png) with `--global` option
3. [Optional - you really should be using svg-to-png mentioned above] Install [convert-svg-to-jpeg](https://www.npmjs.com/package/convert-svg-to-jpeg) with `--global` option
4. You can then convert all the svg flags downloaded to `DataDownloader\flags` with the following command:

    ```convert-svg-to-png DataDownloader\flags\svg\*.svg --height 1400 --width 2100```
    
    **or**
    
    ```convert-svg-to-jpeg DataDownloader\flags\svg\*.svg --height 1400 --width 2100```
5. Note regarding the height & width used - some of the svg files have height/width information missing so if you run 
without the height & width specified the `convert-svg-to-jpeg` will throw errors. 
The reason I'm using such large size for the convert jpg's is because some of the flags are quite large and varied in their 
aspect ratio: a full hd dimensions of 1920(w)x1080(h) seems to work best but clips the wings of the bird on Zambia's flag.
a 2100x1400 seems to give the full view of the flags of all countries.
 
     If use smaller sizes such as 256x256
 then flags such as Algeria get truncated down to a a green square. 
 
6. Another issue with using fixed size output for jpegs is rest of the area covering the flag will be white - which means we would have to crop out the white areas - which causes issues with flags such as one of Algeria which has a large white portion on the right which could pose issues in cropping to the flag.
7. This is where a PNG file is much better since the area outside of the flag is transparent instead of white - much easier to crop to content.


### Running Order
First run ``DataDownloader\download_flags.py`` - this will download the flags in SVG format and place them in 
``DataDownloader\flags\svg`` folder. 

Second, run ```convert-svg-to-png DataDownloader\flags\svg\*.svg --height 1400 --width 2100``` this will place PNG 
version of the SVG flags (in the same folder as the SVG files)

Then finally run ``DataDownloader\crop_flags.py`` - this will take the PNG images and crops them to content and places 
them in  ``DataDownloader\flags\cropped_jpgs`` folder - these are the images which will be featurised.



