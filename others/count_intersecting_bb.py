import argparse
import matplotlib.pyplot as plt

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Merge Bounding boxes. Version 4, only using Geometry rules')
	parser.add_argument('merged_index', help='path to index file containing keywords, score and positioninng in the lines')
	parser.add_argument('raw_index', help='path to index file containing keywords, score and positioninng in the lines')
	parser.add_argument('--min-overlap', type=float, default=0.5, help='minimum percentage of overlaping for 2 bbxs to be considered as intersecting')
	parser.add_argument('--bins', default=10, type=int, help='Number of delimiter')
	
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
	
	base_area1 = (xmax1 - xmin1) * (ymax1 - ymin1)
	base_area2 = (xmax2 - xmin2) * (ymax2 - ymin2)
	area = (xmax - xmin) * (ymax - ymin)
	
	union_area = (float(base_area1)+float(base_area2)-float(area))
	
	percentage = 0.0
	if union_area > 0.0:
		percentage = float(area)/union_area
	
	return percentage



raw_bbs = {}

with open(args.raw_index, 'r') as index_file:
	for line in index_file:
		line = line[:-1]
		pageID, keyword, score_str, xmin_str, ymin_str, xmax_str, ymax_str = line.split(' ')
		
		score = float(score_str)
		xmin = int(xmin_str)
		ymin = int(ymin_str)
		xmax = int(xmax_str)
		ymax = int(ymax_str)
		
		bb = BB(xmin, ymin, xmax, ymax, score)
		
		if pageID not in raw_bbs:
			raw_bbs[pageID] = {}
		if keyword not in raw_bbs[pageID]:
			raw_bbs[pageID][keyword] = []
		
		raw_bbs[pageID][keyword].append(bb)



total = 0
count = 0
hist_data=[]



with open(args.merged_index, 'r') as index_file:
	for line in index_file:
		line = line[:-1]
		pageID, keyword, hit, score_str, xmin_str, ymin_str, xmax_str, ymax_str = line.split(' ')
		
		score = float(score_str)
		xmin = int(xmin_str)
		ymin = int(ymin_str)
		xmax = int(xmax_str)
		ymax = int(ymax_str)
		
		b = BB(xmin, ymin, xmax, ymax, score)
		
		if pageID in raw_bbs and keyword in raw_bbs[pageID]:
			c = 0
			
			for beta in raw_bbs[pageID][keyword]:
				if is_intersection_bb(b, beta) and overlap_percent(b, beta) > args.min_overlap:
					c += 1
			
			total += c
			count += 1
			hist_data.append(c)

print("Total: " + str(total))
print("Count: " + str(count))

array, _, _ = plt.hist(hist_data, bins=args.bins, normed=False)
print(array)
plt.show()

