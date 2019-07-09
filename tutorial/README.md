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

