from flask import Flask , render_template, request, flash, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os


#======================================================
#	APP CONFIGURATION
#======================================================


app = Flask(__name__) #create flask object
app.secret_key = 'secret' #secret cookie key for flash!


app.config['UPLOAD_FOLDER'] = os.getcwd()+"/uploaded_files" #save path
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
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
					flash("No file seleceted")
					return redirect(url_for('unsuccesful'))
			else:
				flash("Failed to upload")
				return redirect(url_for('unsuccesful'))

	# TODO , SERVE CUSTOM PAGE WHEN THIS ERROR IS RAISED, SERVER CURRENTLY TERMINATES CONNECTION
	# excpetion documentation at http://werkzeug.pocoo.org/docs/0.14/exceptions/#werkzeug.exceptions.RequestEntityTooLarge
	except RequestEntityTooLarge:	
		flash("Maximum file size is 21 MB ;)")
		return redirect(url_for('unsuccesful'))
	except:
		flash("Unkown error ocurred. CONTACT ADMIN")
		return redirect(url_for('unsuccesful'))


	return render_template('upload.html') # if not a post request, show the html for submitting the file



#file serving
@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/unsuccesful')
def unsuccesful():
	return render_template('unsuccesful.html')

@app.route('/succesful')
def succesful():
	return render_template('succesful.html')



if __name__ == "__main__":
	app.run()