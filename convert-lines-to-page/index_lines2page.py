import argparse
	


# Parse arguments
parser = argparse.ArgumentParser(description='Convert the Indexes from line level to page level')
parser.add_argument('lines_file', help='path to the text file containing the index at the line level. Line in the format pageID word probability')
parser.add_argument('page_file', help='path to the text file that will contain the index at the page level')
parser.add_argument('--id-list-file', help='path to the file where to store the line ids at the page level')

args = parser.parse_args()



lines_file = open(args.lines_file, "r")
page_file = open(args.page_file, "w")
id_list_file = None
if args.id_list_file:
	id_list_file = open(args.id_list_file, "w")

page_dic = {}

for line in lines_file:
	line_words = line[:-1].split(' ')
	
	page_id = line_words[0]
	word = line_words[1]
	probability = float(line_words[2])
	
	# Adding the page in the dictionnary if it is not inside
	if page_id not in page_dic:
		page_dic[page_id] = {}
	
	# Adding the word in the dictionnary of the page if it is not inside
	if word not in page_dic[page_id]:
		page_dic[page_id][word] = probability
	
	# for that word, keep the one with the hightest probability and it's informations
	page_dic[page_id][word] = max(page_dic[page_id][word], probability)
	
for page_id in page_dic:
	line_id = "this_is_not_a_line"
	if args.id_list_file:
		id_list_file.write(page_id + "." + line_id + "\n")
	
	for word in page_dic[page_id]:
		p = page_dic[page_id][word]
		page_line = page_id + "." + line_id + " " + word + " " + str(p) + " " + str(-1) + " " + str(-1) + " " + str(-1) + "\n"
		page_file.write(page_line)
		

lines_file.close()
page_file.close()
if args.id_list_file:
	id_list_file.close()
