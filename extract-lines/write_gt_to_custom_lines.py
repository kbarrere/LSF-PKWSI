import argparse
from xmlPAGE import *

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Take the GT and write it inside custom lines')
	parser.add_argument('custom_page', help='path to page xml file associated with the custom line extraction')
	parser.add_argument('gt_page', help='path to page xml file associated with the ground truth')
	parser.add_argument('output_page', help='path where to save the resulting page')
	parser.add_argument('--creator', default='PRHLT', help='name of the creator that will be written inside the resulting xml')

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

def get_max_coord(coord_list):
	line_xmin = coord_list[0][0]
	line_ymin = coord_list[0][1]
	line_xmax = coord_list[0][0]
	line_ymax = coord_list[0][1]
	
	for i in range(1, len(coord_list)):
		x, y = coord_list[i]
		
		line_xmin = min(line_xmin, x)
		line_ymin = min(line_ymin, y)
		line_xmax = max(line_xmax, x)
		line_ymax = max(line_xmax, y)
	
	return line_xmin, line_ymin, line_xmax, line_ymax
	

def convert_to_coords(x1, y1, x2, y2):
	return str(x1)+","+str(y1) + " " + str(x1)+","+str(y2)+ " " + str(x2)+","+str(y2)+ " " + str(x2)+","+str(y1)



# Open GT Page XML
gt_page = pageData(args.gt_page)
gt_page.parse()
textline_elements = gt_page.get_region('TextLine')

gt_list = [] # List of (bbx, associated text)
for textline_element in textline_elements:
	line_coords = gt_page.get_coords(textline_element)
	line_xmin, line_ymin, line_xmax, line_ymax = get_max_coord(line_coords)
	
	# ~ line_width = line_xmax - line_xmin
	# ~ line_height = line_ymax - line_ymin
	
	bb = BB(line_xmin, line_ymin, line_xmax, line_ymax, 1)
	
	text = gt_page.get_text(textline_element)
	
	# Store the bbxs and the text
	gt_list.append((bb, text))



# Open Custom Page XML
custom_page = pageData(args.custom_page)
custom_page.parse()
textline_elements = custom_page.get_region('TextLine')



# Open output XML
output_page = pageData(args.output_page, creator=args.creator)

width, height = custom_page.get_size()
img_name = custom_page.get_name()

output_page.new_page(img_name, str(height), str(width))

custom_text_regions = custom_page.get_region('TextRegion')

for custom_text_region in custom_text_regions:
	regionID = custom_page.get_id(custom_text_region)
	regionCoords = custom_page.get_coords(custom_text_region)
	
	# Write the text region
	xmin, ymin, xmax, ymax = get_max_coord(regionCoords)
	output_text_region = output_page.add_element("TextRegion", regionID, "TextRegion", convert_to_coords(xmin, ymin, xmax, ymax))
	
	
	
	

for textline_element in textline_elements:
	line_coords = gt_page.get_coords(textline_element)
	line_xmin, line_ymin = line_coords[0]
	line_xmax, line_ymax = line_coords[2]
	
	bb = BB(line_xmin, line_ymin, line_xmax, line_ymax, 1)
	
	# ~ print("----------------------------------------------")
	# ~ print(bb)
	
	for i in range(len(gt_list)):
		bbgt = gt_list[i][0]
		if is_intersection_bb(bb, bbgt):
			overlap = overlap_percent(bbgt, bb)
			# ~ if overlap > 0.5:
				# ~ print(overlap)
				# ~ print(bbgt)

output_page.save_xml()
