import argparse
import matplotlib.pyplot as plt

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Create an histogram of the width of the images')
	parser.add_argument('identify_file', help='path to the file containing the results of the identify command')
	parser.add_argument('--bins', default=10, type=int, help='Number of delimiter')
	
	args = parser.parse_args()
	
sizes = []

identify_file = open(args.identify_file, 'r')

for line in identify_file:
	line = line[:-1]
	size = line.split(' ')[2]
	w_str, h_str = size.split('x')
	w = int(w_str)
	h = int(h_str)
	
	sizes.append(w)

plt.hist(sizes, bins=args.bins)
plt.title('Histogram of the processed lines width (S_Landau 5214x3396)')
plt.xlabel('Width (in pixels)')
plt.ylabel('Number of lines')
plt.show()

