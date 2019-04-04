import argparse
from xmlPAGE import *



if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Print Bounding boxes for the given index file and image')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines')
	parser.add_argument('pages_path', nargs='+', help='path to page xml file associated to the image and the lines')
	parser.add_argument('gt', help='path to the Ground Truth (GT)')
	parser.add_argument('output_index', help='path to the outputted index')
	parser.add_argument('--threshold', type=float, default=0.5, help='If a bounding boxes has more percent of its area in one line of the GT containing this keyword, then consider it has a hit')
	parser.add_argument('--minimum-score', type=float, default=0.00001, help='Only take into account pseudo-word with a score superior to that value')

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



# Read the index
index_dict = {}
with open(args.index_path, 'r') as index_file:
	for line in index_file:
		line = line[:-1]
		lineID, keyword, score_str, start_frame_str, end_frame_str, total_frame_str = line.split(' ')
		
		pageID, lineID = lineID.split('.')
		score = float(score_str)
		start_frame = int(start_frame_str)
		end_frame = int(end_frame_str)
		total_frame = int(total_frame_str)
		
		if score >= args.minimum_score:
			if pageID not in index_dict:
				index_dict[pageID] = {}
			if lineID not in index_dict[pageID]:
				index_dict[pageID][lineID] = []
			index_dict[pageID][lineID].append([keyword, score, start_frame, end_frame, total_frame])

# Read the GT:
bbxs_dict_gt = {}
gt_file = open(args.gt, 'r')
for line in gt_file:
	line = line[:-1]
	line_split = line.split(' ')
	pageID, lineID, xmin_str, ymin_str, xmax_str, ymax_str = line_split[:6]
	xmin = int(xmin_str)
	ymin = int(ymin_str)
	xmax = int(xmax_str)
	ymax = int(ymax_str)
	keywords = line_split[6:]
	
	bb = BB(xmin, ymin, xmax, ymax, 1.0)
	
	for keyword in keywords:
		if pageID not in bbxs_dict_gt:
			bbxs_dict_gt[pageID] = {}
		if keyword not in bbxs_dict_gt[pageID]:
			bbxs_dict_gt[pageID][keyword] = []
		
		bbxs_dict_gt[pageID][keyword].append(bb)

gt_file.close()


output_file = open(args.output_index, 'w')

# Loop over all page XML files
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
					
					hit = 0
					if pageID in bbxs_dict_gt and keyword in bbxs_dict_gt[pageID]:
						bbxs_gt_list = bbxs_dict_gt[pageID][keyword]
						
						for bb8 in bbxs_gt_list:
							percentagearea = overlap_percent(bb, bb8)
							if percentagearea >= args.threshold:
								hit = 1
					
					line_to_write = pageID + ' ' + keyword + ' ' + str(hit) + ' ' + str(score) + ' ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + '\n' 
					output_file.write(line_to_write)
					
					
	else:
		print("Could not find any page indexed with pageID: " + pageID)

output_file.close()
