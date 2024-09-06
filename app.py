from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
import dlib
import os
from imutils import face_utils
from io import BytesIO
import onnxruntime as ort




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
    

    if function_id == 3:  # 证件照制作
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        #检测人脸
        rects = detector(gray, 0)
        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            
        
                
        from imutils.face_utils import FaceAligner
        
        fa= FaceAligner(predictor, desiredFaceWidth=256,desiredFaceHeight=384)
        faceAligned = fa.align(image, gray, rect)
        
        onnx_session = ort.InferenceSession("modnet.onnx")
        
        readytomatting = cv2.resize(faceAligned, (512, 512))
        
        # Prepare the input data
        image_normalized=readytomatting.astype(np.float32)/255.0
        image_normalized = np.transpose(image_normalized, (2, 0, 1))
        image_input = image_normalized[np.newaxis, :]  # 添加batch维度
        onnx_inputs = {onnx_session.get_inputs()[0].name: image_input}
        onnx_outputs = onnx_session.run(None, onnx_inputs)
        matte = onnx_outputs[0][0][0]
        
        # 创建一个白色背景图像
        white_background = np.ones_like(readytomatting) * 255

        # 增加alpha通道维度
        matte = np.expand_dims(matte, axis=-1)

        # 合成前景和白色背景
        foreground = readytomatting * matte + white_background * (1 - matte)
        #调整为证件照大小
        foreground=foreground.astype(np.uint8)
        final_image = cv2.resize(foreground, (413, 531))
        
        _, img_encoded = cv2.imencode('.png', final_image)
        return send_file(BytesIO(img_encoded), mimetype='image/png')
        

        
        

if __name__ == '__main__':
    app.run(debug=True)
