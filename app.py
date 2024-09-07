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
    print(request.files)
    print(request.form)

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

        # 打码:在选中长方形的区域内进行模糊处理
        image[y1:y2, x1:x2] = cv2.GaussianBlur(image[y1:y2, x1:x2], (23, 23), 30)
        
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
        
        #判断下方是否有白边,如果有,找到白边的最高位置,然后裁剪
        gray = cv2.cvtColor(final_image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            y = min(contours[0].reshape(-1, 2)[:, 1])
            final_image = final_image[:y, :]
            
        
        #在图片的上方增加白边,使得图片为证件照大小
        top = 531 - final_image.shape[0]
        final_image = cv2.copyMakeBorder(final_image, top, 0, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        
        _, img_encoded = cv2.imencode('.png', final_image)
        return send_file(BytesIO(img_encoded), mimetype='image/png')
        

    if function_id == 4:  # 图像换背景功能
        # Check if files are uploaded
        if 'foreground' not in request.files or 'background' not in request.files:
            return "Missing foreground or background file", 400
        
        foreground_file = request.files['foreground']
        background_file = request.files['background']
        
        # Log to verify files are received
        print(f"Foreground file: {foreground_file.filename}")
        print(f"Background file: {background_file.filename}")
        
        if not foreground_file or not background_file:
            return "Foreground or background file is missing", 400


        # Read the images into OpenCV
        foreground_data = np.frombuffer(foreground_file.read(), dtype=np.uint8)
        background_data = np.frombuffer(background_file.read(), dtype=np.uint8)
        foreground_image = cv2.imdecode(foreground_data, cv2.IMREAD_COLOR)
        background_image = cv2.imdecode(background_data, cv2.IMREAD_COLOR)

        # Resize background to match foreground
        background_image_resized = cv2.resize(background_image, (foreground_image.shape[1], foreground_image.shape[0]))

        # Perform background replacement (assuming transparency)
        gray = cv2.cvtColor(foreground_image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

        # Invert mask and combine images
        background_mask = cv2.bitwise_not(mask)
        foreground_part = cv2.bitwise_and(foreground_image, foreground_image, mask=mask)
        background_part = cv2.bitwise_and(background_image_resized, background_image_resized, mask=background_mask)

        # Combine both parts
        result_image = cv2.add(foreground_part, background_part)

        # Return processed image
        _, img_encoded = cv2.imencode('.png', result_image)
        return send_file(BytesIO(img_encoded), mimetype='image/png') 
        
    if function_id == 6: #图片旋转
        # 获取旋转角度
        angle = int(request.form.get('angle', 90)) # 默认旋转90度
        # 获取图像的宽度和高度
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        # 如果是负数，转换为正数
        if angle < 0:
            angle = 360 + angle
        # 如果是90,180,270,360的倍数，直接旋转
        if angle % 90 == 0:
            if angle % 180 == 0:
                # 180度和360度旋转不需要改变尺寸
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated_image = cv2.warpAffine(image, M, (w, h))
            else:
                # 90度和270度旋转需要交换宽度和高度
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                new_w, new_h = h, w
                M[0, 2] += (new_w / 2) - center[0]
                M[1, 2] += (new_h / 2) - center[1]
                rotated_image = cv2.warpAffine(image, M, (new_w, new_h))
            _, img_encoded = cv2.imencode('.png', rotated_image)
        else:
            # 任意角度旋转
            # 旋转图像
            

            # 计算旋转矩阵
            M = cv2.getRotationMatrix2D(center, angle, 1.0)

            # 计算旋转后的图像边界框
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))

            # 调整旋转矩阵以考虑平移
            M[0, 2] += (new_w / 2) - center[0]
            M[1, 2] += (new_h / 2) - center[1]

            # 执行旋转并调整图像大小
            rotated_image = cv2.warpAffine(image, M, (new_w, new_h))

            _, img_encoded = cv2.imencode('.png', rotated_image)
    if function_id == 7:  # 图片翻转
        flip_direction = request.form.get('flip_direction')
        if flip_direction == 'horizontal':
            flipped_image = cv2.flip(image, 1)
        elif flip_direction == 'vertical':
            flipped_image = cv2.flip(image, 0)
        else:
            return 'Invalid flip direction', 400

        _, img_encoded = cv2.imencode('.png', flipped_image)
        return send_file(BytesIO(img_encoded), mimetype='image/png')
            
            
    return send_file(BytesIO(img_encoded), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
