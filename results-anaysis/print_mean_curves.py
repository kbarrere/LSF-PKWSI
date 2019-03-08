import argparse
import matplotlib.pyplot as plt



# Parse arguments
parser = argparse.ArgumentParser(description='Create a csv file to plot curves from results of KWS in a text format')
parser.add_argument('kws_results', nargs='+', help='files containing the information')
parser.add_argument('--x',choices=['Threshold', 'Precision', 'Recall', 'F1-measure', 'Classif-ER', 'Fls-Alarm-Prob', 'Miss-Prob'], default='Recall', help='what data to use as the x axis')
parser.add_argument('--y',choices=['Threshold', 'Precision', 'Recall', 'F1-measure', 'Classif-ER', 'Fls-Alarm-Prob', 'Miss-Prob'], default='Precision', help='what data to use as the y axis')
parser.add_argument('--n', type=int, default=100, help='nu,ber of point to print at the end')

args = parser.parse_args()

global_x_axis = []
global_y_axis = []

metric = {'Threshold':0, 'Precision':1, 'Recall':2, 'F1-measure':3, 'Classif-ER':4, 'Fls-Alarm-Prob':5, 'Miss-Prob':6}

x_metric = metric[args.x]
y_metric = metric[args.y]

plt.xlabel(args.x)
plt.ylabel(args.y)
plt.ylim(0, 1)
plt.xlim(0, 1)

range_x = []
for i in range(args.n):
	x = float(i) / float(args.n) 
	range_x.append(x)

sum_y = [0.0] * args.n

n = 0

for kws_result_file in args.kws_results:
	
	with open(kws_result_file, 'r') as kws_result:
		
		x_axis = []
		y_axis = []
		
		for line in kws_result:
			if len(line) > 0 and line[0] != '#':
				row = []
				
				line = line[:-1]
				line_split = line.split('\t')
				for score in line_split:
					if len(score) > 0:
						row.append(score)
				
				x_axis.append(float(row[x_metric]))
				y_axis.append(float(row[y_metric]))
		
		if len(x_axis) > 0:
			n += 1
			
			# Do a sort of x_axis and y_axis depending of x_axis values
			for i in range(len(x_axis)-1, -1, -1):
				for j in range(i):
					if x_axis[j] > x_axis[j+1]:
						tmp = x_axis[j]
						x_axis[j] = x_axis[j+1]
						x_axis[j+1] = tmp
						
						tmp = y_axis[j]
						y_axis[j] = y_axis[j+1]
						y_axis[j+1] = tmp
			
			
			j = 0
			value = 1
			for i in range(args.n - 1):
				xmin = range_x[i]
				xmax = range_x[i+1]
				
				c = 0
				summed_value = 0.0
				while j < len(x_axis)-1 and x_axis[j] < xmax:
					summed_value += y_axis[j]
					j += 1
					c += 1
				
				if c > 0:
					value = summed_value / c
				
				sum_y[i] += value
		
		else:
			print("ERROR ! Cannot get value from file " +  kws_result_file)
	
y_mean = []		
for y in sum_y:
	y_mean.append(y / n)

plt.plot(range_x, y_mean)
plt.show()
