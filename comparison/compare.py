import argparse

if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Compare two results of KWS.')
	parser.add_argument('result1', help='First file to compare.')
	parser.add_argument('result2', help='Second file to compare.')
	parser.add_argument('--top', type=int, default=3, help='Show the top X (Default is 3) examples for each test.')
	
	args = parser.parse_args()

print("===============================================================")
print("Reading first file...")

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

print("Reading second file...")

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

def sort(l):
	n = len(l)
	for i in range(n-1):
		for j in range(i):
			diff1, pageID1, keyword1 = l[j]
			diff2, pageID2, keyword2 = l[j+1]
			if diff1 < diff2:
				l[j] = (diff2, pageID2, keyword2)
				l[j+1] = (diff1, pageID1, keyword1)

# When method 1 successes only
print("---------------------------------------------------------------")
print("Computing example when method 1 find something and not method 2")

only1 = []

for pageID in dict1:
	for keyword in dict1[pageID]:
		hit1, score1 = dict1[pageID][keyword]
		if hit1 and score1 != -1:
			if pageID in dict2 and keyword in dict2[pageID]:
				hit2, score2 = dict2[pageID][keyword]
				if score2 == -1:
					only1.append((score1, pageID, keyword))

print("Find " + str(len(only1)) + " examples")
print("Obtaining the best " + str(args.top))
sort(only1)

for i in range(min(len(only1), args.top)):
	print(only1[i])


# When method 2 successes only
print("---------------------------------------------------------------")
print("Computing example when method 2 find something and not method 1")

only2 = []

for pageID in dict2:
	for keyword in dict2[pageID]:
		hit2, score2 = dict2[pageID][keyword]
		if hit2 and score2 != -1:
			if pageID in dict1 and keyword in dict1[pageID]:
				hit1, score1 = dict1[pageID][keyword]
				if score1 == -1:
					only2.append((score2, pageID, keyword))

print("Find " + str(len(only2)) + " examples")
print("Obtaining the best " + str(args.top))
sort(only2)

for i in range(min(len(only2), args.top)):
	print(only2[i])


# Where method 1 > method 2 and hit in both cases
print("---------------------------------------------------------------")
print("Computing example when method 1 > method 2")

better1 = []

for pageID in dict1:
	for keyword in dict1[pageID]:
		hit1, score1 = dict1[pageID][keyword]
		if hit1 and score1 != -1:
			if pageID in dict2 and keyword in dict2[pageID]:
				hit2, score2 = dict2[pageID][keyword]
				if score2 != -1 and score1 > score2:
					better1.append((score1 - score2, pageID, keyword))

print("Find " + str(len(better1)) + " examples")
print("Obtaining the best " + str(args.top))
sort(better1)

for i in range(min(len(better1), args.top)):
	print(better1[i])


# Where method 1 < method 2
print("---------------------------------------------------------------")
print("Computing example when method 1 < method 2")

better2 = []

for pageID in dict2:
	for keyword in dict2[pageID]:
		hit2, score2 = dict2[pageID][keyword]
		if hit2 and score2 != -1:
			if pageID in dict1 and keyword in dict1[pageID]:
				hit1, score1 = dict1[pageID][keyword]
				if score1 != -1 and score1 < score2:
					better2.append((score2 - score1, pageID, keyword))

print("Find " + str(len(better2)) + " examples")
print("Obtaining the best " + str(args.top))
sort(better2)

for i in range(min(len(better2), args.top)):
	print(better2[i])
	
print("===============================================================")
