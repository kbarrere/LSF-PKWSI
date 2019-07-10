# Dcoumentation

Here, I will try to give a brief explanation of every scripts.

## [extract-slices](https://github.com/kbarrere/LSF-PKWSI/tree/master/extract-slices)

Here the scripts aim to obtain the page xml file containingg the generated slices.

#### [estimate_heigh.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/extract-slices/estimate_heigh.py)

The scripts is used as an heuristic to compute the best heights for the slices.

#### [create_xml.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/extract-slices/create_xml.py)

This one generates the page xml by using the previous script

#### [rlsa.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/extract-slices/rlsa.py)

A python code taken from [this repository](https://github.com/Vasistareddy/python-rlsa). It is slightly changed so that it can work with python2. It is used as a parameter to estimate the heights.

#### [write_gt_to_custom_lines.py](https://github.com/kbarrere/LSF-PKWSI/blob/master/extract-slices/write_gt_to_custom_lines.py)

An attempt to add a ground truth for each slices bases on the true position of the real lines.
