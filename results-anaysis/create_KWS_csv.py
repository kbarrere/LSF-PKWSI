import csv
import argparse



# Parse arguments
parser = argparse.ArgumentParser(description='Create a csv file from results of KWS in a text format')
parser.add_argument('kws_result', help='file containing results of KWS in a text format')
parser.add_argument('output_csv', help='outputted csv file')

args = parser.parse_args()


with open(args.output_csv, 'wb') as csvfile:
	filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	
	# Title
	cols_name=['MAP', '#Rel-Wrds', 'AP', 'RP', 'F1max', 'RCmax', 'PRres', 'CERmin', 'CER(>1.0)']
	cols_ind={'MAP':0, '#Rel-Wrds':1, 'AP':2, 'RP':3, 'F1max':4, 'RCmax':5, 'PRres':6, 'CERmin':7, 'CER(>1.0)':8}
	n_score = len(cols_name)
	filewriter.writerow(cols_name)
	
	with open(args.kws_result, 'r') as kws_result:
		
		scores = [''] * n_score
		
		for line in kws_result:
			line = line[:-1]
			line_splitted = line.split('=')
			metric = line_splitted[0]
			
			if 'MAP' in metric:
				line_splitted_2 = line_splitted[1].split(' ')
				map_score = line_splitted_2[1]
				scores[cols_ind['MAP']] = map_score
				
				line_splitted_3 = line_splitted[2].split(' ')
				nbr_rel_words = line_splitted_3[1]
				scores[cols_ind['#Rel-Wrds']] = nbr_rel_words
			
			if 'AP' in metric and 'MAP' not in metric:
				line_splitted_2 = line_splitted[1].split(' ')
				ap_score = line_splitted_2[1]
				scores[cols_ind['AP']] = ap_score
			
			if 'RP' in metric:
				line_splitted_2 = line_splitted[1].split(' ')
				rp_score = line_splitted_2[1]
				scores[cols_ind['RP']] = rp_score
			
			if 'F1max' in metric:
				line_splitted_2 = line_splitted[1].split(' ')
				f1max_score = line_splitted_2[1]
				scores[cols_ind['F1max']] = f1max_score
			
			if 'RCmax' in metric:
				line_splitted_2 = line_splitted[1].split(' ')
				rcmax_score = line_splitted_2[1]
				scores[cols_ind['RCmax']] = rcmax_score
		
		filewriter.writerow(scores)
				
				
			
