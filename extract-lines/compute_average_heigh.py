import numpy as np
import cv2
import matplotlib.pyplot as plt
import argparse
import scipy
from skimage.filters import threshold_sauvola
import rlsa as RLSA



if __name__ == '__main__':
	
	# Parse arguments
	parser = argparse.ArgumentParser(description='Get the space between lines of text applying a projection of the gray level and a fft.')
	parser.add_argument('img_paths', nargs='+', help='path to the images to process.')
	parser.add_argument('--output_dir', help='path to the directory where to save the lines.')
	parser.add_argument('--show_input', action='store_true', help='show the input image')
	parser.add_argument('--show_projection', action='store_true', help='show the projection of the gray')
	parser.add_argument('--show_fft', action='store_true', help='show fft of the projection')
	parser.add_argument('--show_lines', action='store_true', help='show input image with computed line space')
	parser.add_argument('--show_filters', action='store_true', help='show the image afeter applying filters')
	parser.add_argument('--show_all', action='store_true', help='show every image. Usefull for debug purpose')
	parser.add_argument('--use_std_limit', action='store_true', help='use the mean and the standard deviation to limit the ray value to the interval [mean - std ; mean + std]')
	parser.add_argument('--use_second_peak', action='store_true', help='use both the first and second peak of the fft to compute two line cuttings.')
	parser.add_argument('--blur', default=0, type=int, help='apply a gaussian blur to the image with the integer passed as argument as the kerel size. Must be an odd number')
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
	parser.add_argument('--max_height', default=-1, help='max height to print')
	parser.add_argument('--max_width', default=-1, help='max width to print')

	args = parser.parse_args()



def resize_image(img_array, max_width, max_height, interpolation=cv2.INTER_AREA):
	height = img_array.shape[0]
	width = img_array.shape[1]
	
	print(str(width) + " , " + str(height))
	print(str(max_width) + " , " + str(max_height))
	
	if height > max_height and width > max_width:
		img_ratio = float(width) / float(height)
		max_ratio = float(max_width) / float(max_height)
		
		print(str(img_ratio) + " | " + str(max_ratio))
		
		if img_ratio > max_ratio:
			scale_ratio = float(width) / float(max_width)
			print(str(scale_ratio))
			resized_image = cv2.resize(img_array, (int(float(width) / scale_ratio), int(float(height) / scale_ratio)), interpolation=interpolation)
			print("Case 1 - " + str(resized_image.shape) + " | " + str(int(float(width) / scale_ratio)) + "," + str(int(float(height) / scale_ratio)))
			return resized_image
			
		else:
			scale_ratio = float(height) / float(max_height)
			resized_image = cv2.resize(img_array, (int(float(width) / scale_ratio), int(float(height) / scale_ratio)), interpolation=interpolation)
			print("Case 2 - " + str(resized_image.shape) + " | " + str(int(float(width) / scale_ratio)) + "," + str(int(float(height) / scale_ratio)))
			return resized_image
			
		
	elif height > max_height:
		scale_ratio = float(height) / float(max_height)
		resized_image = cv2.resize(img_array, (int(float(width) / scale_ratio), max_height), interpolation=interpolation)
		print("Case 3 - " + str(resized_image.shape) + " | " + str(int(float(width) / scale_ratio)) + "," + str(max_height))
		return resized_image
		
	elif width > max_width:
		scale_ratio = float(width) / float(max_width)
		resized_image = cv2.resize(img_array, (max_width, int(float(height) / scale_ratio)), interpolation=interpolation)
		print("Case 4 - " + str(resized_image.shape) + " | " + str(max_width) + "," + str(int(float(height) / scale_ratio)))
		return resized_image
		
	return img_array


def show_image(img_array, title='Image', wait_key=False, delete_after=False, max_height=-1, max_width=-1):
	resized_img = np.copy(img_array)
	if max_height > 0 and max_width > 0:
		resized_img = resize_image(img_array, max_width, max_height)
	
	cv2.imshow(title, resized_img)
	if wait_key:
		cv2.waitKey(0)
	if delete_after:
		cv2.destroyWindow(title)



def project_median_gray(input_image_array):
	height, width = input_image_array.shape
	gray_value = np.zeros((height), np.uint8)
	
	for y in range(height):
		median_value = 0
		for x in range(width):
			median_value = median_value + input_image_array[y][x]
		
		median_value = median_value / width
		gray_value[y] = median_value
	
	return gray_value



def get_mean_and_std(gray_value):
	height = gray_value.shape[0]
	
	c = 0
	for y in range(height):
		c = c + gray_value[y]
	mean = c / height

	c = 0
	for y in range(height):
		c = c + (gray_value[y] - mean) ** 2
	c = c / height
	std = c ** 0.5
	std = int(std)
	
	return mean, std



