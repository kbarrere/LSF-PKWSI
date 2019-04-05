import argparse
from xmlPAGE import *

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Merge Bounding boxes')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines (in the format pageID.LineID keyword score startframe endframe totalframe')
	parser.add_argument('pages_path', nargs='+', help='path to page xml file associated with the index')
	parser.add_argument('output_index', help='path to the outputted index. in the format pageID keyword score xmin ymin xmax ymax')
	parser.add_argument('--rec', type=int, default=1, help='Number of recursive merging')
	parser.add_argument('--min-overlap', type=float, default=0.5, help='Minimum percentage of overlaping for 2 bbxs to be considered as intersecting')
	parser.add_argument('--min-intersection', type=float, default=0.2, help='Minimum percentage of a bb intersecting with other bbxs in a group for a merge')
	
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

def bb_equal(bb1, bb2):
	xmin1, ymin1, xmax1, ymax1 = bb1.get_coords()
	xmin2, ymin2, xmax2, ymax2 = bb2.get_coords()
	score1 = bb1.get_score()
	score2 = bb2.get_score()
	
	return (xmin1 == xmin2 and ymin1 == ymin2 and xmax1 == xmax2 and ymax1 == ymax2 and score1 == score2)

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

def merge_bb_group(bb_list):
	total_mass = 0.0
	total_x = 0.0
	total_y = 0.0
	total_w = 0.0
	total_h = 0.0
	max_score = 0.0
	
	for bb in bb_list:
		xmin, ymin, xmax, ymax = bb.get_coords()
		score = bb.get_score()
		
		total_mass += score
		total_x += score * (xmax + xmin) / 2
		total_y += score * (ymax + ymin) / 2
		total_w += score*(xmax - xmin)
		total_h += score*(ymax - ymin)
		
		max_score = max(max_score, score)
	
	# Temporary solution to avoid division by 0
	if total_mass == 0.0:
		return bb_list[0]
	
	center_x = total_x / total_mass
	center_y = total_y / total_mass
	center_w = total_w / total_mass
	center_h = total_h / total_mass
	
	xmin = center_x - center_w / 2
	xmax = center_x + center_w / 2
	ymin = center_y - center_h / 2
	ymax = center_y + center_h / 2
	
	bb = BB(int(xmin), int(ymin), int(xmax), int(ymax), max_score)
	
	return bb




# Reading the index file
index_file = open(args.index_path, 'r')
index_dict = {}
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
	
index_file.close()


bbxs_dict = {}

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
					
					if pageID not in bbxs_dict:
						bbxs_dict[pageID] = {}
					if keyword not in bbxs_dict[pageID]:
						bbxs_dict[pageID][keyword] = []
					
					bbxs_dict[pageID][keyword].append(bb)
					
	else:
		print("Could not find any page indexed with pageID: " + pageID)

output = open(args.output_index, 'w')

for pageID in bbxs_dict:
	for keyword in bbxs_dict[pageID]:
		bb_list = bbxs_dict[pageID][keyword]
		
		for i in range(args.rec):
			bbxs_grps = []
			
			for bb1 in bb_list:
				
				# Search for a bb that has an intersection with current bb
				is_bb_alone = True
				for bb2 in bb_list:
					overlap = (overlap_percent(bb1, bb2) + overlap_percent(bb2, bb1) ) / 2
					if is_intersection_bb(bb1, bb2) and overlap > args.min_overlap and not bb_equal(bb1, bb2):
						is_bb_alone = False
						
						# Try to insert that couple of bounding box in every existing group of bounding box
						is_couple_new = True
						for bbxs_grp in bbxs_grps:
							is_bbs_match = True
							
							curr_grp_to_test = []
							nbr_intersection1 = 0
							nbr_intersection2 = 0
							
							# Construct the curr group to test
							for bb in bbxs_grp:
								curr_grp_to_test.append(bb)
								
								# Count the number of intersections the couple of bbxs have with the group
								if is_intersection_bb(bb1, bb):
									overlap = (overlap_percent(bb1, bb) + overlap_percent(bb, bb1) ) / 2
									if overlap >= args.min_overlap:
										nbr_intersection1 += 1
								if is_intersection_bb(bb2, bb):
									overlap = (overlap_percent(bb1, bb) + overlap_percent(bb, bb1) ) / 2
									if overlap >= args.min_overlap:
										nbr_intersection2 += 1
							
							# Minimum the couple has to have an intersection with 1 bbx in the group
							if (nbr_intersection1 >= 1 and nbr_intersection2 >= 1):
								
								# Add the couple in the current group to test if they are not already inside
								if bb1 not in curr_grp_to_test:
									curr_grp_to_test.append(bb1)
								if bb2 not in curr_grp_to_test:
									curr_grp_to_test.append(bb2)
									
								nbr_bbxs = len(curr_grp_to_test)
								for bb_tmp1 in curr_grp_to_test:
									nbr_intersection = -1
									for bb_tmp2 in curr_grp_to_test:
										if is_intersection_bb(bb_tmp1, bb_tmp2):
											overlap = (overlap_percent(bb_tmp1, bb_tmp2) + overlap_percent(bb_tmp2, bb_tmp1) ) / 2
											if overlap >= args.min_overlap:
												nbr_intersection += 1
									
									if nbr_intersection < args.min_intersection * (nbr_bbxs-1):
										is_bbs_match = False
							else:
								is_bbs_match = False
							
							# Insert the couple in that group
							if is_bbs_match:
								is_couple_new = False
								if bb1 not in bbxs_grp:
									bbxs_grp.append(bb1)
								if bb2 not in bbxs_grp:
									bbxs_grp.append(bb2)
						
						# Create a new group is the couple match nowhere
						if is_couple_new:
							bbxs_grps.append([bb1, bb2])
					
				if is_bb_alone:
					bbxs_grps.append([bb1])
			
			# Merge the bounding boxes of one group into one big one
			merged_bb_list = []
			
			for bbxs_grp in bbxs_grps:
				new_bb = merge_bb_group(bbxs_grp)
				merged_bb_list.append(new_bb)

			bb_list = merged_bb_list
		
		for bb in bb_list:
			# pageID keyword score xmin ymin xmax ymax
			xmin, ymin, xmax, ymax = bb.get_coords()
			score = bb.get_score()
			line_to_write = pageID + ' ' + keyword + ' ' + str(score) + ' ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + '\n'
			output.write(line_to_write)

output.close()
