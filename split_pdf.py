## Author: Mario Mendez Diaz

from pdf2image import convert_from_path
import PIL
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus.flowables import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import StringIO
import cv2
import numpy
import sys
import os

def print_debug_msg(msg):
	print "************************ "+msg

#return the n largest 4-point contours given a list of contours
def get_n_largest_contours(contours, n):
	
	n_largest_contours = []
	indexes_with_more_than_four_points = []

	# get the indexes of contours with more than 4 points, since they are not slides! 
	for i in range(0,len(contours)-1):
		if len(contours[i]) > 4:
			indexes_with_more_than_four_points.append(i)

	#delete the indexes of the contours iwth more than 4 points
	for index in indexes_with_more_than_four_points:
		if index < len(contours):
			del contours[index]

	#sort the remaining list by area and create a list with the n largest contours
	sorted_contours = sorted(contours, key=lambda x: cv2.contourArea(x))
	for i in range(0, n):
		n_largest_contours.append(sorted_contours[i])	

	return n_largest_contours


#return the contour coordinates of all #number of slides in an image
def get_slides_coordinates(image, min_size, max_size, number_of_slides):
	
	lower_bound_pixel = 0 #values used in colour thresholding
	upper_bound_pixel = 5
	opencv_image = numpy.array(image) # convert to open cv image
	second_image = opencv_image.copy()
	#open cv tings start
	grayscale_img = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2GRAY)
	mask = cv2.inRange(grayscale_img, lower_bound_pixel,upper_bound_pixel) #find black elements (assuming black boxes)
	contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]#find contours in mask

	if len(contours) >= number_of_slides: #only continue if the contours found are at least equal to the expected amount of slides to be found
		largest_contours = get_n_largest_contours(contours, number_of_slides)  #we are interested in the largest (number of slides) contours
		return largest_contours
		
		#========================================================================
		# MISSING CHECK FOR SLIDES BEING IN ALOWED MIN AND MAX DIMENSIONS!
		#=======================================================================
	else:
		return None #return empty list

# use the pdf2image library to convert every page in the pdf to an image
def extract_images_from_pdf(pdf_file_path):	
	images = None
	try:
		images = convert_from_path(pdf_file_path) #get the images
	except:
		print "Error on pdf \""+pdf_name+"\", could not split file " #catch exception
	return images

# crop all images once the coordinates are known, crop only the "individual slides"
def crop_images(images, coords, size):  
	cropped_images = []
	print "length of coords "+str(len(coords))
	print "number of images "+str(len(images))

	for image in images:
		for i in range(0, len(coords)):
			crop_area = (coords[i][0], coords[i][1], coords[i][0] + size[0], coords[i][1] + size[1]) # area is xy coords, plus width and height
			cropped_image = image.crop(crop_area)
			cropped_images.append(cropped_image)
	return cropped_images


#create the output document
def create_new_document(filename, slides, output_destination): 
	
	output_filename = "new_"+filename
	working_dir_path = output_destination+output_filename # get full path of file
	c = canvas.Canvas(working_dir_path, pagesize=letter) # create pdf document

	# save all images into pdf, one page at a time
	for slide in slides:
		side_im = slide
		side_im_data = StringIO.StringIO()
		side_im.save(side_im_data, format='png')
		side_im_data.seek(0)
		side_out = ImageReader(side_im_data)
		c.drawImage(side_out,50,250)
		c.showPage()
	c.save() # save the output!
	return output_filename

#resize all images before they are included in the output
def resize_images(images): 	
	if images is not None:
		resized_images = []
		basewidth = 500   #moidy this value to change image size!
		width = (basewidth/float(images[0].size[0]))
		height = int((float(images[0].size[1]) * float(width)))

		for image in images: # resize all images
			image = image.resize((basewidth, height), PIL.Image.ANTIALIAS)
			resized_images.append(image)
		return resized_images
	else:
		return None

def assert_document_dimensions(width, height):
	orientation = False
	if( width == 1700 and height == 2200):
		orientation = True
	elif( width == 2200 or height == 1700):
		orientation = True
	return orientation

def merge_slides_from_halves(left_side, right_side, mode):
	merged_coordinates = None
	#mode 1 has ordering: [top_left, right_left, middle_left, middle_right, bottom_left, bottom_right]
	#mode 2 has ordering: [top_left, middle_left, bottom_left, top_right, middle_right, bottom_right]
	if mode == 1:
		merged_coordinates = [left_side[0],  left_side[1],  left_side[2],  right_side[0], right_side[1], right_side[2]]
	else:
		merged_coordinates = [left_side[0],  right_side[0],  left_side[1],  right_side[1], left_side[2], right_side[2]]
	return merged_coordinates

