import argparse
import numpy as np

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Correct the shape of the bonding boxes')
	parser.add_argument('index_file', help='path to index file containing keywords, score and positioninng in the lines (in the format pageID.LineID keyword score startframe endframe totalframe')
	parser.add_argument('output_index_file', help='path to the outputted index. In the same format')
	parser.add_argument('--mean', type=float, default=3.128, help='mean of the gaussian of number of frames per character')
	parser.add_argument('--std', type=float, default=1.373, help='std of the gaussian of number of frames per character')
	parser.add_argument('--threshold', type=float, default=0.05, help='If the gaussian score is below that value, correct it')
	
	args = parser.parse_args()



index_file = open(args.index_file, 'r')
output_index_file = open(args.output_index_file, 'w')

delta = args.std * ( -2 * np.log(args.threshold)) ** 0.5
x1 = args.mean - delta
x2 = args.mean + delta

print("x1: " + str(x1))
print("x2: " + str(x2))


for line in index_file:
	line = line[:-1]
	pageIDlineID, keyword, score_str, start_frame_str, end_frame_str, total_frame_str = line.split(' ')
	start_frame = int(start_frame_str)
	end_frame = int(end_frame_str)
	
	nbr_characters = len(keyword)
	nbr_frames = end_frame - start_frame
	frames_per_char = float(nbr_frames) / float(nbr_characters)
	
	
	if frames_per_char < x1:
		# Too small
		new_nbr_frames = int(x1 * nbr_characters)
		
		# Keep the bbx right-aligned
		start_frame = end_frame - new_nbr_frames
		
	elif frames_per_char > x2:
		# Too big
		new_nbr_frames = int(x2 * nbr_characters)
		
		# Keep the bbx right-aligned
		start_frame = end_frame - new_nbr_frames
	
	line_to_write = pageIDlineID + ' ' + keyword + ' ' + score_str + ' ' + str(start_frame) + ' ' + end_frame_str + ' ' + total_frame_str + '\n'
	output_index_file.write(line_to_write)



index_file.close()
output_index_file.close()
