from flask import Flask , render_template, request, flash, url_for, redirect   #flask basic templates   request to get the actual file
from flask_uploads import UploadSet, configure_uploads, patch_request_class #upload set used to instantiate the uploads object
from werkzeug.utils import secure_filename
import os

# flask documentation at https://pythonhosted.org/Flask-Uploads/#flaskext.uploads.UploadSet


app = Flask(__name__) #create flask object
app.secret_key = 'secret' #secret cookie key for flash!



pdf = UploadSet('pdf', 'pdf') # create Upload Set object

#configure upload sets object

app.config['UPLOADED_PDF_DEST'] = os.getcwd()+"/static/img" 
#!!!!app.config['UPLOADED_PDF_URL'] = URL WHERE FILES WILL BE SERVED
#app.config['UPLOADED_PDF_ALLOW'] = '' ALLOWED FILE EXTENSIONS
patch_request_class(app, 16777216) #set maximum size to 16MB
configure_uploads(app, pdf) #set configure values



@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
	if request.method == 'POST':
		if 'pdf' in request.files:
			pdf_file = request.files['pdf']
			filename = pdf.save(request.files['pdf'])
			flash("Notes for " +filename+" F I X E D")
			return render_template('succesful.html')		
		else:
			flash("Failed to upload")
			return redirect(url_for('unsuccesful'))
	return render_template('upload.html') # if not a post request, show the html


@app.route('/unsuccesful')
def unsuccesful():
	return render_template('unsuccesful.html')

@app.route('/succesful')
def succesful():
	return render_template('succesful.html')

def print_debug_msg(msg):
	print "************************ "+msg

if __name__ == "__main__":
	app.run()