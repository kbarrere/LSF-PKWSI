import argparse
import numpy as np

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Some quick stats about bb shapes')
	parser.add_argument('input_index', help='path to the input index. In the format pageID keyword score xmin ymin xmax ymax')
	parser.add_argument('output_index', help='path to the output index. In the format pageID keyword score xmin ymin xmax ymax')
	parser.add_argument('--mean', type=float, default=0.42, help='mean of the gaussian of aspect ratio per character')
	parser.add_argument('--std', type=float, default=0.18, help='std of the gaussian of aspect ratio per character')
	
	args = parser.parse_args()

def gaussian(x, mean, std):
	return np.exp(- ((x - mean) ** 2) / (2 * std ** 2))



input_index = open(args.input_index, 'r')
output_index = open(args.output_index, 'w')

for line in input_index:
	line = line[:-1]
	
	pageID, keyword, index_score_str, xmin_str, ymin_str, xmax_str, ymax_str = line.split(' ')
	index_score = float(index_score_str)
	xmin = int(xmin_str)
	ymin = int(ymin_str)
	xmax = int(xmax_str)
	ymax = int(ymax_str)
	
	width = xmax - xmin + 1
	height = ymax - ymin + 1
	characters = len(keyword)
	
	width = float(width)
	height = float(height)
	characters = float(characters)
	
	char_ratio = width / (height * characters)
	
	pbs = gaussian(char_ratio, args.mean, args.std)
	
	score = pbs * index_score
	
	line_to_write = pageID + ' ' + keyword + ' ' + str(score) + ' ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + '\n'
	output_index.write(line_to_write)
	
input_index.close()
output_index.close()
