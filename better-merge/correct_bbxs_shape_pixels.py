import argparse
import numpy as np
from xmlPAGE import *

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Correct the shape of the bonding boxes')
	parser.add_argument('index_file', help='path to index file containing keywords, score and positioninng in the lines (in the format pageID.LineID keyword score startframe endframe totalframe')
	parser.add_argument('--pages-path', nargs='+', help='path to page xml file associated to the image and the lines')
	parser.add_argument('output_index_file', help='path to the outputted index.')
	parser.add_argument('--mean', type=float, default=29.7175, help='mean of the gaussian of number of frames per character')
	parser.add_argument('--std', type=float, default=13.7702, help='std of the gaussian of number of frames per character')
	parser.add_argument('--threshold', type=float, default=0.05, help='If the gaussian score is below that value, correct it')
	parser.add_argument('--index-format', choices=['frames', 'pixels'], default ='frames', help='Format of the index file.')
	
	args = parser.parse_args()



delta = args.std * ( -2 * np.log(args.threshold)) ** 0.5
x1 = args.mean - delta
x2 = args.mean + delta

print("x1: " + str(x1))
print("x2: " + str(x2))

# Reading the index file
if args.index_format=='frames':
	index_file = open(args.index_file, 'r')
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



	output_index_file = open(args.output_index_file, 'w')

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
						
						width = xmax - xmin
						
						nbr_characters = len(keyword)
						
						if width < x1 * nbr_characters:
							xmin = int(xmax - x1 * nbr_characters)
						elif width > x2 * nbr_characters:
							xmin = int(xmax - x2 * nbr_characters)
						
						line_to_write = pageID + ' ' + keyword + ' ' + str(score) + ' ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + '\n'
						output_index_file.write(line_to_write)
						
	output_index_file.close()

elif args.index_format=='pixels':
	output_index_file = open(args.output_index_file, 'w')
	index_file = open(args.index_file, 'r')
	
	for line in index_file:
		line = line[:-1]
		
		pageID, keyword, score_str, xmin_str, ymin_str, xmax_str, ymax_str = line.split(' ')
		xmin = int(xmin_str)
		ymin = int(ymin_str)
		xmax = int(xmax_str)
		ymax = int(ymax_str)
		
		nbr_characters = len(keyword)
		
		width = xmax - xmin + 1
		
		if width < x1 * nbr_characters:
			xmin = int(xmax - x1 * nbr_characters)
		elif width > x2 * nbr_characters:
			xmin = int(xmax - x2 * nbr_characters)
		
		line_to_write = pageID + ' ' + keyword + ' ' + score_str + ' ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + '\n'
		output_index_file.write(line_to_write)
		
	index_file.close()
	output_index_file.close()
