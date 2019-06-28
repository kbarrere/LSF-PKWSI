import argparse
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Output the number, percentage and stats on the scores of TP, FP and FN')
	parser.add_argument('dat_file', help='file.dat containing the results of kws')
	parser.add_argument('--threshold', type=float, default=0.0, help='only the pseudo-words that has a score above that threshold will be taken into account')
	parser.add_argument('--fp-histogram', type=int, help='Plot an histogram of the false positives with the integer passed as an argument as the delimiter between values')
	
	args = parser.parse_args()



def compute_mean_std(scores):
	n = len(scores)
	
	# Compute mean
	s = 0.0
	for score in scores:
		s += score
	
	mean = -1
	if n > 0:
		mean = s / float(n)
	
	# Compute std
	s = 0
	for score in scores:
		s += (mean - score) ** 2.0
	
	std = -1
	if n > 0:
		std = (s / n) ** 0.5
	
	return mean, std
	
	


tp_scores = []
fp_scores = []
fn_scores = []
tn_scores = []
fn_nbr = 0

with open(args.dat_file, 'r') as dat_file:
	for line in dat_file:
		line = line[:-1]
		lineID, keyword, gtb_s, score_s = line.split(' ')[:4]
		
		# Convert to good type
		score = float(score_s)
		gtb = True if gtb_s == "1" else False
		
		# TP
		if gtb and score >= args.threshold:
			tp_scores.append(score)
			
		# FP
		if not gtb and score >= args.threshold:
			fp_scores.append(score)
		
		# FN
		if gtb and score < args.threshold:
			if score < 0.0:
				fn_nbr += 1
			else:
				fn_scores.append(score)
		
		# TN
		if not gtb and score < args.threshold:
			tn_scores.append(score)
			

tp_mean, tp_std = compute_mean_std(tp_scores)
fp_mean, fp_std = compute_mean_std(fp_scores)
fn_mean, fn_std = compute_mean_std(fn_scores)
tn_mean, tn_std = compute_mean_std(tn_scores)
detected = len(tp_scores) + len(fp_scores)
target_nbr = len(tp_scores) + fn_nbr + len(fn_scores)

print("===============================")
print("# Detected: " + str(detected))
print("# To dectect: " + str(target_nbr))
print("-------------------------------")
print("# TP: " + str(len(tp_scores)))
if detected > 0:
	print("% TP: " + str(float(len(tp_scores)) / float(detected)))
print("TP score mean: " + str(tp_mean))
print("TP score std: " + str(tp_std))
print("-------------------------------")
print("# FP: " + str(len(fp_scores)))
if detected > 0:
	print("% FP: " + str(float(len(fp_scores)) / float(detected)))
print("FP score mean: " + str(fp_mean))
print("FP score std: " + str(fp_std))
print("-------------------------------")
print("# FN: " + str(fn_nbr + len(fn_scores)))
print("# Positives not detected at all: " + str(fn_nbr))
if target_nbr > 0:
	print("% FN: " + str(float(fn_nbr + len(fn_scores)) / float(target_nbr)))
print("FN score mean: " + str(fn_mean))
print("FN score std: " + str(fn_std))
print("-------------------------------")
print("# TN: " + str(len(tn_scores)))
print("TN score mean: " + str(tn_mean))
print("TN score std: " + str(tn_std))

if args.fp_histogram:
	plt.hist(fp_scores, bins=args.fp_histogram)
	plt.show()
