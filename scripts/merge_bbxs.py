import argparse
from xmlPAGE import *
from bounding_boxes import *
import math
import scipy.special
import numpy as np

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Merge Bounding boxes. Version 4, only using Geometry rules')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines')
	parser.add_argument('output_index', help='path to the outputted index. in the format pageID keyword score xmin ymin xmax ymax')
	parser.add_argument('--pages-path', nargs='+', help='path to page xml file associated with the index')
	parser.add_argument('--rec', type=int, default=-1, help='number of recursive merging. A value of -1 (Default) means go until it has converged')
	parser.add_argument('--min-overlap', type=float, default=0.5, help='minimum percentage of overlaping for 2 bbxs to be considered as intersecting')
	parser.add_argument('--min-intersection', type=float, default=0.2, help='minimum percentage of a bb intersecting with other bbxs in a group for a merge')
	parser.add_argument('--verbose', action='store_true', help='print the current page, keyword and step')
	parser.add_argument('--show-progress', action='store_true', help='print the current progress for each page')
	parser.add_argument('--minimum-score', type=float, default=0.00001, help='Only take into account pseudo-word with a score superior to that value')
	parser.add_argument('--index-format', choices=['frames', 'pixels'], default ='pixels', help='Format of the index file.')
	
	
	args = parser.parse_args()

def string_to_boolean(s):
	if s.lower() in ('yes', 'y', 'true', 't', '1'):
		return True
	elif s.lower() in ('no', 'n', 'false', 'f', '0'):
		return False
	else:
		raise argparse.ArgumentTypeError('Boolean value expected.')


	
def merge_bb_group(bb_list, keyword):
	total_mass = 0.0
	total_x = 0.0
	total_y = 0.0
	total_w = 0.0
	total_h = 0.0
	max_score = 0.0
	
	for bb in bb_list:
		xmin, ymin, xmax, ymax = bb.get_coords()
		
		# Compute the probability of a BB based on:
		overlap100 = total_overlap_percent(bb, bb_list) - 1.0 # Overlapping with other BBs
		pbop = sigmoid(overlap100, 8, 2.75)
		
		mean = 0.44 # TUNE
		std = 0.45 # TUNE
		
		pshape = proba_shape(bb, keyword, mean=mean, std=std) # The shape
		
		proba_beta = pbop * pshape
		
		score = bb.get_score() * proba_beta
		
		total_mass += score
		total_x += score * (xmax + xmin) / 2
		total_y += score * (ymax + ymin) / 2
		total_w += score*(xmax - xmin)
		total_h += score*(ymax - ymin)
		
		max_score = max(max_score, score)
	
	# Temporary solution to avoid division by 0
	if total_mass < 0.000001:
		return bb_list[0]
	
	# Weigthed average for the consolidated BB
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
	
def sort_beta_list(beta_list):
	n = len(beta_list)
	for i in range(n-1,-1,-1):
		for j in range(i):
			if beta_list[j].get_score() < beta_list[j+1].get_score():
				tmp_beta = beta_list[j]
				beta_list[j] = beta_list[j+1]
				beta_list[j+1] = tmp_beta



def sigmoid(x, a=1.0, b=0.0):
	return 1 / (1 + math.exp(-a*x+b))

def gaussian(x, mean, std):
	return np.exp(- ((x - mean) ** 2) / (2 * std ** 2))

def proba_shape(beta, keyword, mean=0.42, std=0.18):
	xmin, ymin, xmax, ymax = beta.get_coords()
	
	width = xmax - xmin + 1
	height = ymax - ymin + 1
	characters = len(keyword)
	
	width = float(width)
	height = float(height)
	characters = float(characters)
	
	char_ratio = width / (height * characters)
	
	return gaussian(char_ratio, mean, std)


