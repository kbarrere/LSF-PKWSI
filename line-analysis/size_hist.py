import argparse
import matplotlib.pyplot as plt

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Create an histogram of the width of the images')
	parser.add_argument('identify_file', help='path to the file containing the results of the identify command')
	parser.add_argument('--bins', default=10, type=int, help='Number of delimiter')
	
size = []

identify_file = open(args.identify_file, 'r')

for line in identify_file:
	line = line[:-1]
	print(line)


	
	