#zipper merge two lists
def merge_images(list_one, list_two):
	merged_list = []
	for i in range(0, len(list_one)):
		merged_list.append(list_one[i])
		merged_list.append(list_two[i])
	return merged_list

#extract from a list of 4 point contours only the top left x and y of every contour and return it in a 2d array
def numpy_to_two_d_array(numpy_array):
	two_d_array = []
	coordinate_pair = []
	for i in range(0,len(numpy_array)):
		coordinate_pair = [(numpy_array[i][0][0])[0], (numpy_array[i][0][0])[1]]
		two_d_array.append(coordinate_pair)
	return two_d_array

#sort the given two d array and sort it by ascending order of y coordinate
def sort_by_asc_y(coord_list):
	sorted_list = sorted(coord_list,key=lambda l:l[1])
	return sorted_list

#given an ndimensional numpy array of coordinates return the width and height of the obj represented by the coordinates
def get_slide_size(coords_list):
	obj_coordinates = coords_list[0] #single out only one set of coords
	width = obj_coordinates[2][0][0] - obj_coordinates[0][0][0]
	height = obj_coordinates[2][0][1] - obj_coordinates[0][0][1]
	return (width, height)



#=============================================================
# MAIN PROCESSING FOR EACH KIND OF PDF
#=============================================================


def process_2_slide_pdf(images, pdf_name, input_location, output_destination):
	min_slide_width = 200
	min_slide_height = 200
	max_slide_width = 1050
	max_slide_height = 840

	print_debug_msg("Doing 2 slides...")

	#first crop the image in the two halves
	area_upper_half= (0,0,images[0].size[0], images[0].size[1]/2) # coordinates of upper left quadrant of image)
	area_lower_half = (0,images[0].size[1]/2, images[0].size[0], images[0].size[1])
	
	upper_image_half = images[0].crop(area_upper_half)
	lower_image_half = images[0].crop(area_lower_half) 	

	upper_box_coordinates = find_box_using_opencv(upper_image_half, min_slide_width, min_slide_height, max_slide_width, max_slide_height, False) # attempt to find an individual slides so that slides can be centered in their own page
	lower_box_coordinates = find_box_using_opencv(lower_image_half, min_slide_width, min_slide_height, max_slide_width, max_slide_height, False) # attempt to find an individual slides so that slides can be centered in their own page

	if upper_box_coordinates is not None and lower_box_coordinates is not None:

		#calculate width and height for both slides
		upper_slide_width = upper_box_coordinates[2][0][0] - upper_box_coordinates[0][0][0]
		upper_slide_height = upper_box_coordinates[2][0][1] - upper_box_coordinates[0][0][1]

		lower_slide_width = lower_box_coordinates[2][0][0] - lower_box_coordinates[0][0][0]
		lower_slide_height = lower_box_coordinates[2][0][1] - lower_box_coordinates[0][0][1]


		#get the top left coordinate of the slide for both upper and lower
		upper_slide_x = upper_box_coordinates[0][0][0]  
		upper_slide_y = upper_box_coordinates[0][0][1]

		lower_slide_x = lower_box_coordinates[0][0][0]  
		lower_slide_y = lower_box_coordinates[0][0][1]


		if (upper_slide_x == lower_slide_x) and (upper_slide_y == lower_slide_y) and (upper_slide_width == lower_slide_width) and (upper_slide_height == lower_slide_height):
			print_debug_msg("Symmetry <3")

			slide_coords = [[upper_slide_x, upper_slide_y]]

			#now calcualate the real xy of the image in the bottom
			distance_to_lower_bottom = images[0].size[1]/2 - upper_box_coordinates[2][0][1]
			lower_slide_y = (images[0].size[1]/2) + distance_to_lower_bottom #only need to calculate y, x will be the same		
			slide_coords.insert(2, [upper_slide_x, lower_slide_y])

			print "All slides found successfully in " + pdf_name

			cropped_slide_images = crop_images(images, slide_coords, (upper_slide_width, upper_slide_height))
			return cropped_slide_images


		else:
			print_debug_msg("Not symmetrical")

			#crop all images in half
			upper_half_images = []
			for image in images:
				upper_image_half = image.crop(area_upper_half)
				upper_half_images.append(upper_image_half)

			lower_half_images = []
			for image in images:
				lower_image_half = image.crop(area_lower_half)
				lower_half_images.append(lower_image_half)

			#crop and resize, seperately , merge in the end
			cropped_upper_slides_images = crop_images(upper_half_images,[[upper_slide_x, upper_slide_y]], (upper_slide_width, upper_slide_height))
			cropped_lower_slides_images = crop_images(lower_half_images,[[lower_slide_x, lower_slide_y]], (lower_slide_width, lower_slide_height))

			resized_upper_images = resize_images(cropped_upper_slides_images)
			resized_lower_images = resize_images(cropped_lower_slides_images)

			merged_images = merge_images(resized_upper_images, resized_lower_images)
			return merged_images
	else:
		return "Failed to find slides in document."


