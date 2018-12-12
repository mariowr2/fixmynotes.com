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


def find_box_using_opencv(image, min_width, min_height, max_width, max_height):	#find a slide/box in an image (should only pass images that contain a single slide)
	lower_bound_pixel = 0 #values used in colour thresholding
	upper_bound_pixel = 5
	opencv_image = numpy.array(image) # convert to open cv image

	#open cv tings start
	grayscale_img = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2GRAY)

	mask = cv2.inRange(grayscale_img, lower_bound_pixel,upper_bound_pixel) #find black elements (assuming black boxes)
	contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]#find contours in mask

	if len(contours) > 0:
		slide_coords = max(contours, key = cv2.contourArea) #get the biggest contour
		if len(slide_coords) == 4: #ensure precisely 4 coords, slides are squares

				slide_found_width = (slide_coords[2][0])[0] - (slide_coords[0][0])[0] #get width and heihgt
				slide_found_height = (slide_coords[2][0])[1] - (slide_coords[0][0])[1]

				#ensure found width and height is between allowed bounds
				if(slide_found_width > min_width and slide_found_width < max_width and 
					slide_found_height > min_height and slide_found_height < max_height):
					return slide_coords
	else:
		return None

#used when finding 4 slides
def find_upper_left_slide(image, pdf_name, min_width, min_height, max_width, max_height):	#use the upper left quarter of an image to find the coordinates of a single slide/box

	area = (0,0,image.size[0]/2, image.size[1]/2) # coordinates of upper left quadrant of image)
	image_quadrant = image.crop(area) 

	slide_box_coordinates = find_box_using_opencv(image_quadrant, min_width, min_height, max_width, max_height) #find the cords of the slide in the upper left quadrant

	if slide_box_coordinates is None:
		#print "Failed to find slide in left upper quadrant in file "+pdf_name
		return None
	else:
		#print "Success finding slide in left upper quadrant in file "+pdf_name
		return slide_box_coordinates


#return the three biggest 4-point contours given a list of contours
def get_three_largest_contours(contours):
	
	three_largest_contours = []
	indexes_with_more_than_four_points = []

	# get the indexes of contours with more than 4 points, since they are not slides! 
	for i in range(0,len(contours)-1):
		if len(contours[i]) > 4:
			indexes_with_more_than_four_points.append(i)


	#delete the indexes of the contours
	for index in indexes_with_more_than_four_points:
		if index < len(contours):
			del contours[index]

	#sort the remaining list by area and append the first three contours
	sorted_contours = sorted(contours, key=lambda x: cv2.contourArea(x))
	three_largest_contours.append(sorted_contours[0])
	three_largest_contours.append(sorted_contours[1])
	three_largest_contours.append(sorted_contours[2])	

	return three_largest_contours


#return the contour coordinates of all 3 slides in the left half of the image
def find_left_slides_using_opencv(image, min_width, min_height, max_width, max_height):
	
	lower_bound_pixel = 0 #values used in colour thresholding
	upper_bound_pixel = 5
	opencv_image = numpy.array(image) # convert to open cv image
	second_image = opencv_image.copy()

	min_slide_area = min_width * min_height
	max_slide_area = max_width * max_height

	#open cv tings start
	grayscale_img = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2GRAY)

	mask = cv2.inRange(grayscale_img, lower_bound_pixel,upper_bound_pixel) #find black elements (assuming black boxes)
	contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]#find contours in mask

	if len(contours) > 2: #make sure at least 3 contours were found in the image
		three_largest_contours = get_three_largest_contours(contours)  #get the three largest contours
		

		#check that the returned contours are inside the allowed bounds UGLY HACK
		slides_inside_bounds = (cv2.contourArea(three_largest_contours[0]) > min_slide_area and cv2.contourArea(three_largest_contours[0]) < max_slide_area)
		slides_inside_bounds = slides_inside_bounds and (cv2.contourArea(three_largest_contours[1]) > min_slide_area and cv2.contourArea(three_largest_contours[1]) < max_slide_area)
		slides_inside_bounds = slides_inside_bounds and (cv2.contourArea(three_largest_contours[2]) > min_slide_area and cv2.contourArea(three_largest_contours[2]) < max_slide_area)
		
		if slides_inside_bounds:
			return three_largest_contours
		else:
			return None
	else:
		return None #return empty list


