from PIL import Image
from xmlPAGE import *

img_path = 'RS_Aicha_vorm_Wald_031_0187.jpg'
page_path = 'RS_Aicha_vorm_Wald_031_0187.xml'
index_path = 'RS_Aicha_vorm_Wald_031_0187.idx'
target = 'SEITE'

img = Image.open(img_path)
index = open(index_path, 'r')
page = pageData(page_path)









lines_found = []

# Search for the desired keywords in index
for line in index:
	line = line[:-1]
	lineID, keyword, p, n1, n2, n3 = line.split(' ')
	if keyword == target:
		#lineID = lineID.replace(',', '_')
		pageID, lineID = lineID.split('.')
		lines_found.append((lineID, keyword, p, n1, n2, n3))

for line in lines_found:
	print(line[0])

# Open Page XML
page.parse()
textline_elements = page.get_region('TextLine')

elements_found = []
for textline_element in textline_elements:
	textline_element_id = page.get_id(textline_element)
	for line in lines_found:
		line_id = line[0]
		if textline_element_id == line_id:
			line_coords = page.get_coords(textline_element)
			elements_found.append((textline_element, line_id, line_coords))

index.close()
