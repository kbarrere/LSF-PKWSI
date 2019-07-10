# Dcoumentation

Here, I will try to give a brief explanation of every scripts.

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
