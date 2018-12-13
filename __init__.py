from flask import Flask , render_template, request, flash, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename
import werkzeug.exceptions
import os
import split_pdf # oh yea
import subprocess
import sys
#new import for logging
from logging.handlers import RotatingFileHandler
from flask import request, jsonify
from time import strftime
import time

import logging
import traceback



#======================================================
#	APP CONFIGURATION
#======================================================


app = Flask(__name__) #create flask object
app.secret_key = 'secret' #secret cookie key for flash!
MAX_FILE_SIZE = 25 #size in MB

app.root_path = None
#determine if the app is being run in DEBUG mode and update app root paths
if (len(sys.argv) > 1) and (sys.argv[1] == "DEBUG"):
	app.root_path = os.getcwd()
	print "Running application in debug mode..."
else:
	app.root_path = '/var/www/Fix/Fix'
	print "Running application in production mode..."

app.config['UPLOAD_FOLDER'] = str(app.root_path) + "/static/uploaded_files"  
file_input_location_absolute = str(app.root_path)+"/static/uploaded_files/" 
file_output_location_absolute = str(app.root_path)+"/static/served_files/"

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE * 1024 * 1024
ALLOWED_EXTENSIONS = set(['pdf']) # allowed file extensions

#logger obj
logger = logging.getLogger(__name__)


#=======================================================
# DEFS
#=======================================================
def print_debug_msg(msg):
	print "************************ "+msg

#check the filename is allowed
def allowed_filename(filename):
	return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#delete the uploaded file once it has been processed
def clear_uploaded_file(uploaded_filename):
	script_path = file_input_location_absolute+"delete_pdfs.sh"
	print_debug_msg("Deleting processed file "+uploaded_filename)
	subprocess.call([script_path, file_input_location_absolute,uploaded_filename])


#========================================================
#	APP ROUTES
#========================================================


#file uploading
@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
	if request.method == 'POST':

		splitting_mode = request.form['mode'] # get the radio button selected
		print "SPLITTING MODE SET TO "+str(splitting_mode)

		if 'pdf' in request.files:
			pdf_file = request.files['pdf']
			if not pdf_file.filename == '':
				if pdf_file and allowed_filename(pdf_file.filename):
					filename = secure_filename(pdf_file.filename) # make sure the filename is not dangerous		
					if filename:
						pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #only save if the filename is safe
						return redirect(url_for('uploaded_file',filename=filename, splitting_mode=splitting_mode))
					else:
						flash("There seems to be something wrong with the name of the file you tried to upload.")	
						return redirect(url_for('unsuccesful'))
				else:
					clear_uploaded_file(pdf_file.filename) # delete the file that was uploaded
					flash("This webapp only works with pdf files.")
					return redirect(url_for('unsuccesful'))
			else:
				flash("No file was selected.")
				return redirect(url_for('unsuccesful'))
		else:
			flash("Failed to upload file.")
			return redirect(url_for('unsuccesful'))
	return render_template('upload.html') # if not a post request, show the html for submitting the file



#process pdf, verify successful and then send it to a custom url
@app.route('/uploads/<splitting_mode>/<filename>')
def uploaded_file(filename, splitting_mode):
	

	print "sending file with mode "+str(splitting_mode)

	output_filename = split_pdf.process_pdf(filename, file_input_location_absolute, file_output_location_absolute, int(splitting_mode)) #use the pdf splitter module to do the work
	print_debug_msg("returned filename is "+output_filename)


	if allowed_filename(output_filename):
		return redirect(url_for('serve_file', output_filename=output_filename))
	else:
		flash(output_filename)
		return redirect(url_for('unsuccesful'))



#serve the file with the new name as part of the url for
@app.route('/fixed/<output_filename>')
def serve_file(output_filename):
	uploaded_filename = output_filename[4:]
	ending_char_index = len(uploaded_filename) -1
	print_debug_msg(str(ending_char_index))
	clear_uploaded_file(uploaded_filename) # delete the file that was uploaded
	return send_from_directory(file_output_location_absolute, output_filename) #serve the processed file!



@app.route('/unsuccesful')
def unsuccesful():
	return render_template('unsuccesful.html')


@app.route('/error/')
def error():
	return render_template('error.html')


#====================================================
#	ERROR HANDLING AND LOGGING
#===================================================



# unsure if works or not
@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_request_too_large(e):
	flash("Terrible error ocurred. Maximum file size is "+str(MAX_FILE_SIZE)+" MB")
	return redirect(url_for('unsuccesful'))


@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
	flash("Terrible error ocurred. (Bad Request)")
	return redirect(url_for('error'))


@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_not_found(e):
	flash("4 0 4")
	return redirect(url_for('error'))



if __name__ == "__main__":
	app.run()
