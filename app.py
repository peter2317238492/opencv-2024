from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
import dlib
import os
from imutils import face_utils
from io import BytesIO
import onnxruntime as ort
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from threading import Thread

class ImageMosaicEditor: #打码编辑器
    def __init__(self, root):
        self.root = root
        self.root.title("图像编辑器")

        # 定义窗口的总宽度和高度
        self.window_width = 1600  # 整个窗口宽度
        self.window_height = 600  # 整个窗口高度（左右各显示一张图）

        # 创建工具栏
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.select_button = tk.Button(self.toolbar, text="选择打码区域", command=self.select_area)
        self.select_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.brush_button = tk.Button(self.toolbar, text="涂抹打码", command=self.brush_mode)
        self.brush_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.undo_button = tk.Button(self.toolbar, text="撤销", command=self.undo)
        self.undo_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.finish_button = tk.Button(self.toolbar, text="完成", command=self.finish)
        self.finish_button.pack(side=tk.LEFT, padx=2, pady=2)

        # 创建拖动条调整笔刷大小
        self.brush_size_slider = tk.Scale(self.toolbar, from_=5, to=50, orient=tk.HORIZONTAL, label="笔刷大小")
        self.brush_size_slider.set(20)  # 默认值为20
        self.brush_size_slider.pack(side=tk.LEFT, padx=2, pady=2)

        # 创建画布
        self.canvas = tk.Canvas(root, width=self.window_width, height=self.window_height)
        self.canvas.pack()

        # 加载图像
        self.load_image()

        # 初始化变量
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect_id = None
        self.history = []
        self.brush_mode_active = False

    def display_images(self):
        # 计算每个图像的宽度和高度
        image_width = self.window_width // 2
        image_height = self.window_height

        # 将图像按比例缩放到合适的大小
        self.original_image_resized = self.resize_image(self.original_image, image_width, image_height)
        self.processed_image_resized = self.resize_image(self.processed_image, image_width, image_height)

        # 将OpenCV图像转换为PIL图像
        self.original_image_pil = Image.fromarray(cv2.cvtColor(self.original_image_resized, cv2.COLOR_BGR2RGB))
        self.processed_image_pil = Image.fromarray(cv2.cvtColor(self.processed_image_resized, cv2.COLOR_BGR2RGB))

        # 将PIL图像转换为ImageTk图像
        self.original_image_tk = ImageTk.PhotoImage(self.original_image_pil)
        self.processed_image_tk = ImageTk.PhotoImage(self.processed_image_pil)

        # 在画布上显示图像
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.original_image_tk)
        self.canvas.create_image(image_width, 0, anchor=tk.NW, image=self.processed_image_tk)

    def load_image(self):
        self.original_image = cv2.imread('input_image.jpg')
        self.processed_image = self.original_image.copy()

        self.display_images()

    def resize_image(self, image, max_width, max_height):
        h, w = image.shape[:2]
        # 计算宽高比，确保等比例缩放
        scale = min(max_width / w, max_height / h)
        return cv2.resize(image, (int(w * scale), int(h * scale)))

    def select_area(self):
        self.brush_mode_active = False
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def brush_mode(self):
        self.brush_mode_active = True
        self.canvas.bind("<B1-Motion>", self.on_brush_drag)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        self.end_x = event.x
        self.end_y = event.y
        self.rect = (self.start_x, self.start_y, self.end_x, self.end_y)
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.apply_blur()  # 直接应用打码效果

    def on_brush_drag(self, event):
        if self.brush_mode_active:
            # 获取画布上的鼠标坐标
            x, y = event.x, event.y

            # 计算从画布到实际图像的坐标映射
            image_width = self.window_width // 2
            scale_x = self.original_image.shape[1] / image_width
            scale_y = self.original_image.shape[0] / self.window_height

            # 将鼠标坐标转换为图像坐标
            img_x = int(x * scale_x)
            img_y = int(y * scale_y)

            # 确定涂抹区域的范围（根据拖动条确定笔刷大小）
            brush_size = self.brush_size_slider.get()  # 获取笔刷大小
            x1 = max(0, img_x - brush_size)
            y1 = max(0, img_y - brush_size)
            x2 = min(self.processed_image.shape[1], img_x + brush_size)
            y2 = min(self.processed_image.shape[0], img_y + brush_size)

            # 对涂抹区域应用模糊处理
            roi = self.processed_image[y1:y2, x1:x2]
            blurred_roi = cv2.GaussianBlur(roi, (15, 15), 0)

            # 保存历史状态
            self.history.append(self.processed_image.copy())

            # 应用模糊效果
            self.processed_image[y1:y2, x1:x2] = blurred_roi

            # 实时显示涂抹打码效果
            self.display_images()

    def apply_blur(self):
        if not self.rect:
            messagebox.showwarning("警告", "请先选择打码区域")
            return

        # 获取选择区域的坐标
        x1, y1, x2, y2 = self.rect
        # 计算缩放后的坐标
        image_width = self.window_width // 2
        scale_x = self.original_image.shape[1] / image_width
        scale_y = self.original_image.shape[0] / self.window_height

        # 将坐标转换回图像上的实际坐标
        x1 = int(x1 * scale_x)
        y1 = int(y1 * scale_y)
        x2 = int(x2 * scale_x)
        y2 = int(y2 * scale_y)

        roi = self.processed_image[y1:y2, x1:x2]
        blurred_roi = cv2.GaussianBlur(roi, (15, 15), 0)

        # 保存历史状态
        self.history.append(self.processed_image.copy())

        # 应用模糊效果
        self.processed_image[y1:y2, x1:x2] = blurred_roi
        self.display_images()  # 实时显示打码效果

    def undo(self):
        if self.history:
            self.processed_image = self.history.pop()
            self.display_images()
        else:
            messagebox.showwarning("警告", "没有可以撤销的操作")

    def finish(self):
        # 获取处理后的图像
        processed_image = self.processed_image

        # 使用 cv2.imencode 将图像编码为 PNG 格式
        _, img_encoded = cv2.imencode('.png', processed_image)

        # 使用 BytesIO 来处理二进制流
        self.img_bytes = BytesIO(img_encoded)

        # 关闭Tkinter窗口
        self.root.destroy()

