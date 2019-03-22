if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Create a fake GT for each lines. So that it can be indexed later for using the demonstator')
	parser.add_argument('page_path', nargs='+', help='path to page xml file associated to the image and the lines')
	parser.add_argument('--gt', default='Definitly not the ground truth', help='what to print in the ground truth')

	args = parser.parse_args()

for page_file in args.page_path:
	with open(page_file, 'r') as page:
		for line in page:
			line = line[:-1]
			print(line)
