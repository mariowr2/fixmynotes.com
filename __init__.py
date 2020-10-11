from flask import Flask , render_template, request, flash, url_for, redirect, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from systemd.journal import JournalHandler
import werkzeug.exceptions
import os
import subprocess
import sys
import time
import logging
import traceback

from app import split_pdf 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.secret_key = 'secret'
MAX_FILE_SIZE = 25 #size in MB

if (len(sys.argv) > 1) and (sys.argv[1] == "DEBUG"):
	app.root_path = os.getcwd()
	os.environ["FLASK_ENV"] = "development"
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	logging.getLogger(__name__).addHandler(console)
	logger.info("Running application in debug mode...")
else:
	app.root_path = '/home/fixmynotes/fixmynotes.com/'
	os.environ["FLASK_ENV"] = "production"
	logger.setLevel(logging.INFO)
	logger.addHandler(JournalHandler())
	logger.info("Running application in production mode...")

app.config['UPLOAD_FOLDER'] = str(app.root_path) + "/static/uploaded_files"  
file_input_location_absolute = str(app.root_path)+"/static/uploaded_files/" 
file_output_location_absolute = str(app.root_path)+"/static/served_files/"
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE * 1024 * 1024
ALLOWED_EXTENSIONS = set(['pdf'])

def allowed_filename(filename):
	return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#========================================================
#	APP ROUTES
#========================================================

#file uploading
@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
	if request.method == 'POST':
		splitting_mode = request.form['mode'] # get the radio button selected
		logger.info("splitting mode set to"+str(splitting_mode))
		if 'pdf' in request.files:
			pdf_file = request.files['pdf']
			if not pdf_file.filename == '':
				if pdf_file and allowed_filename(pdf_file.filename):
					filename = secure_filename(pdf_file.filename) # make sure the filename is not dangerous		
					if filename:
						pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #only save if the filename is safe
						return redirect(url_for('uploaded_file',filename=filename, splitting_mode=splitting_mode))
					else:
						logger.warning("Uploaded file did not pass secure name check")
						flash("There seems to be something wrong with the name of the file you tried to upload.")	
						return redirect(url_for('unsuccesful'))
				else:
					logger.warning("non pdf file uploaded")
					flash("This webapp only works with pdf files.")
					return redirect(url_for('unsuccesful'))
			else:
				logger.warning("no file uploaded")
				flash("No file was selected.")
				return redirect(url_for('unsuccesful'))
		else:
			logger.warning("file upload failed")
			flash("Failed to upload file.")
			return redirect(url_for('unsuccesful'))
	return render_template('upload.html') # if not a post request, show the html for submitting the file


#process pdf, verify successful and then send it to a custom url
@app.route('/uploads/<splitting_mode>/<filename>')
def uploaded_file(filename, splitting_mode):
	logger.info("sending file with mode "+str(splitting_mode))
	output_filename = split_pdf.process_pdf(filename, file_input_location_absolute, file_output_location_absolute, int(splitting_mode)) #use the pdf splitter module to do the work
	logger.info("returned filename is "+output_filename)
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
	logger.info(str(ending_char_index))
	#return redirect(os.path.join(file_output_location_absolute, output_filename))
	#return send_from_directory(file_output_location_absolute, output_filename) 
	return render_template('error.html')


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
