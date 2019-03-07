import argparse
import matplotlib.pyplot as plt



# Parse arguments
parser = argparse.ArgumentParser(description='Create a csv file to plot curves from results of KWS in a text format')
parser.add_argument('kws_result', help='file containing the information')

args = parser.parse_args()



precision = []
recall = []

with open(args.kws_result, 'r') as kws_result:
	
	for line in kws_result:
		if len(line) > 0 and line[0] != '#':
			row = []
			
			line = line[:-1]
			line_split = line.split('\t')
			for score in line_split:
				if len(score) > 0:
					row.append(score)
			
			precision.append(row[1])
			recall.append(row[2])

plt.plot(recall, precision, label='rp-curve')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim(0, 1)
plt.xlim(0, 1)
plt.show()