#used when finding 6 slides total, returns the coordinates of all slides in the left half of the image
def find_left_slides(image, pdf_name, min_width, min_height, max_width, max_height):

	area = (0,0,image.size[0]/2, image.size[1])
	#area = (image.size[0]/2,0,image.size[0], image.size[1]) #right half of image
	image_quadrant = image.crop(area)
	left_slide_coordinates = find_left_slides_using_opencv(image_quadrant, min_width, min_height, max_width, max_height)
	return left_slide_coordinates





def calculate_all_slides_coords(upper_left_coords, pdf_size): #calculate one pair of coordinates for all boxes AND width and height of each box

	quadrant_size = (pdf_size[0]/2, pdf_size[1]/2)	
	box_width = upper_left_coords[2][0][0] - upper_left_coords[0][0][0]
	box_height = upper_left_coords[2][0][1] - upper_left_coords[0][0][1]

	#first get measurements relative to the distance of the found box and the edges of the quadrants
	left_x_distance = upper_left_coords[0][0][0]#(x coordinate of left edge)
	right_x_distance = quadrant_size[0] - upper_left_coords[2][0][0]# difference between x corordinate of right edge and edge of quadrant

	y_top_distance = upper_left_coords[0][0][1]# distance from top of box to upper edge of quadrant
	y_lower_distance = quadrant_size[1] - upper_left_coords[2][0][1] # difference between y coordinate of lower edge and the height of the quadrany

	# coordinates of upper left box
	upper_left_quadrant_x = upper_left_coords[0][0][0] #upper left box first
	upper_left_quadrant_y = upper_left_coords[0][0][1]
	
	boxes_coords = [[upper_left_quadrant_x, upper_left_quadrant_y]] # add upper left box

	# coordinates of upper right box
	upper_right_cuadrant_x = quadrant_size[0] + right_x_distance #x coord of upper right quadrant, upper left edge
	upper_right_cuadrant_y = y_top_distance #y coord of upper right quadrant , upper left edge
	boxes_coords.insert(1,[upper_right_cuadrant_x, upper_right_cuadrant_y])

	#coordinates of lower left box
	lower_left_cuadrant_x = upper_left_quadrant_x
	lower_left_cuadrant_y = quadrant_size[1] + y_lower_distance
	boxes_coords.insert(2,[lower_left_cuadrant_x,lower_left_cuadrant_y])

	#coordinates of lower right box
	lower_right_cuadrant_x = upper_right_cuadrant_x
	lower_right_cuadrant_y = lower_left_cuadrant_y
	boxes_coords.insert(3,[lower_right_cuadrant_x, lower_right_cuadrant_y])

	return boxes_coords, (box_width, box_height)


