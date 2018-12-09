## Author: Mario Mendez Diaz

from pdf2image import convert_from_path
import PIL
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

				#ensure found width and height is between bounds
				if(slide_found_width > min_width and slide_found_width < max_width and 
					slide_found_height > min_height and slide_found_height < max_height):
					return slide_coords
	else:
		return None

	
def find_upper_left_slide(image, pdf_name, min_width, min_height, max_width, max_height):	#use the upper left quarter of an image to find the coordinates of a single slide/box

	area = (0,0,image.size[0]/2, image.size[1]/2) # coordinates of upper left quadrant of image
	image_quadrant = image.crop(area) #crop and crate image from cuadrant

	slide_box_coordinates = find_box_using_opencv(image_quadrant, min_width, min_height, max_width, max_height) #find the cords of the slide in the upper left quadrant

	if slide_box_coordinates is None:
		#print "Failed to find slide in left upper quadrant in file "+pdf_name
		return None
	else:
		#print "Success finding slide in left upper quadrant in file "+pdf_name
		return slide_box_coordinates

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


def extract_images_from_pdf(pdf_name):	# use the pdf2image library to convert every page in the pdf to an image
	
	path_to_pdf = os.getcwd()+"/"+pdf_name # get full path of file
	images = None

	try:
		images = convert_from_path(path_to_pdf) #get the images
	except:
		print "Error on pdf \""+pdf_name+"\", could not split file " #catch exception

	return images


def verify_slide(pdf_image,slide_coords,slide_size): #verify the pixels found with open cv and ensure these have black pixels at coordinates

	opencv_image = numpy.array(pdf_image) # convert to open cv image
	grayscale_img = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2GRAY)
	correct_coords = [False, False, False, False] #represents if the coords of each slide truly represent its location

	#check that all coordinates have a black pixel in the image
	#black pixel means that the black edge of a slide is at the coordinates
	for i in range(0,4):
		if(grayscale_img.item(slide_coords[i][1],slide_coords[i][0]) == 0) :   #check left top corner
			if(grayscale_img.item((slide_coords[i][1] + slide_size[1]) -1,(slide_coords[i][0] + slide_size[0] -1 )) == 0):
				correct_coords[i] = True

	if(correct_coords[0] and correct_coords[1] and correct_coords[2] and correct_coords[3]): #if all coords are accurate then just return a single true
		return [True]
	else:
		return correct_coords #if at least one of the coords is not accurate, then return them all

	
def crop_images(images, coords, size):  # crop all images once the coordinates are known, crop only the "individual slides"
	cropped_images = []

	#for each image, do the 4 crops (since 4 slides per image)
	for image in images:
		for i in range(0, len(coords)):
			crop_area = (coords[i][0], coords[i][1], coords[i][0] + size[0], coords[i][1] + size[1]) # area is xy coords, plus width and height
			cropped_image = image.crop(crop_area)
			cropped_images.append(cropped_image)
		
	return cropped_images

def create_new_document(filename, slides,files_processed, output_destination): #create the output document
	
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
	orientation = "Invalid"
	if( width == 1700 and height == 2200):
		orientation = "portrait"
	elif( width == 2200 or height == 1700):
		orientation = "landscape"
	return orientation



################### MAIN PROCESSING FOR EACH PDF , called in a loop from main

def process_pdf(pdf_name, input_location, output_destination,files_processed=1, min_slide_width=200, min_slide_height=200, max_slide_width=1050, max_slide_height=840):
	
	images = extract_images_from_pdf(input_location+pdf_name) # get all pages in pdf as images
	
	if (images and len(images) > 0): #verify that the image extraction was successful

		document_orientation = assert_document_dimensions(images[0].size[0], images[0].size[1])

		if document_orientation == "portrait" or document_orientation == "landscape":  # make sure the dimensions of the document are coorect

			upper_left_box_coordinates = find_upper_left_slide(images[0], pdf_name, min_slide_width, min_slide_height, max_slide_width, max_slide_height) # attempt to find an individual slides so that slides can be centered in their own page

			if(upper_left_box_coordinates is not None): #only proceed if coordinates were found
				slide_coordinates, slide_dimentions = calculate_all_slides_coords(upper_left_box_coordinates, images[0].size) #get all cords from all slides per image
				slides_found = verify_slide(images[0], slide_coordinates, slide_dimentions) #verify if coordinates are accurate and slides are there
				
				if(len(slides_found) < 2):

					print "All slides found successfully in " + pdf_name
					cropped_slide_images = crop_images(images, slide_coordinates, slide_dimentions)
					resized_images = resize_images(cropped_slide_images)
					output_document_name = create_new_document(pdf_name, resized_images, files_processed, output_destination) # DOCUMENT PROCESSED SUCCESFULLY!
					return output_document_name

				else:
					return "Not all slides were found successfully in"
			
			else:
				return "Failed to find individual slides in each page"

		else:
			return "PDF is not letter size (A4 size)"
	else:
		return "Failed to extract pages from document in file"

