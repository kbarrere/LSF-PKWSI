import argparse
from xmlPAGE import *



if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Print Bounding boxes for the given index file and image')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines. In the format pageID keyword score xmin ymin xmax ymax')
	parser.add_argument('gt', help='path to the Ground Truth (GT)')
	parser.add_argument('output_index', help='path to the outputted index')
	parser.add_argument('--threshold', type=float, default=0.5, help='If a bounding boxes has more percent of its area in one line of the GT containing this keyword, then consider it has a hit')
	parser.add_argument('--minimum-score', type=float, default=0.00001, help='Only take into account pseudo-word with a score superior to that value')
	parser.add_argument('--width-extension', type=float, default=0.0, help='By how much percent the size of the bbx should be extendted on horizontal axis')
	parser.add_argument('--only-gt', action='store_true', help='Do not read index and show the gt')

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

def overlap_percent_union(bb1, bb2):
	xmin1, ymin1, xmax1, ymax1 = bb1.get_coords()
	xmin2, ymin2, xmax2, ymax2 = bb2.get_coords()
	
	xmin = max(xmin1, xmin2)
	ymin = max(ymin1, ymin2)
	xmax = min(xmax1, xmax2)
	ymax = min(ymax1, ymax2)
	
	base_area1 = (xmax1 - xmin1) * (ymax1 - ymin1)
	base_area2 = (xmax2 - xmin2) * (ymax2 - ymin2)
	area = (xmax - xmin) * (ymax - ymin)
	
	union_area = (float(base_area1)+float(base_area2)-float(area))
	
	percentage = 0.0
	if union_area > 0.0:
		percentage = float(area)/union_area
	
	return percentage



# Read the GT:
bbxs_dict_gt = {}
gt_file = open(args.gt, 'r')
for line in gt_file:
	line = line[:-1]
	line_split = line.split(' ')
	pageID, lineID, xmin_str, ymin_str, xmax_str, ymax_str = line_split[:6]
	line_xmin = int(xmin_str)
	line_ymin = int(ymin_str)
	line_xmax = int(xmax_str)
	line_ymax = int(ymax_str)
	line_width = line_xmax - line_xmin + 1
	keywords = line_split[6:]
	line_gt = ' '.join(keywords)
	line_gt_len = len(line_gt)
	
	pos = 0
	for keyword in keywords:
		if keyword != "":
			
			begin_pos = pos
			end_pos = pos + len(keyword)
			
			xmin = line_xmin + float(begin_pos) / float(line_gt_len) * float(line_width)
			xmax = line_xmin + float(end_pos) / float(line_gt_len) * float(line_width)
			
			if args.width_extension > 0.0:
				keyword_width = xmax - xmin + 1
				xmin = int(max(line_xmin, xmin - args.width_extension / 2 * keyword_width))
				xmax = int(min(line_xmax, xmax + args.width_extension / 2 * keyword_width))
			
			bb = BB(xmin, line_ymin, xmax, line_ymax, 1)
			
			if pageID not in bbxs_dict_gt:
				bbxs_dict_gt[pageID] = {}
			if keyword not in bbxs_dict_gt[pageID]:
				bbxs_dict_gt[pageID][keyword] = ([], [], []) # List of BBxs, and a list of boolean to kwow if the keyword has been detected
			
			bbxs_dict_gt[pageID][keyword][0].append(bb) # Store the true BBs
			bbxs_dict_gt[pageID][keyword][1].append(None) # Tell if the BB is overlapping with someone
			bbxs_dict_gt[pageID][keyword][2].append(0) # Tell the score of the overlapping BBs
		
		pos += len(keyword) + 1 # Add the number of characters of the word + a space

gt_file.close()


output_file = open(args.output_index, 'w')



