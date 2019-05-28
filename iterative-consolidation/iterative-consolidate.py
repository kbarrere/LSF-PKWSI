import argparse
from xmlPAGE import *
import math

import matplotlib.pyplot as plt

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Print Bounding boxes for the given index file and image')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines (in the format pageID.LineID keyword score startframe endframe totalframe')
	parser.add_argument('pages_path', nargs='+', help='path to page xml file associated with the index')
	
	parser.add_argument('--min-overlap', type=float, default=0.5, help='minimum percentage of overlaping for 2 bbxs to be considered as intersecting')
	parser.add_argument('--min-intersection', type=float, default=0.2, help='minimum percentage of a bb intersecting with other bbxs in a group for a merge')
	parser.add_argument('--minimum-score', type=float, default=0.00001, help='Only take into account pseudo-word with a score superior to that value')
	parser.add_argument('--iterations', type=int, default=10, help='Number of iterations to run')
	
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

def bb_equal(bb1, bb2):
	xmin1, ymin1, xmax1, ymax1 = bb1.get_coords()
	xmin2, ymin2, xmax2, ymax2 = bb2.get_coords()
	
	return (xmin1 == xmin2 and ymin1 == ymin2 and xmax1 == xmax2 and ymax1 == ymax2)

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

def sigmoid(x, a=1.0, b=0.0):
	return 1 / (1 + math.exp(-a*x+b))

def merge_bb_group0(bb_list):
	total_mass = 0.0
	total_x = 0.0
	total_y = 0.0
	total_w = 0.0
	total_h = 0.0
	max_score = 0.0
	
	for bb in bb_list:
		xmin, ymin, xmax, ymax = bb.get_coords()
		
		overlap100 = total_overlap_percent(bb, bb_list) - 1.0
		pbeta = sigmoid(overlap100, 8, 2.75)
		
		score = bb.get_score() * pbeta
		
		total_mass += score
		total_x += score * (xmax + xmin) / 2
		total_y += score * (ymax + ymin) / 2
		total_w += score*(xmax - xmin)
		total_h += score*(ymax - ymin)
		
		max_score = max(max_score, score)
	
	# Temporary solution to avoid division by 0
	if total_mass < 0.000001:
		return bb_list[0]
	
	center_x = total_x / total_mass
	center_y = total_y / total_mass
	center_w = total_w / total_mass
	center_h = total_h / total_mass
	
	xmin = center_x - center_w / 2
	xmax = center_x + center_w / 2
	ymin = center_y - center_h / 2
	ymax = center_y + center_h / 2
	
	if math.isnan(xmin):
		print("xmin:"+str(xmin))
		print("ymin:"+str(ymin))
		print("xmax:"+str(xmax))
		print("ymax"+str(ymax))
		print("total mass:"+str(total_mass))
		print("total x:"+str(total_x))
		print("total y:"+str(total_y))
		print("center_x:"+str(center_x))
		print("center_y:"+str(center_y))
		print("center_w:"+str(center_w))
		print("center_h:"+str(center_h))
	
	bb = BB(int(xmin), int(ymin), int(xmax), int(ymax), max_score)
	
	return bb
	
def merge_bb_groupi(bb_list, bi, debug=False):
	total_mass = 0.0
	total_x = 0.0
	total_y = 0.0
	total_w = 0.0
	total_h = 0.0
	max_score = 0.0
	
	for bb in bb_list:
		xmin, ymin, xmax, ymax = bb.get_coords()
		
		if debug:
			print("beta: " + str(bb))
		
		pbeta = overlap_percent(bb, bi)
		if debug:
			print("P(beta): " + str(pbeta))
		
		score = bb.get_score() * pbeta
		if debug:
			print("score: " + str(score))
		
		total_mass += score
		total_x += score * ((xmax + xmin) / 2)
		total_y += score * ((ymax + ymin) / 2)
		total_w += score*(xmax - xmin)
		total_h += score*(ymax - ymin)
		
		max_score = max(max_score, score)
	
	# Temporary solution to avoid division by 0
	if debug:
		print("total mass: " + str(total_mass))
	if total_mass < 0.000001:
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

def merge_lists(list1, list2):
	output_list = []
	
	for el1 in list1:
		output_list.append(el1)
		
	for el2 in list2:
		if el2 not in output_list:
			output_list.append(el2)
	
	return output_list
	
def append_lists(list1, list2):
	for el2 in list2:
		if el2 not in list1:
			list1.append(el2)



