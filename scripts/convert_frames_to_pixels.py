import argparse
from xmlPAGE import *

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Convert frames to pixels')
	parser.add_argument('index_file', help='path to index file containing keywords, score and positioninng in the lines (in the format pageID.LineID keyword score startframe endframe totalframe')
	parser.add_argument('pages_path', nargs='+', help='path to page xml file associated to the image and the lines')
	parser.add_argument('output_index_file', help='path to the outputted index. In format pageID keyword score xmin ymin xmax ymax')	
	args = parser.parse_args()



def get_max_coords(coords):
	xmin = coords[0][0]
	ymin = coords[0][1]
	xmax = coords[0][0]
	ymax = coords[0][1]
	
	for i in range(1, len(coords)):
		x = coords[i][0]
		y = coords[i][1]
		
		xmin = min(xmin, x)
		ymin = min(ymin, y)
		xmax = max(xmax, x)
		ymax = max(ymax, y)
	
	return xmin, ymin, xmax, ymax


# Reading the index file
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
			
			line_xmin, line_ymin, line_xmax, line_ymax = get_max_coords(line_coords)
			
			line_width = line_xmax - line_xmin + 1
			
			if lineID in index_dict[pageID]:
				for detected in index_dict[pageID][lineID]:
					keyword, score, start_frame, end_frame, total_frame = detected
					
					# Create a bounding box
					xmin = int(line_xmin + float(start_frame)/float(total_frame)*line_width)
					xmax = int(line_xmin + float(end_frame)/float(total_frame)*line_width)
					ymin = line_ymin
					ymax = line_ymax
					
					line_to_write = pageID + ' ' + keyword + ' ' + str(score) + ' ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + '\n'
					output_index_file.write(line_to_write)
					
output_index_file.close()
