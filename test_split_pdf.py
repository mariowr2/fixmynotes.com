import split_pdf
import os 

root_path = os.getcwd()
file_input_location_absolute = str(root_path)+"/static/uploaded_files/" 
file_output_location_absolute = str(root_path)+"/static/served_files/"

#filename = "filename.pdf"
#filename = "6_slides.pdf"
filename = "4_slides.pdf"


splitting_mode = 10


# 0 is 4 slides
# 1 and 2 are 6 slides
# 3   2 slide

split_pdf.process_pdf(filename, file_input_location_absolute, file_output_location_absolute, int(splitting_mode)) 
print "Finished"