line_dict = {} # Stocks line and their position info, their number of frames, ...

# Reading the index file
index_file = open(args.index_path, 'r')
index_dict = {}
for line in index_file:
	line = line[:-1]
	lineID, keyword, score_str, start_frame_str, end_frame_str, total_frame_str = line.split(' ')
	pageID, lineID = lineID.split('.')
	score = float(score_str)
	
	if score > args.minimum_score:
		start_frame = int(start_frame_str)
		end_frame = int(end_frame_str)
		total_frame = int(total_frame_str)
		
		if pageID not in index_dict:
			index_dict[pageID] = {}
		if lineID not in index_dict[pageID]:
			index_dict[pageID][lineID] = []
		index_dict[pageID][lineID].append([keyword, score, start_frame, end_frame, total_frame])
		
		# Complete line dict
		regionID = lineID.split('-')[0].split('_')[-1]
		if pageID not in line_dict:
			line_dict[pageID] = {}
		if regionID not in line_dict[pageID]:
			line_dict[pageID][regionID] = {}
		if lineID not in line_dict[pageID][regionID]:
			line_dict[pageID][regionID][lineID] = [-1, -1, -1, -1, -1] # xmin, ymin, xmax, ymax, number of frames
		if line_dict[pageID][regionID][lineID][4] == -1:
			line_dict[pageID][regionID][lineID][4] = total_frame
	
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
			line_width = line_xmax - line_xmin + 1
			# ~ line_height = line_ymax - line_ymin
			
			# Complete line dict
			regionID = lineID.split('-')[0].split('_')[-1]
			if pageID not in line_dict:
				line_dict[pageID] = {}
			if regionID not in line_dict[pageID]:
				line_dict[pageID][regionID] = {}
			if lineID not in line_dict[pageID][regionID]:
				line_dict[pageID][regionID][lineID] = [-1, -1, -1, -1, -1] # xmin, ymin, xmax, ymax, number of frames
			if line_dict[pageID][regionID][lineID][0] == -1:
				line_dict[pageID][regionID][lineID][0] = line_xmin
				line_dict[pageID][regionID][lineID][1] = line_ymin
				line_dict[pageID][regionID][lineID][2] = line_xmax
				line_dict[pageID][regionID][lineID][3] = line_ymax
			
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
					
					if score > args.minimum_score:
						bbxs_dict[pageID][keyword].append(bb)
					
	else:
		print("Could not find any page indexed with pageID: " + pageID)





# Complete the line with no informations on the number of frames with the mean
for pageID in line_dict:
	for regionID in line_dict[pageID]:
		
		# Get the average number of frames on the line
		frame_count = 0
		for lineID in line_dict[pageID][regionID]:
			xmin, ymin, xmax, ymax, total_frame = line_dict[pageID][regionID][lineID]
			frame_count += total_frame
		mean_frame_count = frame_count / len(line_dict[pageID][regionID])
		
		# Use that number to complete the one without that information
		for lineID in line_dict[pageID][regionID]:
			xmin, ymin, xmax, ymax, total_frame = line_dict[pageID][regionID][lineID]
			if total_frame == -1:
				line_dict[pageID][regionID][lineID][4] = mean_frame_count





optiboxs = [] # Contains the best bbxs at each step

