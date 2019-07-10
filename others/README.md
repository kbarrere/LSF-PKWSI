# Dcoumentation

Here, I will try to give a brief explanation of every scripts.

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
