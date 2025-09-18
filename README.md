# comfyui-sundryutils
Some comfyui nodes that I developed for personal use.

## Available nodes
The nodes are found under the "✨ PersonalPostProc" category.

### ✨ Return DateString
This node returns a date string which comfyui can parse to create folder structures in the output folder. I needed this because I use a save image node with extended file formats that did not recognise the comfyui syntax for dates. Plug this node's output into the fileprefix of a save node.

### ✨ Sharpen, RealGrain & Autocontrast
![Comparison of no grain and grain!](/readme_img/compare_nofilter_grain.png "To the left no grain and to the right with applied grain")
This node overlays an image of real grain on top of your image, this is much less computationally expensive than nodes that create grain on the fly per run and also produces more accurate grain. It also gives the option to add some sharpening and contrast to offset the darkening by the addition of the grain. Add this or a similar extracted grain image by renaming it to `grain.png` and placing it directly inside the `assets` folder: [https://www.flickr.com/photos/patdavid/7314861896](https://www.flickr.com/photos/patdavid/7314861896).


### ✨ Apply HaldClut
![Comparison of no lut and lut!](/readme_img/compare_nolut_lut.png "To the left no lut and to the right with applied lut (Fuji Velvia 50)")
Finally there is a HaldClut applicator which adds a LUT of different simulations of real life analog film to the image for a certain look. Make sure they are of the correct format, namely a HALDCLUT of 12-levels. In the provided link [http://rawtherapee.com/shared/HaldCLUT.zip](http://rawtherapee.com/shared/HaldCLUT.zip) you can find dozens of LUTs that give a unique look to an image and place them in the `assets/luts/` folder. 

### Order of application
As described to me the general order of post-processing application is generally grain and sharpening first and colour correction later, so apply the sharpening first and the LUT second. Adding grain also helps if you add it prior to upscaling in image to image.
