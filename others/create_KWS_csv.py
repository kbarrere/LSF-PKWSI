import csv
import argparse



# Parse arguments
parser = argparse.ArgumentParser(description='Create a csv file from results of KWS in a text format')
parser.add_argument('kws_results', nargs='+', help='file containing results of KWS in a text format')
parser.add_argument('output_csv', help='outputed csv file')

args = parser.parse_args()


with open(args.output_csv, 'wb') as csvfile:
	filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	
	# Title
	cols_name=['File', 'MAP', '#Rel-Wrds', 'AP', 'RP', 'F1max', 'RCmax', 'PRres', 'CERmin', 'CER(>1.0)']
	cols_ind={'File':0, 'MAP':1, '#Rel-Wrds':2, 'AP':3, 'RP':4, 'F1max':5, 'RCmax':6, 'PRres':7, 'CERmin':8, 'CER(>1.0)':9}
	n_columns= len(cols_name)
	filewriter.writerow(cols_name)
	
	for kws_result in args.kws_results:
		
		row = [''] * n_columns
		
		row[cols_ind['File']] = kws_result
		
		with open(kws_result, 'r') as kws_result:
			
			for line in kws_result:
				line = line[:-1]
				line_splitted = line.split('=')
				metric = line_splitted[0]
				
				if 'MAP' in metric:
					line_splitted_2 = line_splitted[1].split(' ')
					map_score = line_splitted_2[1]
					row[cols_ind['MAP']] = map_score
					
					line_splitted_3 = line_splitted[2].split(' ')
					nbr_rel_words = line_splitted_3[1]
					row[cols_ind['#Rel-Wrds']] = nbr_rel_words
				
				if 'AP' in metric and 'MAP' not in metric:
					line_splitted_2 = line_splitted[1].split(' ')
					ap_score = line_splitted_2[1]
					row[cols_ind['AP']] = ap_score
				
				if 'RP' in metric:
					line_splitted_2 = line_splitted[1].split(' ')
					rp_score = line_splitted_2[1]
					row[cols_ind['RP']] = rp_score
				
				if 'F1max' in metric:
					line_splitted_2 = line_splitted[1].split(' ')
					f1max_score = line_splitted_2[1]
					row[cols_ind['F1max']] = f1max_score
				
				if 'RCmax' in metric:
					line_splitted_2 = line_splitted[1].split(' ')
					rcmax_score = line_splitted_2[1]
					row[cols_ind['RCmax']] = rcmax_score
				
				if 'PRres' in metric:
					line_splitted_2 = line_splitted[1].split(' ')
					prres_score = line_splitted_2[1]
					row[cols_ind['PRres']] = prres_score
				
				if 'CERmin' in metric:
					line_splitted_2 = line_splitted[1].split(' ')
					cermin_score = line_splitted_2[1]
					row[cols_ind['CERmin']] = cermin_score
				
				if 'CER(>1.0)' in metric:
					line_splitted_2 = line_splitted[1].split(' ')
					cer_score = line_splitted_2[1]
					row[cols_ind['CER(>1.0)']] = cer_score
			
			filewriter.writerow(row)
				
				
			
