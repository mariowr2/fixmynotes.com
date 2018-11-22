from flask import Flask , render_template, request, flash, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename
#from werkzeug.exceptions import RequestEntityTooLarge, BadRequest
import werkzeug.exceptions
import os
import split_pdf # oh yea
import subprocess


#======================================================
#	APP CONFIGURATION
#======================================================


app = Flask(__name__) #create flask object
app.secret_key = 'secret' #secret cookie key for flash!
MAX_FILE_SIZE = 16 #size in MB

app.config['UPLOAD_FOLDER'] = os.getcwd()+"/uploaded_files" #save path
file_input_location = "/uploaded_files/" # passed to the script that manipulates the pdf 
file_output_location = "served_files"
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE * 1024 * 1024
ALLOWED_EXTENSIONS = set(['pdf']) # allowed file extensions


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
	script_path = os.getcwd()+file_input_location+"delete_pdfs.sh"
	print_debug_msg(uploaded_filename)
	subprocess.call([script_path, uploaded_filename])

#========================================================
#	APP ROUTES
#========================================================


#file uploading
@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
	try:
		if request.method == 'POST':
			if 'pdf' in request.files:
				pdf_file = request.files['pdf']
				if not pdf_file.filename == '':
					if pdf_file and allowed_filename(pdf_file.filename):
						filename = secure_filename(pdf_file.filename) # make sure the filename is not dangerous
						pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))# save the file!				
						return redirect(url_for('uploaded_file',filename=filename))	
					else:
						flash("Only PDF's allowed ;)")
						return redirect(url_for('unsuccesful'))
				else:
					flash("No file selected")
					return redirect(url_for('unsuccesful'))
			else:
				flash("Failed to upload")
				return redirect(url_for('unsuccesful'))

	# TODO , SERVE CUSTOM PAGE WHEN THIS ERROR IS RAISED, SERVER CURRENTLY TERMINATES CONNECTION
	# excpetion documentation at http://werkzeug.pocoo.org/docs/0.14/exceptions/#werkzeug.exceptions.RequestEntityTooLarge
	#http://flask.pocoo.org/docs/1.0/errorhandling/#application-errors
	except werkzeug.exceptions.RequestEntityTooLarge:	
		flash("Maximum file size is 21 MB ;)")
		return redirect(url_for('unsuccesful'))



	return render_template('upload.html') # if not a post request, show the html for submitting the file



#file serving
@app.route('/uploads/<filename>')
def uploaded_file(filename):
	output_filename = split_pdf.process_pdf(filename, file_input_location, file_output_location) #make the magic happen
	output_path = os.getcwd()+"/"+file_output_location #get the directory where the file is stored

	#make sure it was converted correctly
	if allowed_filename(output_filename):
		clear_uploaded_file(filename) # delete the file that was uploaded
		return send_from_directory(output_path, output_filename) #serve the processed file!
	else:
		flash(output_filename)
		return redirect(url_for('unsuccesful'))



@app.route('/unsuccesful')
def unsuccesful():
	return render_template('unsuccesful.html')

@app.route('/succesful')
def succesful():
	return render_template('succesful.html')

@app.route('/error/')
def error():
	return render_template('error.html')

# unsure if works or not
@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_bad_request(e):
	flash("Terrible error ocurred. Maximum file size is "+str(MAX_FILE_SIZE)+" MB")
	return redirect(url_for('unsuccesful'))

#should work
@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
	flash("Terrible error ocurred. (Bad Request)")
	return redirect(url_for('error'))

#works
@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_bad_request(e):
	flash("4 0 4")
	return redirect(url_for('error'))

if __name__ == "__main__":
	app.run()