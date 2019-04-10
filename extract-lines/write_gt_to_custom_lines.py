import argparse
from xmlPAGE import *

if __name__ == '__main__':
	
	# Parse arguments
	parser.add_argument('custom_pages', nargs='+', help='path to page xml files associated with the custom line extraction')
	parser.add_argument('gt_pages', nargs='+', help='path to page xml files associated with the ground truth')
	parser.add_argument('output_path', nargs='+', help='path where to save the resultinge pages')

	args = parser.parse_args()
