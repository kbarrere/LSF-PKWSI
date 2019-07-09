## Tutorial

In this tutorial, you will learn the basics about the main scripts for _Line Segmentation Free Probabilistic Keyword Spotting and Indexing_.

### **Step 1:** Creating the slices:

The first step consist in obtaining the page xml file corresponding to the images.
Each page is going to be divided into several slices that are used later for the indexing system.

In the directory _test_material_, a 1 image example is included here to play with.

Start by using it if you want:

```
cp test_material/RS_Aicha_vorm_Wald_031_0187.jpg .
```

Or use the one image you prefer.

Then proceed to the calculation of the slices using the provided scripts.

```
python ../extract-lines/create_xml.py RS_Aicha_vorm_Wald_031_0187.jpg . --blur 25 --local_threshold 201 --rlsa 20 --smooth_fft 0.0005
```

The parameters used here are tuned to fit the image (the corresponding dataset), you might try to change them.

### **Step 2:** The indexing

Well I have not been working on this step, so this is up to you !

Briefly you will need to:
* Obtain images from the slices with the xml file
* Apply an HTR architecture to obtain the characters' probabilities frame by frame, slice by slice
* Create a character lattice from the probabilities
* Obtain and index the best words

To save time, you can use the provided index and corresponding xml file (I advice to use both provided since they might differ from what you created

```
cp test_material/RS_Aicha_vorm_Wald_031_0187.xml .
cp test_material/RS_Aicha_vorm_Wald_031_0187.idx .
```

### **Step 3:** Time to merge !

Now, the fun starts.

Once you obtained your index corresponding to your given image and xml file, you'll need an additional step consolidating all the overlapping spots obtained with the spots.

#### Convert to pixel level

Before merging, we convert the Bounding Boxes (BB) from a frame level directly outputted by the indexing to a pixel level.
This will allow further preprocessing before merging.

```
python ../scripts/convert_frames_to_pixels.py RS_Aicha_vorm_Wald_031_0187.idx RS_Aicha_vorm_Wald_031_0187.xml px.idx
```

#### Shorten the large BBs

With our approach we sometime obtain very large BBs.
Here we count the number of characters in the keyword and modify the shape of the BB based on this number and some statistics.
This might have to be tuned.

```
python ../scripts/correct_bbxs_shape_pixels.py px.idx corrected.idx
```

#### Merging finally !

Now that we corrected the shapes, we can consolidated the raw BBs:

```
python ../scripts/merge_bbxs.py corrected.idx merged.idx
```

With the file _merged.idx_ you now have an index that you can use to make queries !

Each line contains (in the following order):
* Id of the page
* Keyword
* Probability
* xmin
* ymin
* xmax
* ymax

You reach the end of the tutorial.
However, Everything is not showcased here.
