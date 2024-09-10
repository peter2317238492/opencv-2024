from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('bb.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    file = request.files['image']
    function_id = int(request.form['function_id'])

    in_memory_file = BytesIO()
    file.save(in_memory_file)
    data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)

    if function_id == 2:  # 例如图像分割功能
        threshold_value = int(request.form.get('threshold', 127))
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, segmented_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)
        _, img_encoded = cv2.imencode('.png', segmented_image)
        return send_file(BytesIO(img_encoded), mimetype='image/png')

    # 处理其他function_id的情况...
    
    
if __name__ == '__main__':
    app.run(debug=True)
