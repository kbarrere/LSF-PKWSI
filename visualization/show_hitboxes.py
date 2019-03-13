from PIL import Image
import numpy as np
from xmlPAGE import *

img_path = 'RS_Aicha_vorm_Wald_031_0187.jpg'
page_path = 'RS_Aicha_vorm_Wald_031_0187.xml'
index_path = 'RS_Aicha_vorm_Wald_031_0187.idx'
target = 'SEITE'

img = Image.open(img_path)
index = open(index_path, 'r')
page = pageData(page_path)



def draw_line(img, x1, y1, x2, y2, line_thickness=1, color=(255, 0, 0), dx=0.1):
	width, height = img.size
	
	if x1 != x2:
		a = float((y1 - y2)) / float((x1 - x2))
		b = y1 - a * x1
		
		for xt in np.arange(min(x1, x2), max(x1, x2), dx):
			yt = a*xt + b
			for dxt in np.arange(-float(line_thickness)/2, float(line_thickness)/2):
				for dyt in np.arange(-float(line_thickness)/2, float(line_thickness)/2):
					x = int(min(max(xt + dxt, 0), width-1))
					y = int(min(max(yt + dyt, 0), height-1))
					img.putpixel((int(x), int(y)), color)
	
	elif y1 != y2:
		a = float((x1 - x2)) / float((y1 - y2))
		b = x1 - a * y1
		
		for yt in np.arange(min(y1, y2), max(y1, y2), dx):
			xt = a*yt + b
			for dxt in np.arange(-float(line_thickness)/2, float(line_thickness)/2):
				for dyt in np.arange(-float(line_thickness)/2, float(line_thickness)/2):
					x = int(min(max(xt + dxt, 0), width-1))
					y = int(min(max(yt + dyt, 0), height-1))
					img.putpixel((x, y), color)



def score_to_color(score, bad_color=(255, 0, 0), good_color=(0, 255, 0)):
	output_color = []
	for c in range(len(bad_color)):
		output_color.append(int(bad_color[c] + score*(good_color[c]-bad_color[c])))
	
	return tuple(output_color)


lines_found = []

# Search for the desired keywords in index
for line in index:
	line = line[:-1]
	lineID, keyword, p, start_frame, end_frame, total_frames = line.split(' ')
	if keyword == target:
		#lineID = lineID.replace(',', '_')
		pageID, lineID = lineID.split('.')
		lines_found.append((lineID, keyword, float(p), int(start_frame), int(end_frame), int(total_frames)))

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
			_, keyword, p, start_frame, end_frame, total_frame = line
			line_xmin, line_ymin = line_coords[0]
			line_xmax, line_ymax = line_coords[2]
			width = line_xmax - line_xmin
			height = line_ymax - line_ymin
			
			xmin = int(line_xmin + float(start_frame)/float(total_frame)*width)
			xmax = int(line_xmin + float(end_frame)/float(total_frame)*width)
			
			ymin = line_ymin
			ymax = line_ymax
			
			# ~ print("---------------------------------------------------")
			# ~ print("line_xmin " + str(line_xmin))
			# ~ print("width " + str(width))
			# ~ print("start_frame " + str(start_frame))
			# ~ print("end_frame " + str(end_frame))
			# ~ print("total_frame " + str(total_frame))
			# ~ print("xmin " + str(xmin))
			# ~ print("xmax " + str(xmax))
			# ~ print("ymin " + str(ymin))
			# ~ print("ymax " + str(ymax))
			
			line_coords=[[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]
			
			elements_found.append((keyword, p, line_coords))

for el in elements_found:
	score = el[1]
	coords = el[2]
	for i in range(len(coords)):
		x1, y1 = coords[i]
		x2, y2 = coords[(i+1) % len(coords)]
		draw_line(img, x1, y1, x2, y2, color=score_to_color(score), line_thickness=5)

img.show()

index.close()