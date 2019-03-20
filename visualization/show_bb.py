from PIL import Image
import numpy as np
import argparse
from xmlPAGE import *



if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Print Bounding boxes for the given index file and image')
	parser.add_argument('img_path', help='path to the image to show')
	parser.add_argument('page_path', help='path to page xml file associated to the image and the lines')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines')
	parser.add_argument('target', help='keyword to search for')
	parser.add_argument('--gt', help='path to the Ground Truth (GT)')
	parser.add_argument('--bb-thickness', type=int, default=5, help='Size of the bounding box contour')
	parser.add_argument('--rec-merge', type=int, default=0, help='Number of time to merge the close bounding box. -1 to do it until it converges')

	args = parser.parse_args()


class BB:
	def __init__(self, xmin, ymin, xmax, ymax, score):
		self.xmin = xmin
		self.ymin = ymin
		self.xmax = xmax
		self.ymax = ymax
		self.score = score
	
	def get_coords(self):
		return self.xmin, self.ymin, self.xmax, self.ymax
	
	def get_score(self):
		return self.score

def is_in_range(xmin, xmax, x):
	return (xmin <= x and x <= xmax)

def is_intersection_segment(xmin1, xmax1, xmin2, xmax2):
	return (is_in_range(xmin1, xmax1, xmin2) or is_in_range(xmin1, xmax1, xmax2) or is_in_range(xmin2, xmax2, xmin1) or is_in_range(xmin2, xmax2, xmax1))

def is_intersection_bb(bb1, bb2):
	xmin1, ymin1, xmax1, ymax1 = bb1.get_coords()
	xmin2, ymin2, xmax2, ymax2 = bb2.get_coords()
	
	return (is_intersection_segment(xmin1, xmax1, xmin2, xmax2) and is_intersection_segment(ymin1, ymax1, ymin2, ymax2))
	
	
	
	


img = Image.open(args.img_path)

def draw_line(img, x1, y1, x2, y2, line_thickness=1, color=(255, 0, 0), dx=0.1):
	width, height = img.size
	
	if x1 != x2:
		a = float((y1 - y2)) / float((x1 - x2))
		b = y1 - a * x1
		
		for xt in np.arange(min(x1, x2), max(x1, x2), dx):
			yt = a*xt + b
			for dxt in np.arange(-float(line_thickness)/2, float(line_thickness)/2):
				for dyt in np.arange(-float(line_thickness)/2, float(line_thickness)/2):
					x = int(min(max(xt + dxt, 0), width-1))
					y = int(min(max(yt + dyt, 0), height-1))
					img.putpixel((int(x), int(y)), color)
	
	elif y1 != y2:
		a = float((x1 - x2)) / float((y1 - y2))
		b = x1 - a * y1
		
		for yt in np.arange(min(y1, y2), max(y1, y2), dx):
			xt = a*yt + b
			for dxt in np.arange(-float(line_thickness)/2, float(line_thickness)/2):
				for dyt in np.arange(-float(line_thickness)/2, float(line_thickness)/2):
					x = int(min(max(xt + dxt, 0), width-1))
					y = int(min(max(yt + dyt, 0), height-1))
					img.putpixel((x, y), color)



def draw_box(img, xmin, ymin, xmax, ymax, line_thickness=1, color=(255, 0, 0), dx=0.1):
	draw_line(img, xmin, ymin, xmin, ymax, line_thickness=line_thickness, color=color, dx=dx)
	draw_line(img, xmin, ymax, xmax, ymax, line_thickness=line_thickness, color=color, dx=dx)
	draw_line(img, xmax, ymax, xmax, ymin, line_thickness=line_thickness, color=color, dx=dx)
	draw_line(img, xmax, ymin, xmin, ymin, line_thickness=line_thickness, color=color, dx=dx)
	
	
def score_to_color(score, bad_color=(255, 0, 0), good_color=(0, 255, 0)):
	output_color = []
	for c in range(len(bad_color)):
		output_color.append(int(bad_color[c] + score*(good_color[c]-bad_color[c])))
	
	return tuple(output_color)


lines_found = []

# Search for the desired keywords in index
index = open(args.index_path, 'r')
for line in index:
	line = line[:-1]
	lineID, keyword, p, start_frame, end_frame, total_frames = line.split(' ')
	if keyword == args.target:
		#lineID = lineID.replace(',', '_')
		pageID, lineID = lineID.split('.')
		lines_found.append((lineID, keyword, float(p), int(start_frame), int(end_frame), int(total_frames)))
index.close()

# Open Page XML
page = pageData(args.page_path)
page.parse()
textline_elements = page.get_region('TextLine')

elements_found = []
for textline_element in textline_elements:
	textline_element_id = page.get_id(textline_element)
	for line in lines_found:
		line_id = line[0]
		if textline_element_id == line_id:
			line_coords = page.get_coords(textline_element)
			_, keyword, p, start_frame, end_frame, total_frame = line
			line_xmin, line_ymin = line_coords[0]
			line_xmax, line_ymax = line_coords[2]
			width = line_xmax - line_xmin
			height = line_ymax - line_ymin
			
			xmin = int(line_xmin + float(start_frame)/float(total_frame)*width)
			xmax = int(line_xmin + float(end_frame)/float(total_frame)*width)
			
			ymin = line_ymin
			ymax = line_ymax
			
			line_coords=[[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]
			
			elements_found.append((keyword, p, line_coords))

# Show bounding boxes and scores on the picture
for el in elements_found:
	score = el[1]
	coords = el[2]
	for i in range(len(coords)):
		x1, y1 = coords[i]
		x2, y2 = coords[(i+1) % len(coords)]
		draw_line(img, x1, y1, x2, y2, color=score_to_color(score), line_thickness=args.bb_thickness)

# Show bounding boxes and scores on the picture of the GT
if args.gt:
	gt = open(args.gt, 'r')

	for line in gt:
		line = line[:-1]
		line_split = line.split(' ')
		pageID, lineID, xmin, ymin, xmax, ymax = line_split[:6]
		keywords = line_split[6:]
		for keyword in keywords:
			if keyword == args.target:
				draw_box(img, int(xmin), int(ymin), int(xmax), int(ymax), color=(0, 0, 255), line_thickness=args.bb_thickness)
			
	gt.close

img.show()
