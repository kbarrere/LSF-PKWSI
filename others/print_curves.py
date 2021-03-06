import argparse
import matplotlib.pyplot as plt
import numpy as np



# Parse arguments
parser = argparse.ArgumentParser(description='Create a csv file to plot curves from results of KWS in a text format')
parser.add_argument('kws_results', nargs='+', help='files containing the information')
parser.add_argument('--x',choices=['Threshold', 'Precision', 'Recall', 'F1-measure', 'Classif-ER', 'Fls-Alarm-Prob', 'Miss-Prob'], default='Recall', help='what data to use as the x axis')
parser.add_argument('--y',choices=['Threshold', 'Precision', 'Recall', 'F1-measure', 'Classif-ER', 'Fls-Alarm-Prob', 'Miss-Prob'], default='Precision', help='what data to use as the y axis')
parser.add_argument('--show-threshold', type=float, default=0.0, help='print points on the curves showing how the thresold increase regularly')
parser.add_argument('--link-threshold', action='store_true', help='Draw a curve between the sames theshold')
parser.add_argument('--format-2', action='store_true', help='Wheter to read the data as a two columns Precision Recall')

args = parser.parse_args()

metric = {'Threshold':0, 'Precision':1, 'Recall':2, 'F1-measure':3, 'Classif-ER':4, 'Fls-Alarm-Prob':5, 'Miss-Prob':6}
if args.format_2:
	metric = {'Precision':0, 'Recall':1}

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
				
				curr_threshold = 0.0
				if args.show_threshold > 0:
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

if args.link_threshold and len(args.kws_results) >= 2:
	threshold_line_x=[]
	threshold_line_y=[]
	
	for i in range(min(len(threshold_x[0]), len(threshold_x[1]))):
		line_x = [threshold_x[0][i], threshold_x[1][i]]
		line_y = [threshold_y[0][i], threshold_y[1][i]]
		
		threshold_line_x.append(line_x)
		threshold_line_y.append(line_y)
	
	for i in range(len(threshold_line_x)):
		plt.plot(threshold_line_x[i], threshold_line_y[i], 'r--')

plt.show()
