import argparse
from xmlPAGE import *

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Take the GT and write it inside custom lines')
	parser.add_argument('custom_page', help='path to page xml file associated with the custom line extraction')
	parser.add_argument('gt_page', help='path to page xml file associated with the ground truth')
	parser.add_argument('output_path', help='path where to save the resulting page')

	args = parser.parse_args()

class BB:
	def __init__(self, xmin, ymin, xmax, ymax, score):
		self.xmin = xmin
		self.ymin = ymin
		self.xmax = xmax
		self.ymax = ymax
		self.score = score
		self.score = score
	
	def get_coords(self):
		return self.xmin, self.ymin, self.xmax, self.ymax
	
	def get_score(self):
		return self.score
	
	def __repr__(self):
		return "BB("+self.__str__()+")"
	
	def __str__(self):
		return "xmin="+str(self.xmin)+" ymin="+str(self.ymin)+" xmax="+str(self.xmax)+" ymax="+str(self.ymax)+" score="+str(self.score)

def is_in_range(xmin, xmax, x):
	return (xmin <= x and x <= xmax)

def is_intersection_segment(xmin1, xmax1, xmin2, xmax2):
	return (is_in_range(xmin1, xmax1, xmin2) or is_in_range(xmin1, xmax1, xmax2) or is_in_range(xmin2, xmax2, xmin1) or is_in_range(xmin2, xmax2, xmax1))

def is_intersection_bb(bb1, bb2):
	xmin1, ymin1, xmax1, ymax1 = bb1.get_coords()
	xmin2, ymin2, xmax2, ymax2 = bb2.get_coords()
	
	return (is_intersection_segment(xmin1, xmax1, xmin2, xmax2) and is_intersection_segment(ymin1, ymax1, ymin2, ymax2))

def overlap_percent(bb1, bb2):
	xmin1, ymin1, xmax1, ymax1 = bb1.get_coords()
	xmin2, ymin2, xmax2, ymax2 = bb2.get_coords()
	
	xmin = max(xmin1, xmin2)
	ymin = max(ymin1, ymin2)
	xmax = min(xmax1, xmax2)
	ymax = min(ymax1, ymax2)
	
	base_area = (xmax1 - xmin1) * (ymax1 - ymin1)
	area = (xmax - xmin) * (ymax - ymin)
	
	percentage = 0.0
	if base_area > 0.0:
		percentage = float(area)/float(base_area)
	
	return percentage


# Open Page XML
gt_page = pageData(args.gt_page)
gt_page.parse()
textline_elements = gt_page.get_region('TextLine')

gt_list = [] # List of (bbx, associeted text)
for textline_element in textline_elements:
	line_coords = gt_page.get_coords(textline_element)
	line_xmin, line_ymin = line_coords[0]
	line_xmax, line_ymax = line_coords[2]
	# ~ line_width = line_xmax - line_xmin
	# ~ line_height = line_ymax - line_ymin
	
	bb = BB(line_xmin, line_ymin, line_xmax, line_ymax, 1)
	
	text = gt_page.get_text(textline_element)
	
	# Store the bbxs and the text
	gt_list.append((bb, text))