if not args.only_gt:
	try_again = []
	
	# Read the index
	with open(args.index_path, 'r') as index_file:
		for line in index_file:
			line = line[:-1]
			pageID, keyword, index_score_str, xmin_str, ymin_str, xmax_str, ymax_str = line.split(' ')
			
			index_score = float(index_score_str)
			xmin = int(xmin_str)
			ymin = int(ymin_str)
			xmax = int(xmax_str)
			ymax = int(ymax_str)
			
			if index_score >= args.minimum_score and keyword != "":
				bb = BB(xmin, ymin, xmax, ymax, index_score)
				
				hit = 0
				if pageID in bbxs_dict_gt and keyword in bbxs_dict_gt[pageID]:
					bbxs_gt_list = bbxs_dict_gt[pageID][keyword]
					
					best_overlap_i = -1
					best_overlap_score = 0
					for i in range(len(bbxs_gt_list[0])):
						bbgt = bbxs_gt_list[0][i]
						if is_intersection_bb(bb, bbgt):
							percentagearea = overlap_percent(bb, bbgt)
							if percentagearea >= args.threshold:
								overlap100 = overlap_percent_union(bb, bbgt)
								score = overlap100 * index_score
								
								if score > bbxs_gt_list[2][i]: # This BB is better than the previous one for this true spot
									if score > best_overlap_score: # This true spot is better for the keyword
										best_overlap_score = score
										best_overlap_i = i
					
					if best_overlap_i != -1: # If we find a good spot :
						previous_bb = bbxs_dict_gt[pageID][keyword][1][best_overlap_i]
						if previous_bb is not None: # There is a previous BB with an inferior score
							try_again.append(previous_bb)
						
						# Store the best existing BB for the true spot
						bbxs_dict_gt[pageID][keyword][1][best_overlap_i] = bb
						bbxs_dict_gt[pageID][keyword][2][best_overlap_i] = best_overlap_score
						
					else: # Write the false positive
						line_to_write = pageID + ' ' + keyword + ' ' + '0' + ' ' + str(index_score) + ' ' + str(int(xmin)) + ' ' + str(int(ymin)) + ' ' + str(int(xmax)) + ' ' + str(int(ymax)) + '\n' 
						output_file.write(line_to_write)
	
	# Try again with the remaining BBs
	while len(try_again) > 0:
		try_again2 = []
		
		for bb in try_again:
			xmin, ymin, xmax, ymax = bb.get_coords()
			index_score = bb.get_score()
			
			hit = 0
			if pageID in bbxs_dict_gt and keyword in bbxs_dict_gt[pageID]:
				bbxs_gt_list = bbxs_dict_gt[pageID][keyword]
				
				best_overlap_i = -1
				best_overlap_score = 0
				for i in range(len(bbxs_gt_list[0])):
					bbgt = bbxs_gt_list[0][i]
					if is_intersection_bb(bb, bbgt):
						percentagearea = overlap_percent(bb, bbgt)
						if percentagearea >= args.threshold:
							overlap100 = overlap_percent_union(bb, bbgt)
							score = overlap100 * index_score
							
							if score > bbxs_gt_list[2][i]: # This BB is better than the previous one for this true spot
								if score > best_overlap_score: # This true spot is better for the keyword
									best_overlap_score = score
									best_overlap_i = i
				
				if best_overlap_i != -1: # If we find a good spot :
					previous_bb = bbxs_dict_gt[pageID][keyword][1][best_overlap_i]
					if previous_bb is not None: # There is a previous BB with an inferior score
						try_again2.append(previous_bb)
					
					# Store the best existing BB for the true spot
					bbxs_dict_gt[pageID][keyword][1][best_overlap_i] = bb
					bbxs_dict_gt[pageID][keyword][2][best_overlap_i] = best_overlap_score
				
				else: # Write the false positive
					line_to_write = pageID + ' ' + keyword + ' ' + '0' + ' ' + str(index_score) + ' ' + str(int(xmin)) + ' ' + str(int(ymin)) + ' ' + str(int(xmax)) + ' ' + str(int(ymax)) + '\n' 
					output_file.write(line_to_write)
		
		try_again = try_again2

# Get the keywords missed
for pageID in bbxs_dict_gt:
	for keyword in bbxs_dict_gt[pageID]:
		for i in range(len(bbxs_dict_gt[pageID][keyword][0])):
			
			if bbxs_dict_gt[pageID][keyword][1][i] is None: # if a miss
				bbgt = bbxs_dict_gt[pageID][keyword][0][i]
				xmin, ymin, xmax, ymax = bbgt.get_coords()
				
				# Write the miss
				line_to_write = pageID + ' ' + keyword + ' ' + '1' + ' ' + '-1' + ' ' + str(int(xmin)) + ' ' + str(int(ymin)) + ' ' + str(int(xmax)) + ' ' + str(int(ymax)) + '\n' 
				output_file.write(line_to_write)
			
			else: # else ther is an hit
				bb = bbxs_dict_gt[pageID][keyword][1][i]
				xmin, ymin, xmax, ymax = bb.get_coords()
				index_score = bb.get_score()
				
				# Write the hit
				line_to_write = pageID + ' ' + keyword + ' ' + '1' + ' ' + str(index_score) + ' ' + str(int(xmin)) + ' ' + str(int(ymin)) + ' ' + str(int(xmax)) + ' ' + str(int(ymax)) + '\n' 
				output_file.write(line_to_write)

output_file.close()
