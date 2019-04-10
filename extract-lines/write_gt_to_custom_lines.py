import argparse
from xmlPAGE import *

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Take the GT and write it inside custom lines')
	parser.add_argument('custom_page', help='path to page xml file associated with the custom line extraction')
	parser.add_argument('gt_page', help='path to page xml file associated with the ground truth')
	parser.add_argument('output_path', help='path where to save the resulting page')

	args = parser.parse_args()

print(args.custom_pages)
print(args.gt_pages)
print(args.output_path)