def split_vertically(images, pdf_name, number_of_slides_in_half, min_slide_dimensions, max_slide_dimensions):
	
	print_debug_msg("CONSTRUCCION   Doing "+str((2*number_of_slides_in_half))+" slides...")

	#first crop image in half and find coordinates of the slides in each half
	left_crop_area = (0,0,images[0].size[0]/2, images[0].size[1])
	image_left_half = images[0].crop(left_crop_area)

	right_crop_area = (images[0].size[0]/2, 0, images[0].size[0], images[0].size[1])
	image_right_half = images[0].crop(right_crop_area)

	#get coordinates of slides in both halves
	left_half_slide_coordinates = get_slides_coordinates(image_left_half, min_slide_dimensions, max_slide_dimensions, number_of_slides_in_half)
	right_half_slide_coordinates = get_slides_coordinates(image_right_half, min_slide_dimensions, max_slide_dimensions, number_of_slides_in_half)

	#get width and heght for left and right slides
	left_slides_size = get_slide_size(left_half_slide_coordinates)
	right_slides_size = get_slide_size(right_half_slide_coordinates)

	#convert numpy contours arrray to two dimensional array
	left_half_slide_coordinates = numpy_to_two_d_array(left_half_slide_coordinates)
	right_half_slide_coordinates = numpy_to_two_d_array(right_half_slide_coordinates)

	#sort list of contours by height so we are comparing the correct coordinates from both halves
	left_half_slide_coordinates = sort_by_asc_y(left_half_slide_coordinates)
	right_half_slide_coordinates = sort_by_asc_y(right_half_slide_coordinates)

	left_slide_images = []
	for image in images:
		left_image_half = image.crop(left_crop_area)
		left_slide_images.append(left_image_half)

	right_slide_images = []
	for image in images:
		right_image_half = image.crop(right_crop_area)
		right_slide_images.append(right_image_half)

	#crop and resize
	cropped_left_side_slide_images = crop_images(left_slide_images, left_half_slide_coordinates, left_slides_size)
	cropped_right_side_slide_images = crop_images(right_slide_images, right_half_slide_coordinates, right_slides_size)

	resized_left_side_slide_images = resize_images(cropped_left_side_slide_images)
	resized_right_side_slide_images = resize_images(cropped_right_side_slide_images)

	#merge both image lists and create the output document
	merged_images = merge_images(cropped_left_side_slide_images, cropped_right_side_slide_images)
	return merged_images


# TODOOOOOOOO
# verificar que el orden de las slides es correcto
# pasar de una llamda a dos llamadas a split vertically
# agregar chekcs de minimum size max size, defensive programming
# agreagar caso especiales de ordenamiento de slides diferente como en 6
# poner safety a todos los metodos
# testear




def process_pdf(pdf_name, input_location, output_destination,splitting_mode=0):

	images = extract_images_from_pdf(input_location+pdf_name) # get all pages in pdf as images	
	cropped_slide_images = None #cropped images with a slide in every image
	
	FOUR_SLIDES = 0
	SIX_SLIDES_FIRST_ORDER = 1
	SIX_SLIDES_SECOND_ORDER = 2
	TWO_SLIDES = 3

	if (images and len(images) > 0): #verify that the image extraction was successful
		correct_dimensions = assert_document_dimensions(images[0].size[0], images[0].size[1]) # assert correct document size
		if correct_dimensions:
			if splitting_mode == FOUR_SLIDES:
				cropped_slide_images =  process_4_slide_pdf(images, pdf_name, input_location, output_destination)
			if (splitting_mode == SIX_SLIDES_FIRST_ORDER) or (splitting_mode == SIX_SLIDES_SECOND_ORDER):
				cropped_slide_images = process_6_slide_pdf(images, pdf_name, input_location, output_destination, splitting_mode) #send the pdf to the relevant processing
			if splitting_mode == TWO_SLIDES:
				cropped_slide_images = process_2_slide_pdf(images, pdf_name, input_location, output_destination)


			####UNDER CONSTRUCTION
			if splitting_mode == 10:
				cropped_slide_images = split_vertically(images, pdf_name, 2, (100, 100), (800,800))

			

			#finish the document: resize images and paste them in the output document
			if cropped_slide_images is not None:
				resized_images = resize_images(cropped_slide_images) # increase size of cropped images
				output_document_name = create_new_document(pdf_name, resized_images,output_destination)  #write the output document
				return output_document_name
			else:
				return cropped_slide_images #will be string giving details about encountered errror
		else:
			return "Unsupported document size. Only A4 letter size is supported."
	else:
		return "Failed to extract images from pdf."

	
	

