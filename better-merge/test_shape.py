import argparse
import matplotlib.pyplot as plt

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Some quick stats about bb shapes')
	parser.add_argument('input_index', help='path to the input index. In the format pageID keyword score xmin ymin xmax ymax')
	parser.add_argument('--bins', default=10, type=int, help='Number of delimiter')
	
	args = parser.parse_args()



input_index = open(args.input_index, 'r')

char_ratios = []

for line in input_index:
	line = line[:-1]
	
	pageID, keyword, hit, score, xmin_str, ymin_str, xmax_str, ymax_str = line.split(' ')
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
	char_ratios.append(char_ratio)

input_index.close()

total = 0.0
for v in char_ratios:
	total += v
mean = total / len(char_ratios)
print("Mean: " + str(mean))

total = 0.0
for v in char_ratios:
	total += (v - mean) ** 2
std = (total / len(char_ratios)) ** 0.5
print("Std: " + str(std)) 


plt.hist(char_ratios, bins=args.bins, normed=True)
plt.show()
