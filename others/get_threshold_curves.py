import csv
import argparse



# Parse arguments
parser = argparse.ArgumentParser(description='Create a csv file to plot curves from results of KWS in a text format')
parser.add_argument('kws_result', help='file containing the information')
parser.add_argument('output_csv', help='outputed csv file')

args = parser.parse_args()


with open(args.output_csv, 'wb') as csvfile:
	filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	
	# Title
	cols_name=['Threshold', 'Precision', 'Recall', 'F1-measure', 'Classif-ER', 'FLs-Alarm-Prob', 'Miss-Prob']
	n_columns= len(cols_name)
	
	cols_ind={}
	for i in range(n_columns):
		cols_ind[cols_name[i]] = i
	
	filewriter.writerow(cols_name)
	
	with open(args.kws_result, 'r') as kws_result:
	
		for line in kws_result:
			if len(line) > 0 and line[0] != '#':
				row = []
				
				line = line[:-1]
				line_split = line.split('\t')
				for score in line_split:
					if len(score) > 0:
						row.append(score)
				
				filewriter.writerow(row)	
