import argparse
import math
from xmlPAGE import *



if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Print Bounding boxes for the given index file and image')
	parser.add_argument('--pages-path', nargs='+', help='path to page xml file associated to the image and the lines')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines')
	parser.add_argument('output_index_path', help='path to the output index containing the modified scores')
	parser.add_argument('--overlap-number', action='store_true', help='Multiply the score based on a sigmoid of the number of overlaping bbxs')
	parser.add_argument('--overlap-percent', action='store_true', help='Multiply the score based on the percentage of area overlapped by other bbxs')
	parser.add_argument('--overlap-score', action='store_true', help='Multiply the score based on the percentage of area overlapped by other bbxs multiplied by their respectives scores')
	parser.add_argument('--overlap-score-union', action='store_true', help='Multiply the score based on the percentage of area overlapped by other bbxs multiplied by their respectives scores, taking into account the union of overlaping bbxs')
	parser.add_argument('--gaussian-shape', action='store_true', help='Multiply the score based on a gaussian function depending on the number of frames of the bbx')
	parser.add_argument('--index-format', choices=['frames', 'pixels'], default ='frames', help='Format of the index file.')
	
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

def number_intersection(bb, bb_list):
	c = 0
	for bb8 in bb_list:
		if is_intersection_bb(bb, bb8):
			c += 1
	return c

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

def total_overlap_percent(bb, bb_list, debug=False):
	c = 0.
	for bb8 in bb_list:
		if is_intersection_bb(bb, bb8):
			if debug:
				print("Overlap with " + str(bb8))
				print("Value: " + str(overlap_percent(bb, bb8)))
			c += overlap_percent(bb, bb8)
	return c

def overlap_score(bb1, bb2):
	overlapper100 = overlap_percent(bb1, bb2)
	return overlapper100*bb2.get_score()

def total_overlap_score(bb, bb_list, debug=False):
	c = 0.
	for bb8 in bb_list:
		if is_intersection_bb(bb, bb8):
			if debug:
				print("Overlap with " + str(bb8))
				print("Value: " + str(overlap_score(bb, bb8)))
			c += overlap_score(bb, bb8)
	return c

def overlap_percent_union(bb1, bb2):
	xmin1, ymin1, xmax1, ymax1 = bb1.get_coords()
	xmin2, ymin2, xmax2, ymax2 = bb2.get_coords()
	
	xmin = max(xmin1, xmin2)
	ymin = max(ymin1, ymin2)
	xmax = min(xmax1, xmax2)
	ymax = min(ymax1, ymax2)
	
	base_area_1 = (xmax1 - xmin1) * (ymax1 - ymin1)
	base_area_2 = (xmax2 - xmin2) * (ymax2 - ymin2)
	area = (xmax - xmin) * (ymax - ymin)
	
	percentage = 0.0
	if base_area_1+base_area_2-area > 0.0:
		percentage = float(area)/(float(base_area_1+base_area_2-area))
	
	return percentage

def overlap_score_union(bb1, bb2):
	overlapper100 = overlap_percent_union(bb1, bb2)
	return overlapper100*bb2.get_score()

def total_overlap_score_union(bb, bb_list, debug=False):
	c = 0.
	for bb8 in bb_list:
		if is_intersection_bb(bb, bb8):
			if debug:
				print("Overlap with " + str(bb8))
				print("Value: " + str(overlap_score_union(bb, bb8)))
			c += overlap_score_union(bb, bb8)
	return c

def sigmoid(x, a=1.0, b=0.0):
	return 1 / (1 + math.exp(-a*x+b))
	
def gaussian(x, mean, std):
	return np.exp(- ((x - mean) ** 2) / (2 * std ** 2))


# Reading the index file
index_file = open(args.index_path, 'r')

bbxs_dict = {}
index_dict = {}

if args.index_format == 'frames':
	for line in index_file:
		line = line[:-1]
		lineID, keyword, score_str, start_frame_str, end_frame_str, total_frame_str = line.split(' ')
		pageID, lineID = lineID.split('.')
		score = float(score_str)
		start_frame = int(start_frame_str)
		end_frame = int(end_frame_str)
		total_frame = int(total_frame_str)
		
		if pageID not in index_dict:
			index_dict[pageID] = {}
		if lineID not in index_dict[pageID]:
			index_dict[pageID][lineID] = []
		index_dict[pageID][lineID].append([keyword, score, start_frame, end_frame, total_frame])