# Get a group ?	
for pageID in bbxs_dict:
	for keyword in bbxs_dict[pageID]:
		bb_list = bbxs_dict[pageID][keyword]
		
		# Construct original bbxs lists
		original_bb_list = []
		for bb in bb_list:
			original_bb_list.append([bb])
		
		bbxs_grps = []
		original_bbxs_grps = []
			
		for i1 in range(len(bb_list)):
			bb1 = bb_list[i1]
			
			# Search for a bb that has an intersection with current bb
			is_bb_alone = True
			for i2 in range(len(bb_list)):
				bb2 = bb_list[i2]
				overlap = (overlap_percent(bb1, bb2) + overlap_percent(bb2, bb1) ) / 2
				if is_intersection_bb(bb1, bb2) and overlap > args.min_overlap and not bb_equal(bb1, bb2):
					is_bb_alone = False
					
					# Try to insert that couple of bounding box in every existing group of bounding box
					is_couple_new = True
					# ~ for bbxs_grp in bbxs_grps:
					for ibbxs_grp in range(len(bbxs_grps)):
						bbxs_grp = bbxs_grps[ibbxs_grp]
						original_bbxs_grp = original_bbxs_grps[ibbxs_grp]
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
								append_lists(original_bbxs_grp, original_bb_list[i1])
							if bb2 not in bbxs_grp:
								bbxs_grp.append(bb2)
								append_lists(original_bbxs_grp, original_bb_list[i2])
								
					
					# Create a new group is the couple match nowhere
					if is_couple_new:
						bbxs_grps.append([bb1, bb2])
						original_bbxs_grps.append(merge_lists(original_bb_list[i1], original_bb_list[i2]))
				
			if is_bb_alone:
				bbxs_grps.append([bb1])
				original_bbxs_grps.append(original_bb_list[i1])
		
		
		
		

		# Merge the bounding boxes of one group into one big one
		merged_bb_list = []
		
		for bbxs_grp in original_bbxs_grps:

			new_bb = merge_bb_group0(bbxs_grp)
			# ~ if new_bb.get_score() > args.minimum_score:
				# ~ merged_bb_list.append(new_bb)
			# ~ else:
				# ~ print("OSKOUR")
			merged_bb_list.append(new_bb)

		bb_list = merged_bb_list
		original_bb_list = bbxs_grps

		
		
		# Write results
		for bb in bb_list:
			# pageID keyword score xmin ymin xmax ymax
			xmin, ymin, xmax, ymax = bb.get_coords()
			score = bb.get_score()
			# ~ line_to_write = pageID + ' ' + keyword + ' ' + str(score) + ' ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + '\n'
			# ~ output.write(line_to_write)
			
			i = 0
			if len(optiboxs) <= i:
				optiboxs.append({})
			if pageID not in optiboxs[i]:
				optiboxs[i][pageID] = {}
			if keyword not in optiboxs[i][pageID]:
				optiboxs[i][pageID][keyword] = []
			
			optiboxs[i][pageID][keyword].append(bb)

# ~ print(optiboxs[0]["M_Breitenberg_009-01_0098"]["BLANK"])
# ~ print(optiboxs[0]["M_Breitenberg_009-01_0098"])





def scores(optiboxs, i, bbs_dict, scores):
	total_score = 0
	for pageID in optiboxs[i]:
		for keyword in optiboxs[i][pageID]:
			for b in optiboxs[i][pageID][keyword]:
				s = 0
				for beta in bbxs_dict[pageID][keyword]:
					if is_intersection_bb(beta, b):
						index_score = beta.get_score()
						beta_score = overlap_percent(beta, b)
						s += beta_score * index_score
				
				if len(scores) <= i:
					scores.append({})
				if pageID not in scores[i]:
					scores[i][pageID] = {}
				if keyword not in scores[i][pageID]:
					scores[i][pageID][keyword] = []
				scores[i][pageID][keyword].append(s)
				
				total_score += s
	
	return total_score

scs = []
total_sc = scores(optiboxs, 0, bbxs_dict, scs)
print(total_sc)
# ~ print(scs)

x = [0]
y = [total_sc]





def iterate(optiboxs, i, bbs_dict, scs):
	
	print("==========================================================")
	print("Iteration " + str(i))
	
	for pageID in optiboxs[i-1]:
		for keyword in optiboxs[i-1][pageID]:
			for b in optiboxs[i-1][pageID][keyword]:			
				s = 0
				beta_list = []
				for beta in bbxs_dict[pageID][keyword]:
					if is_intersection_bb(beta, b):
						beta_list.append(beta)
				
				if len(beta_list) > 0:
					bi = merge_bb_groupi(beta_list, b)
					
					if len(optiboxs) <= i:
						optiboxs.append({})
					if pageID not in optiboxs[i]:
						optiboxs[i][pageID] = {}
					if keyword not in optiboxs[i][pageID]:
						optiboxs[i][pageID][keyword] = []
					
					optiboxs[i][pageID][keyword].append(bi)
	
	total_sc = scores(optiboxs, i, bbxs_dict, scs)
	print("Total score: " + str(total_sc))
	
	return total_sc

# ~ for i in range(1, 10):
	# ~ iterate(optiboxs, i, bbxs_dict, scs)
i = 1
while i < args.iterations:
	total_sc = iterate(optiboxs, i, bbxs_dict, scs)
	x.append(i)
	y.append(total_sc)
	i += 1

plt.plot(x, y)
plt.title("Evolution of best BB's relevance")
plt.xlabel("Iterations")
plt.ylabel("Sum of BB's relevance")
plt.show()