import argparse

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Compare two results of KWS.')
	parser.add_argument('result1', help='First file to compare.')
	parser.add_argument('result2', help='Second file to compare.')
	
	args = parser.parse_args()

dict1 = {}

file1 = open(args.result1, 'r')

for line in file1:
	line = line[:-1]
	pageID, keyword, hit_str, score_str = line.split(' ')
	hit = False
	if hit_str == '1':
		hit = True
	score = float(score_str)
	
	if pageID not in dict1:
		dict1[pageID] = {}
	dict1[pageID][keyword] = (hit, score)

file1.close()

dict2 = {}

file2 = open(args.result2, 'r')

for line in file2:
	line = line[:-1]
	pageID, keyword, hit_str, score_str = line.split(' ')
	hit = False
	if hit_str == '1':
		hit = True
	score = float(score_str)
	
	if pageID not in dict2:
		dict2[pageID] = {}
	dict2[pageID][keyword] = (hit, score)

file2.close()

