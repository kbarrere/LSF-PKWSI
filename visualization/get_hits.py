import argparse
from xmlPAGE import *



if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Print Bounding boxes for the given index file and image')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines')
	parser.add_argument('page_path', help='path to page xml file associated to the image and the lines')
	parser.add_argument('gt', help='path to the Ground Truth (GT)')

	args = parser.parse_args()

# Read the index
with open(args.index_path, 'r') as index_file:
	for line in index_file:
		line = line[:-1]
		pageIDlineID, keyword, score, start_frame, end_frame, total_frame = line.split(' ')
