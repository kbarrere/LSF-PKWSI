import argparse



if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Print an histogram of the detected bounding box width divided by the size of the detected word.')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines')
	parser.add_argument('data_path', help='path to index file containing keywords, score and positioninng in the lines')
	
	args = parser.parse_args()


data_file = open(args.data_path, 'r')

for line in data_file:
	line = line[:-1]
	print(line)

data_file.close()
