import argparse
import matplotlib.pyplot as plt
import numpy as np



# Parse arguments
parser = argparse.ArgumentParser(description='Create a csv file to plot curves from results of KWS in a text format')
parser.add_argument('kws_results', nargs='+', help='files containing the information')
parser.add_argument('--x',choices=['Threshold', 'Precision', 'Recall', 'F1-measure', 'Classif-ER', 'Fls-Alarm-Prob', 'Miss-Prob'], default='Recall', help='what data to use as the x axis')
parser.add_argument('--y',choices=['Threshold', 'Precision', 'Recall', 'F1-measure', 'Classif-ER', 'Fls-Alarm-Prob', 'Miss-Prob'], default='Precision', help='what data to use as the y axis')
parser.add_argument('--show-threshold', type=float, default=0.0, help='print points on the curves showing how the thresold increase regularly')

args = parser.parse_args()

metric = {'Threshold':0, 'Precision':1, 'Recall':2, 'F1-measure':3, 'Classif-ER':4, 'Fls-Alarm-Prob':5, 'Miss-Prob':6}

x_metric = metric[args.x]
y_metric = metric[args.y]

plt.xlabel(args.x)
plt.ylabel(args.y)
plt.ylim(0, 1)
plt.xlim(0, 1)

threshold_x = []
threshold_y = []

for kws_result_file in args.kws_results:
	
	with open(kws_result_file, 'r') as kws_result:
		if args.show_threshold > 0:
			threshold_x.append([])
			threshold_y.append([])
		
		x_axis = []
		y_axis = []
		
		threshold_i = 0
				
		for line in kws_result:
			
			if len(line) > 0 and line[0] != '#':
				row = []
				
				line = line[:-1]
				line_split = line.split('\t')
				for score in line_split:
					if len(score) > 0:
						row.append(float(score))
				
				x_axis.append(row[x_metric])
				y_axis.append(row[y_metric])
				
				curr_threshold = row[metric['Threshold']]
				
				if args.show_threshold > 0:
					while threshold_i*args.show_threshold < curr_threshold:
						threshold_x[-1].append(row[x_metric])
						threshold_y[-1].append(row[y_metric])
						threshold_i += 1
	
		plt.plot(x_axis, y_axis)
		
if args.show_threshold > 0:
	for i in range(len(threshold_x)):
		plt.plot(threshold_x[i], threshold_y[i], 'x')

plt.show()
