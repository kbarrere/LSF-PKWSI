import argparse
import matplotlib.pyplot as plt



# Parse arguments
parser = argparse.ArgumentParser(description='Create a csv file to plot curves from results of KWS in a text format')
parser.add_argument('kws_result', help='file containing the information')
parser.add_argument('--x',choices=['Threshold', 'Precision', 'Recall', 'F1-measure', 'Classif-ER', 'Fls-Alarm-Prob', 'Miss-Prob'], default='Recall', help='what data to use as the x axis')
parser.add_argument('--y',choices=['Threshold', 'Precision', 'Recall', 'F1-measure', 'Classif-ER', 'Fls-Alarm-Prob', 'Miss-Prob'], default='Precision', help='what data to use as the y axis')

args = parser.parse_args()



x_axis = []
y_axis = []

metric = {'Threshold':0, 'Precision':1, 'Recall':2, 'F1-measure':3, 'Classif-ER':4, 'Fls-Alarm-Prob':5, 'Miss-Prob':6}

x_metric = metric[args.x]
y_metric = metric[args.y]

with open(args.kws_result, 'r') as kws_result:
	
	for line in kws_result:
		if len(line) > 0 and line[0] != '#':
			row = []
			
			line = line[:-1]
			line_split = line.split('\t')
			for score in line_split:
				if len(score) > 0:
					row.append(score)
			
			x_axis.append(row[x_metric])
			y_axis.append(row[y_metric])

plt.plot(x_axis, y_axis)
plt.xlabel(args.x)
plt.ylabel(args.y)
plt.ylim(0, 1)
plt.xlim(0, 1)
plt.show()
