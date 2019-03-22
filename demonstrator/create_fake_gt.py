import argparse
from xmlPAGE import *

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Create a fake GT for each lines. So that it can be indexed later for using the demonstator')
	parser.add_argument('page_path', nargs='+', help='path to page xml file associated to the image and the lines')
	parser.add_argument('resulting_fake_gt', help='File in which to write the results')
	parser.add_argument('--gt', default='Definitly not the ground truth', help='what to print in the ground truth')

	args = parser.parse_args()

with open(args.resulting_fake_gt, 'w') as output:
	for page_file in args.page_path:
		# Get page ID
		page_id = page_file.split('/')[-1].split('.')[0]
		
		# Open and Page XML
		page = pageData(page_file)
		page.parse()
		textline_elements = page.get_region('TextLine')
		
		# Loop over all lines
		for textline_element in textline_elements:
			# Get line ID
			textline_element_id = page.get_id(textline_element)
			line_id = page_id + '.' + textline_element_id
			
			# Get coords
			line_coords = page.get_coords(textline_element)
			line_xmin, line_ymin = line_coords[0]
			line_xmax, line_ymax = line_coords[2]
			
			# Write inside the file :
			line_to_write = page_id + " " + line_id + " " + str(line_xmin) + " " + str(line_ymin) + " " + str(line_xmax) + " " + str(line_ymax) + " " + args.gt + "\n"
			output.write(line_to_write)