def limit_to_std(gray_value, mean, std, gray_value_img=None):
	height = gray_value.shape[0]
	
	min_limit = max(mean - std, 0)
	max_limit = min(mean + std, 255)

	if gray_value_img is not None:
		for y in range(height):
			gray_value_img[y][mean] = [255, 0, 0]
			gray_value_img[y][min_limit] = [0, 255, 0]
			gray_value_img[y][max_limit] = [0, 255, 0]

	# Limit the signal
	for y in range(height):
		if gray_value[y] < min_limit:
			gray_value[y] = min_limit
		if gray_value[y] > max_limit:
			gray_value[y] = max_limit



def compute_fft(gray_value, scale_fft=True):
	height = gray_value.shape[0]
	
	sp = np.fft.fft(gray_value)
	sp[0] = 0
	
	t = np.arange(height)
	freq = np.fft.fftfreq(t.shape[-1])
	
	sp = sp[:height//2]
	freq = freq[:height//2]
	
	ampl = np.abs(sp)
	
	if scale_fft:
		ampl = ampl * freq
	
	return ampl, freq



def gaussian(x, mean, std):
	return np.exp(- ((x - mean) ** 2) / (2 * std ** 2))

def revert_gaussian(x, mean, std):
	return 1 - gaussian(x, mean, std)
	


def compute_average_height(img_paths, output_dir=None, show_input=False, show_projection=False, show_fft=False, show_lines=False, show_filters=False, show_all=False, use_std_limit=False, use_second_peak=False, blur=0, threshold=-1, local_threshold=-1, rlsa=-1, local_subdivision=1, min_space_size=5, do_not_scale_fft=False, smooth_fft=-1, wait_key=False, wait_key_end=False, print_wavelength=False, print_progress=False, max_height=-1, max_width=-1):
	file_completed = 0
	
	average_line_heights = []
	
	# Apply the whole process to every image
	for img_path in img_paths:
		
		average_line_height = []
		
		img_name = img_path.split('/')[-1]
		
		# Read the image from the path
		input_img = cv2.imread(img_path, cv2.IMREAD_COLOR)
		# ~ img = np.copy(input_img)
		img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
		height, width, channels = input_img.shape
		
		# Show the input image
		if show_input or show_all:
			show_image(input_img, title=img_name+' - '+'Input Image', wait_key=wait_key, max_height=max_height, max_width=max_width)
		
		# Apply a Gaussian filter
		if blur > 0:
			img = cv2.GaussianBlur(img, (blur, blur), 0)
		
		# Apply a global threshold to the image
		if threshold > -1 and threshold < 256:
			# Aplly a threshold
			for y in range(height):
				for x in range(width):
					if img[y][x][0] < threshold and img[y][x][1] < threshold and img[y][x][2] < threshold:
						img[y][x] = [0, 0, 0]
					else:
						img[y][x] = [255, 255, 255]
		
		# Apply a local threshold to the image
		if local_threshold > -1:
			img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, local_threshold, 2)
		
		# Apply Run Lenght Smoothing Algorithm (RLSA)
		if rlsa > -1:
			img = RLSA.rlsa(img, True, False, rlsa)

		if show_filters or show_all:
			show_image(img, title=img_name+' - '+'Filtered Image', wait_key=wait_key, max_height=max_height, max_width=max_width)
		
		local_width = int(width / local_subdivision) 
		local_height = int(height / local_subdivision)
		ampl = np.zeros(local_height//2)
		freq = np.zeros(local_height//2)
		for local_y in range(local_subdivision):
			start_y = local_y * local_height
			end_y = height
			if local_y < local_subdivision-1:
				end_y = (local_y+1) * local_height
			
			for local_x in range(local_subdivision):
				start_x = local_x * local_width
				end_x = width
				if local_x < local_subdivision-1:
					end_x = (local_x+1) * local_width
				
				local_img = img[start_y:end_y, start_x:end_x]
		
				# Compute the median gray values
				gray_value = project_median_gray(local_img)

				# Create the image if showing it is asked
				gray_value_img = None
				if show_projection or show_all:
					gray_value_img = np.zeros((local_height, 256, 3), np.uint8)
					background = [255, 255, 255]
					value_color = [0, 0, 255]
					gray_value_img[:][:] = background

				# Compute mean value, and std :
				if use_std_limit:
					mean, std = get_mean_and_std(gray_value)
					limit_to_std(gray_value, mean, std, gray_value_img=gray_value_img)

				# Show projection in an image
				if show_projection or show_all:
					for y in range(local_height):
						gray_value_img[y][gray_value[y]] = value_color = [0, 0, 255]
					
					show_image(gray_value_img, title=img_name+' - '+'gray Projection' + ' - ' + str(local_y) + ',' + str(local_x), wait_key=wait_key, max_height=max_height, max_width=max_width)

				# Compute the fft
				local_ampl, local_freq = compute_fft(gray_value, scale_fft=(not do_not_scale_fft))	
				freq_len = freq.shape[0]
				
				if local_x == 0 and local_y == 0:
					freq = local_freq
				
				for y in range(local_height//2):
					ampl[y] += local_ampl[y] / (local_subdivision ** 2)
		
		if smooth_fft>0:
			# Smooth the FFT by applying a Gaussian Kernel for every frequency
			freq_size = len(ampl)
			smooth_ampl = np.zeros(freq_size)
			for i in range(freq_size):
				ampl_i = 0
				
				for j in range(freq_size):
					ampl_i += gaussian(freq[j], freq[i], smooth_fft)*ampl[j]
				
				smooth_ampl[i] = ampl_i
			ampl = smooth_ampl
		
		# Get the spike
		argmax = np.argmax(ampl[:int(freq_len / min_space_size / 0.5)])
		maxfreq = freq[argmax]
		wavelength = 1 / maxfreq
		average_line_height.append(wavelength)
		
		# Get the second spike
		is_second_peak = False
		if use_second_peak:
			maxampl1 = ampl[argmax]
			argmax2 = np.argmax((ampl * revert_gaussian(freq, maxfreq, 0.2*maxfreq))[:int(freq_len / min_space_size / 0.5)])
			maxampl2 = ampl[argmax2]
			maxfreq2 = freq[argmax2]
			wavelength2 = 1 / maxfreq2
			
			# ~ if maxampl2 > 0.7*maxampl1 and not (maxfreq % maxfreq2 < 0.05 * maxfreq2 or maxfreq % maxfreq2 > 0.95 * maxfreq2 or maxfreq2 % maxfreq < 0.05 * maxfreq or maxfreq2 % maxfreq > 0.95 * maxfreq):
			if maxampl2 > 0.7*maxampl1:
				is_second_peak = True
				average_line_height.append(wavelength2)
		

		# Show the input image with space between lines showed
		if show_lines or show_all or output_dir:
			line_img = np.copy(input_img)
			i = 1
			while wavelength*i < height:
				for x in range(width):
					line_img[int(wavelength*i)][x] = [0, 255, 0]
				
				i = i + 1
			
			# If a second spike is also used
			if is_second_peak:
				i = 1
				while wavelength2*i < height:
					for x in range(width):
						if line_img[int(wavelength2*i)][x][0] == 0 and line_img[int(wavelength2*i)][x][1] == 255 and line_img[int(wavelength2*i)][x][2] == 0:
							line_img[int(wavelength2*i)][x] = [0, 255, 255]
						else:
							line_img[int(wavelength2*i)][x] = [0, 0, 255]
					
					i = i + 1
			
			if show_lines or show_all:
				show_image(line_img, title=img_name+' - '+'Input Image with computed space between lines', wait_key=wait_key, max_height=max_height, max_width=max_width)
			
			if output_dir:
				cv2.imwrite(output_dir + img_name, line_img)
		
		# Show FFT
		if show_fft or show_all:
			plt.plot(freq, ampl)
			if is_second_peak:
				plt.plot(freq, ampl * revert_gaussian(freq, maxfreq, 0.2*maxfreq))
			plt.show()
		
		if print_wavelength:
			print(wavelength)
			if is_second_peak:
				print(wavelength2)
			
		
		file_completed = file_completed + 1
		if print_progress and len(img_paths) > 1:
			print("Progress: " + str(file_completed) + "/" + str(len(img_paths)))
		
		average_line_heights.append(average_line_height)

	if wait_key_end:
		cv2.waitKey(0)

	cv2.destroyAllWindows()
	
	return average_line_heights

if __name__ == '__main__':
	compute_average_height(img_paths=args.img_paths, output_dir=args.output_dir, show_input=args.show_input, show_projection=args.show_projection, show_fft=args.show_fft, show_lines=args.show_lines, show_filters=args.show_filters, show_all=args.show_all, use_std_limit=args.use_std_limit, use_second_peak=args.use_second_peak, blur=args.blur, threshold=args.threshold, local_threshold=args.local_threshold, rlsa=args.rlsa, local_subdivision=args.local_subdivision, min_space_size=args.min_space_size, do_not_scale_fft=args.do_not_scale_fft, smooth_fft=args.smooth_fft, wait_key=args.wait_key, wait_key_end=args.wait_key_end, print_wavelength=args.print_wavelength, print_progress=args.print_progress, max_height=args.max_height, max_width=args.max_width)
