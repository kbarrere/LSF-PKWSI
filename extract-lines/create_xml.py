import cv2

from compute_average_heigh import *
from xmlPAGE import *



if __name__ == '__main__':
	# Parse arguments
	parser = argparse.ArgumentParser(description='Get the space between lines of text applying a projection of the gray level and a fft.')
	parser.add_argument('img_paths', nargs='+', help='path to the images to process')
	parser.add_argument('output_xml_dir', help='path to the directory where to save the resultings xml')
	parser.add_argument('--window_height_multiplier', type=float, default=1.25, help='this scalar multiplied by the average line height give the height of an extracted line')
	parser.add_argument('--window_shift_multiplier', type=float, default=0.33, help='this scalar multiplied by the average line height give the shifht between each extracted line')
	parser.add_argument('--creator', default='PRHLT', help='name of the creator that will be written inside the resulting xml')
	parser.add_argument('--output_dir', help='path to the directory where to save the lines')
	parser.add_argument('--show_input', action='store_true', help='show the input image')
	parser.add_argument('--show_projection', action='store_true', help='show the projection of the gray')
	parser.add_argument('--show_fft', action='store_true', help='show fft of the projection')
	parser.add_argument('--show_lines', action='store_true', help='show input image with computed line space')
	parser.add_argument('--show_filters', action='store_true', help='show the image afeter applying filters')
	parser.add_argument('--show_all', action='store_true', help='show every image. Usefull for debug purpose')
	parser.add_argument('--use_std_limit', action='store_true', help='use the mean and the standard deviation to limit the ray value to the interval [mean - std ; mean + std]')
	parser.add_argument('--use_second_peak', action='store_true', help='use both the first and second peak of the fft to compute two line cuttings')
	parser.add_argument('--blur', default=0, type=int, help='apply a gaussian blur to the image with the integer passed as argument as the kerel size')
	parser.add_argument('--threshold', default=-1, type=int, help='apply a threshold to the image with the integer passed as argument as the threshold value')
	parser.add_argument('--local_threshold', default=-1, type=int, help='apply a local threshold to the image with the integer passed as argument as the local window size. Must be an odd number')
	parser.add_argument('--rlsa', default=-1, type=int, help='apply a Run Lenght Smoothing Algorithm. The image must be Binarized before. The value passed as an argument correspond to TODO')
	parser.add_argument('--local_subdivision', default=1, type=int, help='cut the image in sub images. The argument passed determined the number of subimage for each axis')
	parser.add_argument('--min_space_size', default=5, type=int, help='minimum size of the space between lines')
	parser.add_argument('--do_not_scale_fft', action='store_true', help='by default, fft is scaled by frequency')
	parser.add_argument('--smooth_fft', default=0, type=float, help='Smooth the Fourier Transfrom by applying a Gaussian Kernel. The value passed as argument is the stantard deviation of the gaussian function. The unit of this value is the frequency.')
	parser.add_argument('--wait_key', action='store_true', help='wait a key to be pressed between images')
	parser.add_argument('--wait_key_end', action='store_true', help='wait a key to be pressed to exit the program')
	parser.add_argument('--print_wavelength', action='store_true', help='print the wavelength of the differents peaks in the console')
	parser.add_argument('--print_progress', action='store_true', help='print the progress of the whole process when using different images')
	parser.add_argument('--max_height', type=int, default=-1, help='max height to print')
	parser.add_argument('--max_width', type=int, default=-1, help='max width to print')

	args = parser.parse_args()

def convert_to_coords(x1, y1, x2, y2):
	return str(x1)+","+str(y1) + " " + str(x1)+","+str(y2)+ " " + str(x2)+","+str(y2)+ " " + str(x2)+","+str(y1)

if __name__ == '__main__':
	file_completed = 0
	
	for i in range(len(args.img_paths)):
		img_path = args.img_paths[i]
		img_name = img_path.split('/')[-1]
		basename = img_name[:-len(img_name.split('.')[-1])-1]
		
		input_img = cv2.imread(img_path, cv2.IMREAD_COLOR)
		height, width, channels = input_img.shape
		
		page_data = pageData(args.output_xml_dir + "/" + basename+".xml", creator=args.creator)
		page_data.new_page(img_name, str(height), str(width))
		
		pageCoords = convert_to_coords(0, 0, width-1, height-1)
		
		# Extract average line heights for each image
		average_line_heights = compute_average_height(img_paths=[img_path], output_dir=args.output_dir, show_input=args.show_input, show_projection=args.show_projection, show_fft=args.show_fft, show_lines=args.show_lines, show_filters=args.show_filters, show_all=args.show_all, use_std_limit=args.use_std_limit, use_second_peak=args.use_second_peak, blur=args.blur, threshold=args.threshold, local_threshold=args.local_threshold, rlsa=args.rlsa, local_subdivision=args.local_subdivision, min_space_size=args.min_space_size, do_not_scale_fft=args.do_not_scale_fft, smooth_fft=args.smooth_fft, wait_key=args.wait_key, wait_key_end=args.wait_key_end, print_wavelength=args.print_wavelength, print_progress=False, max_height=args.max_height, max_width=args.max_width)[0]
		
		for j in range(len(average_line_heights)):
			average_line_height = average_line_heights[j]
			
			regionId = str(j) + "-" + str(average_line_height).replace('.', '_')
			regionCoords = pageCoords
			text_region = page_data.add_element("TextRegion", regionId, "TextRegion", regionCoords)
			
			window_height = average_line_height * args.window_height_multiplier
			window_shift = average_line_height * args.window_shift_multiplier
			
			k = 0
			while int(k*window_shift+window_height-1) < height:
				lineCoords = convert_to_coords(0, int(k*window_shift), width-1, int(k*window_shift+window_height-1))
				lineId = regionId + "-" + str(window_height).replace('.', '_') + "-" + str(window_shift).replace('.', '_') + "-" + str(k)
				page_data.add_element("TextLine", lineId, "TextLine", lineCoords, parent=text_region)
				k =  k + 1
			
		page_data.save_xml()
		
		file_completed = file_completed + 1
		if args.print_progress and len(args.img_paths) > 1:
			print("Progress: " + str(file_completed) + "/" + str(len(args.img_paths)))
			
			
