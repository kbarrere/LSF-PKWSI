import argparse
	


# Parse arguments
parser = argparse.ArgumentParser(description='Convert the Groundtruth from line level to page level')
parser.add_argument('lines_file', help='path to the text file containing the groundtruth at the line level')
parser.add_argument('page_file', help='path to the text file containing the groundtruth at the line level')
parser.add_argument('--id-list-file', help='path to the file that gives pageID')

args = parser.parse_args()



class PageGT:
	def __init__(self, page_id):
		self.page_id = page_id
		self.words = []
		self.x = 0
		self.y = 0
	
	def add_word(self, word):
		self.words.append(word)
	
	def expand_coordinates(self, x, y):
		if x > self.x:
			self.x = x
		if y > self.y:
			self.y = y
	
	def get_words(self):
		return self.words
	
	def get_coordinates(self):
		return self.x, self.y

page_ids = []
if args.id_list_file:
	with open(args.id_list_file, 'r') as id_list_file:
		for line in id_list_file:
			line = line[:-1]
			line_split = line.split('.')
			pageID = line_split[0]
			page_ids.append(pageID)
	


lines_file = open(args.lines_file, "r")
page_file = open(args.page_file, "w")

page_dic = {}

for line in lines_file:
	line_words = line[:-1].split(' ')
	
	page_id = line_words[0]
	line_id = line_words[1]
	x1 = line_words[2]
	y1 = line_words[3]
	x2 = line_words[4]
	y2 = line_words[5]
	words = line_words[6:]
	
	if not args.id_list_file or page_id in page_ids:
		# Adding the page in the dictionnary if it is not iniside it
		if page_id not in page_dic:
			page_dic[page_id] = PageGT(page_id)
		
		# Store every words
		for word in words:
			if word:
				page_dic[page_id].add_word(word)
		
		page_dic[page_id].expand_coordinates(x2, y2)

for key in page_dic:
	page_id = key
	line_id = page_id+".this_is_not_a_line"
	x1, y1 = 0, 0
	x2, y2 = page_dic[key].get_coordinates()
	words = page_dic[key].get_words()
	page_line = page_id + " " + line_id + " " + str(x1) + " " + str(y1) + " " + str(x2) + " " + str(y2) + " " + " ".join(words) + "\n"
	
	page_file.write(page_line)

lines_file.close()
page_file.close()
