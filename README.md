# Line Segmentation Free Probabilistic Keyword Spotting and Indexing

An approach to remove the need for automatic textline extraction for Probabilistic Keyword Spotting and Indexing.

A tutorial is available [here](https://github.com/kbarrere/LSF-PKWSI/tree/refactor/tutorial#tutorial).

# Requierements

xmlPAGE.py from [P2PaLA](https://github.com/lquirosd/P2PaLA) by Lorenzo Quirós Díaz.
[direct link](https://github.com/lquirosd/P2PaLA/blob/master/page_xml/xmlPAGE.py)

# Dcoumentation

Here, I will try to give a brief explanation of every scripts.

## [convert-lines-to-page](https://github.com/kbarrere/LSF-PKWSI/tree/master/convert-lines-to-page)

The scripts in this folder aim to convert index, ground truth from a line format to the page format.
This is usefull to compare with others.

#### [gt_lines2page.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/convert-lines-to-page/gt_lines2page.py)

This script is used to convert a ground truth.

#### [index_lines2page.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/convert-lines-to-page/index_lines2page.py)

It convert the index obtained after applysing Keyword Spotting.

### [extract-slices](https://github.com/kbarrere/LSF-PKWSI/tree/master/extract-slices)

Here the scripts aim to obtain the page xml file containingg the generated slices.

#### [estimate_heigh.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/extract-slices/estimate_heigh.py)

The scripts is used as an heuristic to compute the best heights for the slices.

#### [create_xml.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/extract-slices/create_xml.py)

This one generates the page xml by using the previous script

#### [rlsa.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/extract-slices/rlsa.py)

A python code taken from [this repository](https://github.com/Vasistareddy/python-rlsa). It is slightly changed so that it can work with python2. It is used as a parameter to estimate the heights.

#### [write_gt_to_custom_lines.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/extract-slices/write_gt_to_custom_lines.py)

An attempt to add a ground truth for each slices bases on the true position of the real lines.

## [scripts](https://github.com/kbarrere/LSF-PKWSI/tree/master/scripts)

In that folder, there is the main scripts to use.

#### [bounding_boxes.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/scripts/bounding_boxes.py)

It is a class provided to retrieve information from the bounding boxes obtained, and perform various operations on it.

#### [convert_frames_to_pixels.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/scripts/convert_frames_to_pixels.py)

Converts the indexed bounding boxes with the frame positions obtained with Keyword Spotting to a pixel level.

#### [correct_bbxs_shape_pixels.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/scripts/correct_bbxs_shape_pixels.py)

As we obtained very large bounding boxes, with the keyword in their rightmost part, we proposed to cut the bounding boxes left part with this script.

#### [get_hits.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/scripts/get_hits.py)

Provided an index and the groundtruth, it marks the hits and misses for bounding boxes.

#### [merge_bbxs.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/scripts/merge_bbxs.py)

Script to merge raw and overlapping bounding boxes to a single and consolidated boundung box.

## [others](https://github.com/kbarrere/LSF-PKWSI/tree/master/others)

Well.. Everything else that may be used one day.

#### [compare.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/compare.py)

Compare two index obtained and print stats.

#### [count_intersecting_bb.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/count_intersecting_bb.py)

Count the number of overlapping bounding boxes per obtained consolidated bounding box

#### [count_results.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/count_results.py)

Count the number of true positives, false postives, ... and provide stats.

#### [create_KWS_csv.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/create_KWS_csv.py)

Write results in a csv file. Good to compare approaches with excel, ...

#### [create_fake_gt.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/create_fake_gt.py)

It was used to provide a quick demo. Basically add a text to each line.

#### [get_threshold_curves.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/get_threshold_curves.py)

Provided the results obtained with the program in [this repository](https://github.com/PRHLT/KwsEvalTool.git), create a csv file with every piece of information.

#### [merge_intersecting_bbs.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/merge_intersecting_bbs.py)

An attempt to merge again every consolidated bounding boxes that are still overlapping. It has proved to be useless.

#### [print_curves.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/print_curves.py)

Plot RP curves.

#### [print_mean_curves.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/print_mean_curves.py)

Plot the mean RP curve for a lot of file.

#### [shape_hist.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/shape_hist.py)

Shows an histogram of the shapes of every bounding boxes

#### [show_bb_box.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/show_bb_box.py)

A visualization tool for printing the bounding boxes.

#### [sort_diff_rp.sh](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/sort_diff_rp.sh)

Given the RP curve, compute precision - recall and prinnt the results sorted. Useful when you are looking for the point where precision = recall.

#### [test_shape.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/sort_diff_rp.sh)

Provides stats about the shapes of the bounding boxes.

## [test-process.txt](https://github.com/kbarrere/LSF-PKWSI/blob/master/others/test_shape.py)

This file contains the steps I used to obtain the indexes.
