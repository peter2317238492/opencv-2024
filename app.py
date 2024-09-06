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
    
    if function_id == 1:  # 区域打码功能
        # 获取屏幕分辨率
        screen_res = 1280, 720  # 可以根据实际情况调整
        scale_width = screen_res[0] / image.shape[1]
        scale_height = screen_res[1] / image.shape[0]
        scale = min(scale_width, scale_height)
        
        # 缩放图像
        window_width = int(image.shape[1] * scale)
        window_height = int(image.shape[0] * scale)
        resized_image = cv2.resize(image, (window_width, window_height))

        # 展示一个窗口，将图像缩放到合适的大小，用户用鼠标选择打码区域
        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                print('Start Mouse Position:', x, y)
                point1.append((x, y))
            if event == cv2.EVENT_LBUTTONUP:
                print('End Mouse Position:', x, y)
                point2.append((x, y))
                cv2.rectangle(resized_image, point1[0], point2[0], (0, 255, 0), 2)
                cv2.imshow('image', resized_image)

        point1 = []
        point2 = []
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', on_mouse)
        cv2.imshow('image', resized_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # 将缩放后的坐标转换回原始图像的坐标
        x1, y1 = int(point1[0][0] / scale), int(point1[0][1] / scale)
        x2, y2 = int(point2[0][0] / scale), int(point2[0][1] / scale)

        # 打码
        image[y1:y2, x1:x2] = 0
        _, img_encoded = cv2.imencode('.png', image)
        return send_file(BytesIO(img_encoded), mimetype='image/png')
    

if __name__ == '__main__':
    app.run(debug=True)
