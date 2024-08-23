from flask import Flask, render_template, request, redirect, url_for
import cv2
import os

app = Flask(__name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
current_image = None

@app.route('/')
def index():
    return render_template('index.html', image=None)

@app.route('/upload', methods=['POST'])
def upload():
    global current_image
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        current_image = filepath
        return render_template('index.html', image={'original': current_image, 'processed': current_image})

@app.route('/process', methods=['POST'])
def process():
    global current_image
    if not current_image:
        return redirect(url_for('index'))

    image = cv2.imread(current_image)
    process_type = request.form['processType']

    if process_type == 'gray':
        processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif process_type == 'crop':
        width = int(request.form['width'])
        height = int(request.form['height'])
        processed_image = cv2.resize(image, (width, height))
        processed_image = processed_image[0:height, 0:width]  # Simple crop to top-left
    elif process_type == 'resize':
        width = int(request.form['width'])
        height = int(request.form['height'])
        processed_image = cv2.resize(image, (width, height))

    processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed-' + os.path.basename(current_image))
    cv2.imwrite(processed_filepath, processed_image)

    return render_template('index.html', image={'original': current_image, 'processed': processed_filepath})

if __name__ == '__main__':
    app.run(debug=True)
