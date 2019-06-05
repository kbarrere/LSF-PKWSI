import argparse

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Merge Bounding boxes. Version 4, only using Geometry rules')
	parser.add_argument('input_index', help='path to the input index. In the format pageID keyword score xmin ymin xmax ymax')
	parser.add_argument('output_index', help='path to the outputted index. In the format pageID keyword score xmin ymin xmax ymax')
	
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
	
	def set_score(self, score):
		self.score = score
	
	def __repr__(self):
		return "BB("+self.__str__()+")"
	
	def __str__(self):
		return "xmin="+str(self.xmin)+" ymin="+str(self.ymin)+" xmax="+str(self.xmax)+" ymax="+str(self.ymax)+" score="+str(self.score)

def bb_equal(bb1, bb2):
	xmin1, ymin1, xmax1, ymax1 = bb1.get_coords()
	xmin2, ymin2, xmax2, ymax2 = bb2.get_coords()
	
	return (xmin1 == xmin2 and ymin1 == ymin2 and xmax1 == xmax2 and ymax1 == ymax2)

def bb_equal_strict(bb1, bb2):
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



# Index the index
input_index = open(args.input_index, 'r')

bb_dict = {}

for line in input_index:
	line = line[:-1]
	
	pageID, keyword, score_str, xmin_str, ymin_str, xmax_str, ymax_str = line.split(' ')
	
	score = float(score_str)
	xmin = int(xmin_str)
	ymin = int(ymin_str)
	xmax = int(xmax_str)
	ymax = int(ymax_str)
	
	bb = BB(xmin, ymin, xmax, ymax, score)
	
	if pageID not in bb_dict:
		bb_dict[pageID] = {}
	if keyword not in bb_dict[pageID]:
		bb_dict[pageID][keyword] = []
	bb_dict[pageID][keyword].append(bb)

input_index.close()



# Merge the bbs
output_index = open(args.output_index, 'w')

for pageID in bb_dict:
	for keyword in bb_dict[pageID]:
		
		groups = []
		
		for bb in bb_dict[pageID][keyword]:
			
			first_group = -1
			groups2 = []
			
			# Try to insert the bb in a group
			for i in range(len(groups)):
				group = groups[i]
				
				is_intersection = False
				
				# Test if bb is intersecting with one of the bbs off the group
				for bbg in group:
					if is_intersection_bb(bb, bbg):
						is_intersection = True
						break
				
				if is_intersection:
					if first_group == -1:
						# Merge bb and the group
						first_group = i
						group.append(bb)
						groups2.append(group)
					else:
						# Merge bb and the two intersecting group
						groups2[first_group].append(bb)
						for bbg in group:
							groups2[first_group].append(bbg)
				else:
					groups2.append(group)

			# Create a new group if no one match
			if first_group == -1:
				groups2.append([bb])
			
			groups = groups2
		
		# Merge the bbs inside each group
		for group in groups:
			bb = merge_bb_group(group)
			
			xmin, ymin, xmax, ymax = bb.get_coords()
			score = bb.get_score()
			
			line_to_write = pageID + ' ' + keyword + ' ' + str(score) + ' ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + '\n'
			output_index.write(line_to_write)
			
				