# Give a score to each Consolidated BB
def scores(b, beta_list, keyword):
	
	# Sort the list
	sort_beta_list(beta_list)
	
	# Experimental probability
	#        p(1)    p(2)    p(3)    p(4)    p(5)    p(6)    p(7)    p(8)
	pnexp = [0.1069, 0.2375, 0.2694, 0.0862, 0.1226, 0.1221, 0.0516, 0.0036]
	
	# Compute relevance probability
	s = 0.0
	
	N = 8 # TUNE
	p = 0.7 # TUNE
	
	for n in range(1, min(len(beta_list), N)+1):
		pn = scipy.special.binom(N,n) * p ** n * (1 - p) ** (N - n)
		# ~ pn = pnexp[n-1] if n -1 < len(pnexp) else 0
		prod = 1
		
		# Keep a partition with the n best betas
		for beta in beta_list[:n]:
			
			mean = 0.44 # TUNE
			std = 0.45 # TUNE
			
			proba_beta = overlap_percent(beta, b) * proba_shape(beta, keyword, mean=mean, std=std)
			prod *= proba_beta * beta.get_score()
		
		s += prod*pn
	
	return s
	
	
	
	
	
bbxs_dict = {} # Store the BBs
line_dict = {} # Stocks line and their position info, their number of frames, ...

# Reading the index file
index_file = open(args.index_path, 'r')

if args.index_format == 'frames':
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
				line_width = line_xmax - line_xmin + 1
				
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



output = open(args.output_index, 'w')

for pageID in bbxs_dict:
	c = 0
	cm = len(bbxs_dict[pageID])
	for keyword in bbxs_dict[pageID]:
		c += 1
		if args.show_progress:
			print(str(c) + "/" + str(cm))
		bb_list = bbxs_dict[pageID][keyword]
		
		# Construct original bbxs lists
		original_bb_list = []
		for bb in bb_list:
			original_bb_list.append([bb])
		
		previous_len = 0
		i = 0
		
		while (previous_len != len(bb_list)) and ( i < args.rec or args.rec == -1):
			
			i += 1
			previous_len = len(bb_list)
			
			if args.verbose:
				print(pageID + " - " + keyword + " - Step " + str(i))
			
			bbxs_grps = []
			original_bbxs_grps = []
			
			# ~ for bb1 in bb_list:
			for i1 in range(len(bb_list)):
				bb1 = bb_list[i1]
				
				# Search for a bb that has an intersection with current bb
				is_bb_alone = True
				for i2 in range(len(bb_list)):
					bb2 = bb_list[i2]
					overlap = overlap_percent(bb1, bb2)
					if is_intersection_bb(bb1, bb2) and overlap > args.min_overlap and not bb_equal(bb1, bb2):
						is_bb_alone = False
						
						# Try to insert that couple of bounding box in every existing group of bounding box
						is_couple_new = True
						
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
									overlap = overlap_percent(bb1, bb)
									if overlap >= args.min_overlap:
										nbr_intersection1 += 1
								if is_intersection_bb(bb2, bb):
									overlap = overlap_percent(bb1, bb)
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
											overlap = overlap_percent(bb_tmp1, bb_tmp2)
											
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
				
				new_bb = merge_bb_group(bbxs_grp, keyword)
				
				merged_bb_list.append(new_bb)

			bb_list = merged_bb_list
			original_bb_list = bbxs_grps
		
		
		
		# Write results
		for b in bb_list:
			# pageID keyword score xmin ymin xmax ymax
			xmin, ymin, xmax, ymax = b.get_coords()
			score = b.get_score()
			
			if pageID in bbxs_dict and keyword in bbxs_dict[pageID]:
					
				# Construct list of betas overlapping with b
				beta_list = []
				for beta in bbxs_dict[pageID][keyword]:
					if is_intersection_bb(beta, b):
						overlap = overlap_percent(beta, b)
						if overlap > args.min_overlap:
							beta_list.append(beta)
			
				score = scores(b, beta_list, keyword)
			
			line_to_write = pageID + ' ' + keyword + ' ' + str(score) + ' ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + '\n'
			output.write(line_to_write)

output.close()
