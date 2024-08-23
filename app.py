from flask import Flask, render_template, request, redirect, url_for
import cv2
import os

app = Flask(__name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html', image=None)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # 读取图像
        image = cv2.imread(filepath)

        # OpenCV处理, 例如转换为灰度图
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 保存处理后的图像
        processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed-' + file.filename)
        cv2.imwrite(processed_filepath, gray_image)

        return render_template('index.html', image=processed_filepath)

if __name__ == '__main__':
    app.run(debug=True)
