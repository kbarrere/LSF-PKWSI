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
	parser.add_argument('--new-merge', type=int, default=0, help='Number of time to merge the close bounding box. -1 to do it until it converges')

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

def merge_bbs(bb1, bb2):
	xmin1, ymin1, xmax1, ymax1 = bb1.get_coords()
	xmin2, ymin2, xmax2, ymax2 = bb2.get_coords()
	score1 = bb1.get_score()
	score2 = bb2.get_score()
	
	bb = BB(min(xmin1, xmin2), min(ymin1, ymin2), max(xmax1, xmax2), max(ymax1, ymax2), max(score1, score2))
	return bb

def merge_bb_group(bb_list):
	bb = bb_list[0]
	for i in range(1, len(bb_list)):
		bb2 = bb_list[i]
		bb = merge_bbs(bb, bb2)
	
	return bb

def new_merge_bb_group(bb_list):
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
	
	# ~ xmin = int(center_x - center_w / 2)
	# ~ xmax = int(center_x + center_w / 2)
	# ~ ymin = int(center_y - center_h / 2)
	# ~ ymax = int(center_y + center_h / 2)
	xmin = center_x - center_w / 2
	xmax = center_x + center_w / 2
	ymin = center_y - center_h / 2
	ymax = center_y + center_h / 2
	
	# Trying to enlarge a bit the merged bounding box based on it's position compared to the bbxs creating it
	# ~ xmin_m = 0.0
	# ~ ymin_m = 0.0
	# ~ xmax_m = 0.0
	# ~ ymax_m = 0.0
	# ~ for bb in bb_list:
		# ~ xminbb, yminbb, xmaxbb, ymaxbb = bb.get_coords()
		# ~ scorebb = bb.get_score()
		# ~ xmin_m += scorebb*abs(xmin - xminbb)
		# ~ ymin_m += scorebb*abs(ymin - yminbb)
		# ~ xmax_m += scorebb*abs(xmax - xmaxbb)
		# ~ ymax_m += scorebb*abs(ymax - ymaxbb)
		# ~ if xmin > xminbb:
			# ~ xmin_m += scorebb * (xmin - xminbb)
		# ~ if ymin > yminbb:
			# ~ ymin_m += scorebb * (ymin - yminbb)
		# ~ if xmax < xmaxbb:
			# ~ xmax_m += scorebb * (xmax - xmaxbb)
		# ~ if ymax < ymaxbb:
			# ~ ymax_m += scorebb * (ymax - ymaxbb)
	
	# ~ xminvar = xmin_m / total_mass
	# ~ yminvar = ymin_m / total_mass
	# ~ xmaxvar = xmax_m / total_mass
	# ~ ymaxvar = ymax_m / total_mass
	
	# ~ xmin -= xminvar
	# ~ ymin -= yminvar
	# ~ xmax += xmaxvar
	# ~ ymax += ymaxvar
	
	bb = BB(int(xmin), int(ymin), int(xmax), int(ymax), max_score)
	return bb
	
def bb_equal(bb1, bb2):
	xmin1, ymin1, xmax1, ymax1 = bb1.get_coords()
	xmin2, ymin2, xmax2, ymax2 = bb2.get_coords()
	score1 = bb1.get_score()
	score2 = bb2.get_score()
	
	return (xmin1 == xmin2 and ymin1 == ymin2 and xmax1 == xmax2 and ymax1 == ymax2 and score1 == score2)

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


def draw_bb(img, bb, line_thickness=1, dx=0.1):
	xmin, ymin, xmax, ymax = bb.get_coords()
	score = bb.get_score()
	
	draw_box(img, xmin, ymin, xmax, ymax, line_thickness=line_thickness, color=score_to_color(score), dx=dx)


def score_to_color(score, bad_color=(255, 0, 0), good_color=(0, 255, 0)):
	output_color = []
	for c in range(len(bad_color)):
		output_color.append(int(bad_color[c] + score*(good_color[c]-bad_color[c])))
	
	return tuple(output_color)



img = Image.open(args.img_path)
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
bb_list = []
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
			
			bb = BB(xmin, ymin, xmax, ymax, p)
			bb_list.append(bb)
			
			# ~ line_coords=[[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]
			
			# ~ elements_found.append((keyword, p, line_coords))

bb_list_tmp1 = bb_list

for i in range(args.rec_merge):
	bb_list_list_tmp2 = []
	
	nbr_new = 0

	for bb1 in bb_list_tmp1:
		
		# Search for a bb that has an intersection with current bb
		is_bb_alone = True
		for bb2 in bb_list:
			if is_intersection_bb(bb1, bb2) and not bb_equal(bb1, bb2):
				is_bb_alone = False
				
				# Try to insert that couple of bounding box in every existing group of bounding box
				is_couple_new = True
				for bb_list_tmp2 in bb_list_list_tmp2:
					
					# ~ # Test if that couple can be inserted in that group
					is_bbs_match = True
					if bb1 not in bb_list_tmp2:
						for bb3 in bb_list_tmp2:
							if not is_intersection_bb(bb1, bb3):
								is_bbs_match = False
					if bb2 not in bb_list_tmp2:
						for bb3 in bb_list_tmp2:
							if not is_intersection_bb(bb2, bb3):
								is_bbs_match = False
					
					# Insert the couple in that group
					if is_bbs_match:
						is_couple_new = False
						if bb1 not in bb_list_tmp2:
							nbr_new += 1
							bb_list_tmp2.append(bb1)
						if bb2 not in bb_list_tmp2:
							nbr_new += 1
							bb_list_tmp2.append(bb2)
				
				# Create a new group is the couple match nowhere
				if is_couple_new:
					bb_list_list_tmp2.append([bb1, bb2])
			
		if is_bb_alone:
			bb_list_list_tmp2.append([bb1])
	
	# Merge the bounding boxes of one group into one big one
	merged_bb_list = []
	
	for bb_list_tmp2 in bb_list_list_tmp2:
		merged_bb_list.append(merge_bb_group(bb_list_tmp2))

	bb_list_tmp1 = merged_bb_list