elif args.index_format == 'pixels':
	for line in index_file:
		line = line[:-1]
		pageID, keyword, score_str, xmin_str, ymin_str, xmax_str, ymax_str = line.split(' ')
		score = float(score_str)
		xmin = int(xmin_str)
		ymin = int(ymin_str)
		xmax = int(xmax_str)
		ymax = int(ymax_str)
		bb = BB(xmin, ymin, xmax, ymax, score)
		
		if pageID not in bbxs_dict:
			bbxs_dict[pageID] = {}
		if keyword not in bbxs_dict[pageID]:
			bbxs_dict[pageID][keyword] = []
		
		bbxs_dict[pageID][keyword].append(bb)
		
index_file.close()


# Loop over all page XML files
if args.pages_path:
	for page_path in args.pages_path:
		# Get the pageID from the path
		pageID = page_path.split('/')[-1].split('.')[0]
		if pageID in index_dict:
			# Open Page XML
			page = pageData(page_path)
			page.parse()
			textline_elements = page.get_region('TextLine')

			for textline_element in textline_elements:
				lineID = page.get_id(textline_element)
				
				line_coords = page.get_coords(textline_element)
				line_xmin, line_ymin = line_coords[0]
				line_xmax, line_ymax = line_coords[2]
				line_width = line_xmax - line_xmin
				# ~ line_height = line_ymax - line_ymin
				
				if lineID in index_dict[pageID]:
					for detected in index_dict[pageID][lineID]:
						keyword, score, start_frame, end_frame, total_frame = detected
						
						# Create a bounding box
						xmin = int(line_xmin + float(start_frame)/float(total_frame)*line_width)
						xmax = int(line_xmin + float(end_frame)/float(total_frame)*line_width)
						ymin = line_ymin
						ymax = line_ymax
						bb = BB(xmin, ymin, xmax, ymax, score)
						
						if pageID not in bbxs_dict:
							bbxs_dict[pageID] = {}
						if keyword not in bbxs_dict[pageID]:
							bbxs_dict[pageID][keyword] = ([], []) # BB_list, frame_numbers
						
						bbxs_dict[pageID][keyword][0].append(bb)
						bbxs_dict[pageID][keyword][1].append((lineID, start_frame, end_frame, total_frame))
						
		else:
			print("Could not find any page indexed with pageID: " + pageID)

# Create the resulting index file
output = open(args.output_index_path, 'w')
for pageID in bbxs_dict:
	for keyword in bbxs_dict[pageID]:
		bb_list = bbxs_dict[pageID][keyword][0]
		frame_list = bbxs_dict[pageID][keyword][1]
		for i in range(len(bb_list)):
			bb = bb_list[i]
			lineID, start_frame, end_frame, total_frame = frame_list[i]
			
			score = bb.get_score()
			
			pbon = 1.0
			if args.overlap_number:
				overlap = number_intersection(bb, bb_list) - 1
				pbon = sigmoid(overlap, 5, 1.0)
			
			pbop = 1.0
			if args.overlap_percent:
				overlap100 = total_overlap_percent(bb, bb_list) - 1.0
				pbop = sigmoid(overlap100, 8, 2.75)
			
			pbos = 1.0
			if args.overlap_score:
				overlapscore = total_overlap_score(bb, bb_list) - bb.get_score()
				pbos = sigmoid(overlapscore, 25, 12.5)
				# ~ pbos = pbos if overlapscore > 0.30 else 0.0
			
			pbosu = 1.0
			if args.overlap_score_union:
				overlapscore = total_overlap_score_union(bb, bb_list) - bb.get_score()
				pbosu = sigmoid(overlapscore, 42, 18)
				# ~ pbosu = pbosu if overlapscore > 0.23725 else 0.0
			
			pbgs = 1.0
			if args.gaussian_shape:
				nbr_frames = end_frame - start_frame
				len_keyword = len(keyword)
				frames_per_char = float(nbr_frames)/float(len_keyword)
				pbgs = gaussian(frames_per_char, 0, 62) # For large bbxs
				pbgs = pbgs * sigmoid(frames_per_char, 3, 0) # For small bbxs
			
			pb = pbon * pbop * pbos * pbosu * pbgs
			score = pb * score
			
			line_to_write = pageID+'.'+lineID+' '+keyword+' '+str(score)+' '+str(start_frame)+' '+str(end_frame)+' '+str(total_frame)+'\n'
			output.write(line_to_write)
			
output.close()