#calculate the rest of the coordinates using the coordinates already acquired
def calculate_remaining_slides_coordinates(left_half_slides_coords, pdf_size):

	left_boxes_coords = None # stores the top left corner of all 6 slides in the document
	right_boxes_coords = None

	quadrant_size = (pdf_size[0]/2, pdf_size[1])

	#calculate the width and height for all slides
	box_width = left_half_slides_coords[0][3][0][0] - left_half_slides_coords[0][0][0][0]
	box_height = left_half_slides_coords[0][2][0][1] - left_half_slides_coords[0][0][0][1]

	#calculate the distance from each slide to right borders of the document
	box_distance_right_border = quadrant_size[0] - left_half_slides_coords[0][3][0][0]


	#first dump all top left coords of the 3 slides that have been found already
	left_boxes_coords = [[ left_half_slides_coords[0][0][0][0], left_half_slides_coords[0][0][0][1]]]
	left_boxes_coords.insert(1, [left_half_slides_coords[1][0][0][0], left_half_slides_coords[1][0][0][1]])
	left_boxes_coords.insert(2, [left_half_slides_coords[2][0][0][0], left_half_slides_coords[2][0][0][1]])


	#sort coordinates in ascending order depending on their y coordinate! ; very important
	left_boxes_coords = sorted(left_boxes_coords,key=lambda l:l[1])

	
	#now calculate the coordinates on the other half of the image

	#first top right slide, only need to calculate the x once!
	
	#top_right_slide_x = left_boxes_coords[0][0] + box_width +(2 * box_distance_right_border) 
	top_right_slide_x = pdf_size[0]/2 + box_distance_right_border
	top_right_slide_y = left_boxes_coords[0][1]
	right_boxes_coords = [[top_right_slide_x, top_right_slide_y]]

	#middle right slide
	middle_right_slide_y = left_boxes_coords[1][1]
	right_boxes_coords.insert(1, [top_right_slide_x, middle_right_slide_y])

	#bottom right slide
	bottom_right_slide_y = left_boxes_coords[2][1]
	right_boxes_coords.insert(2, [top_right_slide_x, bottom_right_slide_y])

	print left_boxes_coords
	print right_boxes_coords
	

	return left_boxes_coords, right_boxes_coords, (box_width, box_height)


def extract_images_from_pdf(pdf_file_path):	# use the pdf2image library to convert every page in the pdf to an image
	
	images = None

	try:
		images = convert_from_path(pdf_file_path) #get the images
	except:
		print "Error on pdf \""+pdf_name+"\", could not split file " #catch exception

	return images


def verify_slide(pdf_image,slide_coords,slide_size, slide_number): #verify the pixels found with open cv and ensure these have black pixels at coordinates

	opencv_image = numpy.array(pdf_image) # convert to open cv image
	grayscale_img = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2GRAY)
	correct_coords = [False, False, False, False] #represents if the coords of each slide truly represent its location

	#check that all coordinates have a black pixel in the image
	#black pixel means that the black edge of a slide is at the coordinates
	for i in range(0,slide_number):
		if(grayscale_img.item(slide_coords[i][1],slide_coords[i][0]) == 0) :   #check left top corner
			if(grayscale_img.item((slide_coords[i][1] + slide_size[1]) -1,(slide_coords[i][0] + slide_size[0] -1 )) == 0):
				correct_coords[i] = True


	if slide_number == 4:
		if(correct_coords[0] and correct_coords[1] and correct_coords[2] and correct_coords[3]): #if all coords are accurate then just return a single true
			return [True]
		else:
			return correct_coords
	if slide_number == 3:
		if(correct_coords[0] and correct_coords[1] and correct_coords[2]):
			return [True]
		else:
			return correct_coords
	else:
		return correct_coords


	
def crop_images(images, coords, size):  # crop all images once the coordinates are known, crop only the "individual slides"
	cropped_images = []

	#for each image, do the 4 crops (since 4 slides per image)
	print "length of coords "+str(len(coords))
	print "number of images "+str(len(images))

	for image in images:
		for i in range(0, len(coords)):
			crop_area = (coords[i][0], coords[i][1], coords[i][0] + size[0], coords[i][1] + size[1]) # area is xy coords, plus width and height
			cropped_image = image.crop(crop_area)
			cropped_images.append(cropped_image)
	return cropped_images



def create_new_document(filename, slides, output_destination): #create the output document
	
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

def resize_images(images): #resize all images before they are included in the output	
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

