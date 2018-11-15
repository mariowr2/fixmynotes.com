from flask import Flask , render_template, request   #flask basic templates   request to get the actual file
from flask_uploads import UploadSet, configure_uploads, IMAGES  #upload set used to instantiate the uploads object

app = Flask(__name__)

photos = UploadSet('photos', IMAGES) # args is name and type 
# IMAGES type of upload .. see pythonhosted.org/Flask-Uploads.


app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos) #pass app and photos object

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST' and 'photo' in request.files: #if find photo and post request
		filename = photos.save(request.files['photo'])
		return filename
	return render_template('upload.html')


if __name__ == "__main__":
	app.run()