def open_editor_mosaic():
    global editor
    root = tk.Tk()
    editor = ImageMosaicEditor(root)
    root.mainloop()  # 阻塞，直到 Tkinter 编辑器关闭

# 处理图像
def process_image_ani(img, x32=True):
    h, w = img.shape[:2]
    if x32:  # 调整为32的倍数
        def to_32s(x):
            return 256 if x < 256 else x - x % 32
        img = cv2.resize(img, (to_32s(w), to_32s(h)))
    # 转换为 RGB 格式，并归一化到 [-1, 1]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 127.5 - 1.0
    return img

# 加载测试数据
def load_test_data_ani(image_path):
    img0 = cv2.imread(image_path).astype(np.float32)
    img = process_image_ani(img0)  # 处理图像
    img = np.expand_dims(img, axis=0)  # 增加 batch 维度
    return img, img0.shape[:2]  # 返回原始图像尺寸以便恢复

# 使用模型进行转换
def Convert_ani(img, scale,session):
    x = session.get_inputs()[0].name
    y = session.get_outputs()[0].name
    # 使用 ONNX 模型进行推理
    fake_img = session.run([y], {x: img})[0]
    # 反归一化并恢复为原始尺寸
    images = (np.squeeze(fake_img) + 1.) / 2 * 255
    images = np.clip(images, 0, 255).astype(np.uint8)
    # 恢复为原始图像大小
    output_image = cv2.resize(images, (scale[1], scale[0]))
    return cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR)  # 转回 BGR 格式


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
        cv2.imwrite('input_image.jpg', image)

        # 启动 Tkinter 编辑器的线程
        thread = Thread(target=open_editor_mosaic)
        thread.start()
        thread.join()  # 等待编辑器关闭
        
        # 检查编辑器是否成功返回图像
        if editor and editor.img_bytes:
            # 返回处理后的图像
            return send_file(editor.img_bytes, mimetype='image/png')
        else:
            return "No image processed", 400


        '''
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
    
        '''
    if function_id == 3:  # 证件照制作
        background_color = request.form.get('background_color')
        photo_size = request.form.get('photo_size')
        width, height = map(int, photo_size.split('x'))
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        #读取输入图像的尺寸
        image_height, image_width = image.shape[:2]
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
        
        # 设置背景颜色
        if background_color == 'white':
            bg_color = (255, 255, 255)
        elif background_color == 'red':
            bg_color = (0, 0, 255)
        elif background_color == 'blue':
            bg_color = (255, 0, 0)
        else:
            return 'Invalid background color', 400
        # 按照要求的背景颜色(红白蓝)生成背景图
        if background_color == 'red':
            white_background = np.ones_like(readytomatting) * 255
            white_background[:, :, 0] = 0
            white_background[:, :, 1] = 0
        elif background_color == 'white':
            white_background = np.ones_like(readytomatting) * 255
        elif background_color == 'blue':
            white_background = np.ones_like(readytomatting) * 255
            white_background[:, :, 1] = 0
            white_background[:, :, 2] = 0
        else:
            return 'Invalid background color', 400
        

        # 增加alpha通道维度
        matte = np.expand_dims(matte, axis=-1)

        # 合成前景和白色背景
        foreground = readytomatting * matte + white_background * (1 - matte)
        foreground=cv2.resize(foreground,(image_width, image_height))
        #调整为证件照大小
        foreground=foreground.astype(np.uint8)
        
        # 获取原始图像的宽高比
        (h, w) = foreground.shape[:2]
        aspect_ratio = w / h

        # 根据目标尺寸计算新的尺寸，保持宽高比
        if width / height > aspect_ratio:
            new_height = height
            new_width = int(height * aspect_ratio)
        else:
            new_width = width
            new_height = int(width / aspect_ratio)

        # 调整尺寸但保持宽高比
        resized_foreground = cv2.resize(foreground, (new_width, new_height))

        
        if new_width == width:
            top=height-new_height
            final_image = cv2.copyMakeBorder(resized_foreground, top, 0, 0, 0, cv2.BORDER_CONSTANT, value=bg_color)
        else:
            left = (width - new_width) // 2
            right = width - new_width - left
            final_image = cv2.copyMakeBorder(resized_foreground, 0, 0, left, right, cv2.BORDER_CONSTANT, value=bg_color)

        if background_color =='white':
            gray = cv2.cvtColor(final_image, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                y = min(contours[0].reshape(-1, 2)[:, 1])
                final_image = final_image[:y, :]
            top = height - final_image.shape[0]
            final_image = cv2.copyMakeBorder(final_image, top, 0, 0, 0, cv2.BORDER_CONSTANT, value=bg_color)
                
        if background_color =='red':
            #去除下方的红色背景
            #转换为HSV颜色空间
            hsv = cv2.cvtColor(final_image, cv2.COLOR_BGR2HSV)
            #提取红色区域
            lower_red = np.array([0, 43, 46])
            upper_red = np.array([10, 255, 255])
            mask1 = cv2.inRange(hsv, lower_red, upper_red)
            lower_red = np.array([156, 43, 46])
            upper_red = np.array([180, 255, 255])
            mask2 = cv2.inRange(hsv, lower_red, upper_red)
            mask = mask1 + mask2
            #腐蚀膨胀
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            #找到红色区域的轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                y = min(contours[0].reshape(-1, 2)[:, 1])
                final_image = final_image[:y, :]
                
            # 确保裁剪后的图像高度不超过目标高度
            if final_image.shape[0] > height:
                final_image = final_image[:height, :]
            
            top = height - final_image.shape[0]
            final_image = cv2.copyMakeBorder(final_image, top, 0, 0, 0, cv2.BORDER_CONSTANT, value=bg_color)

        
        if background_color =='blue':
            #去除下方的蓝色背景
            #转换为HSV颜色空间
            hsv = cv2.cvtColor(final_image, cv2.COLOR_BGR2HSV)
            #提取蓝色区域
            lower_blue = np.array([100, 43, 46])
            upper_blue = np.array([124, 255, 255])
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            #腐蚀膨胀
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            #找到蓝色区域的轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                y = min(contours[0].reshape(-1, 2)[:, 1])
                final_image = final_image[:y, :]
            
            # 确保裁剪后的图像高度不超过目标高度
            if final_image.shape[0] > height:
                final_image = final_image[:height, :]
            
            top = height - final_image.shape[0]
            final_image = cv2.copyMakeBorder(final_image, top, 0, 0, 0, cv2.BORDER_CONSTANT, value=bg_color)
            
        
        
            
        '''
        final_image = cv2.resize(foreground, (height,width))
        
        #判断下方是否有白边,如果有,找到白边的最高位置,然后裁剪
        gray = cv2.cvtColor(final_image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            y = min(contours[0].reshape(-1, 2)[:, 1])
            final_image = final_image[:y, :]
            
        
        #在图片的上方增加白边,使得图片为证件照大小
        top = height - final_image.shape[0]
        final_image = cv2.copyMakeBorder(final_image, top, 0, 0, 0, cv2.BORDER_CONSTANT, value=bg_color)
        
        #上下拉伸图片,使得图片为证件照大小
        #final_image = cv2.resize(final_image, (height, width))
        '''
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
        
    if function_id == 5:  # 图像卡通化功能
        session = ort.InferenceSession('Shinkai_53.onnx')
        
        #保存图片
        cv2.imwrite('input_image.jpg', image)

        # 加载和预处理输入图像
        img, scale = load_test_data_ani('input_image.jpg')
        
        
        # 进行动漫风格转换
        anime_img = Convert_ani(img, scale,session)
        
        # Return processed image
        _, img_encoded = cv2.imencode('.png', anime_img)
        #删除图片
        os.remove('input_image.jpg')
        return send_file(BytesIO(img_encoded), mimetype='image/png') 
        # 显示结果
        cv2.imshow("Anime Style Image", anime_img)
        cv2.imwrite("output_anime_image.jpg", anime_img)

        cv2.waitKey(0)
        cv2.destroyAllWindows()


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


    if function_id == 8:  
        def CrossPoint(line1, line2): 
            x0, y0, x1, y1 = line1[0]
            x2, y2, x3, y3 = line2[0]

            dx1 = x1 - x0
            dy1 = y1 - y0

            dx2 = x3 - x2
            dy2 = y3 - y2
            
            D1 = x1 * y0 - x0 * y1
            D2 = x3 * y2 - x2 * y3

            y = float(dy1 * D2 - D1 * dy2) / (dy1 * dx2 - dx1 * dy2)
            x = float(y * dx1 - D1) / dy1

            return (int(x), int(y))

        def SortPoint(points):
            sp = sorted(points, key = lambda x:(int(x[1]), int(x[0])))
            if sp[0][0] > sp[1][0]:
                sp[0], sp[1] = sp[1], sp[0]
            
            if sp[2][0] > sp[3][0]:
                sp[2], sp[3] = sp[3], sp[2]
            
            return sp

        def imgcorr(src):
            rgbsrc = src.copy()
            graysrc = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            blurimg = cv2.GaussianBlur(src, (3, 3), 0)
            Cannyimg = cv2.Canny(blurimg, 35, 189)

            lines = cv2.HoughLinesP(Cannyimg, 1, np.pi / 180, threshold = 30, minLineLength = 320, maxLineGap = 40)
        
            for i in range(int(np.size(lines)/4)):
                for x1, y1, x2, y2 in lines[i]:
                    cv2.line(rgbsrc, (x1, y1), (x2, y2), (255, 255, 0), 3)
            
            points = np.zeros((4, 2), dtype = "float32")
            points[0] = CrossPoint(lines[0], lines[2])
            points[1] = CrossPoint(lines[0], lines[3])
            points[2] = CrossPoint(lines[1], lines[2])
            points[3] = CrossPoint(lines[1], lines[3])
            
            sp = SortPoint(points)

            width = int(np.sqrt(((sp[0][0] - sp[1][0]) ** 2) + (sp[0][1] - sp[1][1]) ** 2))
            height = int(np.sqrt(((sp[0][0] - sp[2][0]) ** 2) + (sp[0][1] - sp[2][1]) ** 2))

            dstrect = np.array([
                [0, 0],
                [width - 1, 0],
                [0, height - 1],
                [width - 1, height - 1]], dtype = "float32")
        
            transform = cv2.getPerspectiveTransform(np.array(sp), dstrect)
            warpedimg = cv2.warpPerspective(src, transform, (width, height))

            return warpedimg
        dst = imgcorr(image)
        
        _, img_encoded = cv2.imencode('.png', dst)
        return send_file(BytesIO(img_encoded), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

