import argparse
import matplotlib.pyplot as plt



if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Print an histogram of the detected bounding box width divided by the size of the detected word.')
	parser.add_argument('index_path', help='path to index file containing keywords, score and positioninng in the lines')
	parser.add_argument('data_path', help='path to index file containing keywords, score and positioninng in the lines')
	parser.add_argument('--bins', default=10, type=int, help='Number of delimiter')
	parser.add_argument('--max', default=20.0, type=float, help='Max value between which the results are not taken into account')
	parser.add_argument('--quiet', action='store_true', help='Do not print anything')
	
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

# Store every word that is in the ground truth inside a list
data_dict = {}
data_file = open(args.data_path, 'r')

for line in data_file:
	line = line[:-1]
	pagelineID, keyword, gtb_str, score_str = line.split(' ')
	pageID, lineID = pagelineID.split('.')
	gtb = False
	if gtb_str == '1':
		gtb = True
	
	# ~ if gtb:
	if True:
		if pageID not in data_dict:
			data_dict[pageID] = {}
		if lineID not in data_dict[pageID]:
			data_dict[pageID][lineID] = []
		if keyword not in data_dict[pageID][lineID]:
			data_dict[pageID][lineID].append(keyword)
			
data_file.close()


# Get the size of the bounding box normalised by the size of the word
datas = []

index_file = open(args.index_path)

for line in index_file:
	line = line[:-1]
	pagelineID, keyword, score_str, start_frame_str, end_frame_str, total_frame_str = line.split(' ')
	pageID, lineID = pagelineID.split('.')
	
	if pageID in data_dict and lineID in data_dict[pageID] and keyword in data_dict[pageID][lineID]:
		start_frame = int(start_frame_str)
		end_frame = int(end_frame_str)
		nbr_frames = end_frame - start_frame
		len_keyword = len(keyword)
		frames_per_char = float(nbr_frames)/float(len_keyword)
		if frames_per_char > args.max:
			if not args.quiet:
				print("Warning very high value !")
				print(" - PageID: " + pageID)
				print(" - LineID: " + lineID)
				print(" - Keyword: " + keyword)
				print(" - Start frame: " + start_frame_str)
				print(" - End frame: " + end_frame_str)
				print(" - Number of frams per char: " + str(frames_per_char))
				print("Bounding box not taken into account")
				print("If this is not an expected result, you should consider increasing the argument --max.")
		else:
			datas.append(frames_per_char)

if not args.quiet:
	print("Detected " + str(len(datas)) + " bounding boxes")

index_file.close()

mean, std = compute_mean_std(datas)
print("Computed mean: " + str(mean))
print("Computed std: " + str(std))

plt.hist(datas, bins=args.bins)
plt.show()