################### MAIN PROCESSING FOR EACH PDF , called in a loop from main
def process_6_slide_pdf(images, pdf_name, input_location, output_destination, splitting_mode):
	min_slide_width = 50
	min_slide_height = 50
	max_slide_width = 1050
	max_slide_height = 840

	print_debug_msg("Doing 6 slides, mode "+str(splitting_mode))
	
	#get the coordinates for all of the slides in the left half of the iamge
	left_slides_coords = find_left_slides(images[0], pdf_name, min_slide_width, min_slide_height, max_slide_width, max_slide_height)
	
	if left_slides_coords:

		left_side_slide_coords, right_side_slide_coords, slide_size = calculate_remaining_slides_coordinates(left_slides_coords, images[0].size)
		#left_slides_found = verify_slide(images[0], left_side_slide_coords, slide_size, 3) #verify if coordinates are accurate and slides are there
		#right_slides_found = verify_slide(images[0],right_side_slide_coords, slide_size, 3)

		left_slides_found = True
		right_slides_found = True
		if left_slides_found and right_slides_found: #proceed only if both the right and left side were found
			
			combined_slides = merge_slides_from_halves(left_side_slide_coords, right_side_slide_coords, splitting_mode)	


			cropped_slide_images = crop_images(images,combined_slides, slide_size)


			#print_debug_msg("number of images cropped is "+str(len(cropped_slide_images)))
			

			resized_images = resize_images(cropped_slide_images)

			#print_debug_msg("number of images resized is "+str(len(resized_images)))

			# for i in range(0, len(resized_images)):
			# 	resized_images[i].save("resize"+str(i)+".png", "PNG")


			output_document_name = create_new_document(pdf_name, resized_images,output_destination) # DOCUMENT PROCESSED SUCCESFULLY!

			#print_debug_msg("filename is "+output_document_name)
			return output_document_name
			

		else:
			return "Program was unable to verify that all slides were found"
	else:
		return "Failed to find 3 slides on the image."






def process_4_slide_pdf(images, pdf_name, input_location, output_destination):
	
	min_slide_width = 200
	min_slide_height = 200
	max_slide_width = 1050
	max_slide_height = 840

	print_debug_msg("Doing 4 slides")

	upper_left_box_coordinates = find_upper_left_slide(images[0], pdf_name, min_slide_width, min_slide_height, max_slide_width, max_slide_height) # attempt to find an individual slides so that slides can be centered in their own page

	if(upper_left_box_coordinates is not None): #only proceed if coordinates were found
		
		slide_coordinates, slide_dimentions = calculate_all_slides_coords(upper_left_box_coordinates, images[0].size) #get all cords from all slides per image
		#slides_found = verify_slide(images[0], slide_coordinates, slide_dimentions, 4) #verify if coordinates are accurate and slides are there
		slides_found = [True]
		if(len(slides_found) == 1):

			print "All slides found successfully in " + pdf_name
			cropped_slide_images = crop_images(images, slide_coordinates, slide_dimentions)
			resized_images = resize_images(cropped_slide_images)
			output_document_name = create_new_document(pdf_name, resized_images,output_destination) # DOCUMENT PROCESSED SUCCESFULLY!
			return output_document_name

		else:
			return "Program was unable to verify that all slides were found"
	
	else:
		return "Failed to find individual slide."

		
	



def process_pdf(pdf_name, input_location, output_destination,splitting_mode=0):

	images = extract_images_from_pdf(input_location+pdf_name) # get all pages in pdf as images
	
	if (images and len(images) > 0): #verify that the image extraction was successful

		correct_dimensions = assert_document_dimensions(images[0].size[0], images[0].size[1]) # get size of document

		if correct_dimensions and splitting_mode == 0:
			return process_4_slide_pdf(images, pdf_name, input_location, output_destination)

		if correct_dimensions and (splitting_mode == 1) or (splitting_mode == 2):
			filename = process_6_slide_pdf(images, pdf_name, input_location, output_destination, splitting_mode)
			print_debug_msg("filename is "+filename)
			return filename
		
		else:
			return "Incorrect dimensions or incorrect mode"
	else:
		return "Failed to extract images from pdf"
	

	return "epic fail"

	