bb_list = bb_list_tmp1

for i in range(args.new_merge):
	bb_list_list_tmp2 = []
	
	nbr_new = 0
	
	for bb1 in bb_list_tmp1:
		
		# Search for a bb that has an intersection with current bb
		is_bb_alone = True
		for bb2 in bb_list_tmp1:
			overlap = (overlap_percent(bb1, bb2) + overlap_percent(bb2, bb1) ) / 2
			# ~ if is_intersection_bb(bb1, bb2) and not bb_equal(bb1, bb2):
			if is_intersection_bb(bb1, bb2) and overlap > 0.5 and not bb_equal(bb1, bb2):
				is_bb_alone = False
				
				# Try to insert that couple of bounding box in every existing group of bounding box
				is_couple_new = True
				for bb_list_tmp2 in bb_list_list_tmp2:
					
					# Test if that couple can be inserted in that group
					# ~ is_bbs_match = True
					# ~ if bb1 not in bb_list_tmp2:
						# ~ for bb3 in bb_list_tmp2:
							# ~ if not is_intersection_bb(bb1, bb3):
								# ~ is_bbs_match = False
					# ~ if bb2 not in bb_list_tmp2:
						# ~ for bb3 in bb_list_tmp2:
							# ~ if not is_intersection_bb(bb2, bb3):
								# ~ is_bbs_match = False
					
					is_bbs_match = True
					
					# Build a temporary new group
					# ~ bbxs = []
					# ~ for bb in bb_list_tmp2:
						# ~ bbxs.append(bb)
					# ~ if bb1 not in bbxs or bb2 not in bbxs:
						# ~ if bb1 not in bbxs:
							# ~ bbxs.append(bb1)
						# ~ if bb2 not in bbxs:
							# ~ bbxs.append(bb2)
						
						# ~ nbr_bbxs = len(bbxs)
						# ~ for bb_tmp1 in bbxs:
							# ~ nbr_intersection = -1
							# ~ for bb_tmp2 in bbxs:
								# ~ if is_intersection_bb(bb_tmp1, bb_tmp2):
									# ~ overlap100 = overlap_percent(bb_tmp1, bb_tmp2)
									# ~ if overlap100 > 0.75:
										# ~ nbr_intersection += 1
							
							# ~ if nbr_intersection < 0.66 * (nbr_bbxs-1):
								# ~ is_bbs_match = False
					# ~ else:
						# ~ # If the couple is already in the group, do nothing
						# ~ is_bbs_match = False
						# ~ is_couple_new = False
					bbxs = []
					nbr_true_intersection_1 = 0
					nbr_true_intersection_2 = 0
					for bb in bb_list_tmp2:
						bbxs.append(bb)
						if is_intersection_bb(bb1, bb):
							# ~ overlap = (overlap_percent(bb1, bb) + overlap_percent(bb, bb1) ) / 2
							# ~ if overlap >= 0.5:
								# ~ nbr_true_intersection_1 += 1
							nbr_true_intersection_1 += 1
						if is_intersection_bb(bb2, bb):
							# ~ overlap = (overlap_percent(bb1, bb) + overlap_percent(bb, bb1) ) / 2
							# ~ if overlap >= 0.5:
								# ~ nbr_true_intersection_2 += 1
							nbr_true_intersection_2 += 1
					
					if (nbr_true_intersection_1 >= 1 and nbr_true_intersection_2 >= 1) or len(bbxs) == 0:
						if bb1 not in bbxs:
							bbxs.append(bb1)
						if bb2 not in bbxs:
							bbxs.append(bb2)
							
						nbr_bbxs = len(bbxs)
						for bb_tmp1 in bbxs:
							nbr_intersection = -1
							for bb_tmp2 in bbxs:
								if is_intersection_bb(bb_tmp1, bb_tmp2):
									overlap100 = (overlap_percent(bb_tmp1, bb_tmp2) + overlap_percent(bb_tmp2, bb_tmp1) ) / 2
									if overlap100 >= 0.5:
										nbr_intersection += 1
							
							if nbr_intersection < 0.2 * (nbr_bbxs-1):
								is_bbs_match = False
					else:
						is_bbs_match = False
					
					# Insert the couple in that group
					if is_bbs_match:
						is_couple_new = False
						if bb1 not in bb_list_tmp2:
							nbr_new += 1
							bb_list_tmp2.append(bb1)
						if bb2 not in bb_list_tmp2:
							nbr_new += 1
							bb_list_tmp2.append(bb2)
				
				# Create a new group is the couple match nowhere
				if is_couple_new:
					bb_list_list_tmp2.append([bb1, bb2])
			
		if is_bb_alone:
			bb_list_list_tmp2.append([bb1])
	
	# Merge the bounding boxes of one group into one big one
	merged_bb_list = []
	
	for bb_list_tmp2 in bb_list_list_tmp2:
		new_bb = new_merge_bb_group(bb_list_tmp2)
		merged_bb_list.append(new_bb)

	bb_list_tmp1 = merged_bb_list

bb_list = bb_list_tmp1


# Show bounding boxes and scores on the picture
for bb in bb_list:
	draw_bb(img, bb, line_thickness=args.bb_thickness)
	
	xmin, ymin, xmax, ymax = bb.get_coords()

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


