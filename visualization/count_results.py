import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Output the number, percentage and stats on the scores of TP, FP and FN')
	parser.add_argument('dat_file', help='file.dat containing the results of kws')
	
	args = parser.parse_args()



def compute_mean_std(scores):
	n = len(scores)
	
	# Compute mean
	s = 0.0
	for score in scores:
		s += score
	
	mean = s / float(n)
	
	# Compute std
	std = 42
	
	return mean, std
	
	


tp_scores = []

with open(args.dat_file, 'r') as dat_file:
	for line in dat_file:
		line = line[:-1]
		lineID, keyword, gtb_s, score_s = line.split(' ')
		
		# Convert to good type
		score = float(score_s)
		gtb = True if gtb_s == "1" else False
		
		# TP
		if gtb and score >= 0:
			tp_scores.append(score)

tp_mean, tp_std = compute_mean_std(tp_scores)
print("# TP: " + str(len(tp_scores)))
print("TP mean: " + str(tp_mean))
print("TP std: " + str(tp_std))
		
		
		
