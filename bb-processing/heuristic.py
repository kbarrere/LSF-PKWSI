import argparse


if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Print Bounding boxes for the given index file and image')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines')
	
	args = parser.parse_args()

with open(args.index_path, 'r') as index_file:
	for line in index_file:
		line = line[:-1]
		print(line)
