// JavaScript代码，处理图像上传
function uploadImage(pageNumber) {
    const fileInput = document.getElementById(`upload-image-${pageNumber}`);
    const file = fileInput.files[0];
    if (!file) {
        alert("请先选择一张图片。");
        return;
    }

    const formData = new FormData();
    formData.append('image', file);
    formData.append('function_id', pageNumber);

    // 对于图像分割功能，传递阈值
    if (pageNumber === 2) {
        const threshold = document.getElementById('threshold-value').value;
        formData.append('threshold', threshold);
    }
    //对于证件照功能，传递背景颜色和照片尺寸
    if (pageNumber === 3) {
        const backgroundColor = document.getElementById('background-color-3').value;
        const photoSize = document.getElementById('photo-size-3').value;
        formData.append('background_color', backgroundColor);
        formData.append('photo_size', photoSize);
    }

    //对于图像旋转功能,传递角度
    if (pageNumber === 6) {
        const angle = document.getElementById('angle-value').value;
        formData.append('angle', angle);
    }
    //对于图像翻转功能,传递翻转方向
    if (pageNumber === 7) {
        const flipDirection = document.getElementById('flip-direction').value;
        formData.append('flip_direction', flipDirection);
    }

    const uploadedImageUrl = URL.createObjectURL(file);   // 本地预览
    const uploadedImage = document.getElementById(`uploaded-image-${pageNumber}`);  // 显示上传的图像
    uploadedImage.src = uploadedImageUrl;  // 显示上传的图像
    uploadedImage.style.display = 'block';  // 显示上传的图像

    fetch('/process_image', {
        method: 'POST',
        body: formData
    })        //// 向服务器发送图像
    .then(response => response.blob())
    .then(blob => {
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById(`processed-image-${pageNumber}`).src = imageUrl;
    })
    .catch(error => {
        console.error('错误:', error);
    });
}  // uploadImage

function showSubPage(pageNumber) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.style.display = 'none');
    document.getElementById(`sub-page-${pageNumber}`).style.display = 'block';
    const buttons = document.querySelectorAll('.toolbar button');
    buttons.forEach(button => button.classList.remove('active'));
    document.getElementById(`btn-${pageNumber}`).classList.add('active');
}  // showSubPage

function downloadImage(pageNumber) {
    const image = document.getElementById(`processed-image-${pageNumber}`);
    const url = image.src;
    
    // 检查是否是图片资源
   // if (url.endsWith('.jpg') || url.endsWith('.jpeg') || url.endsWith('.png')) {
        const link = document.createElement('a');
        link.href = url;
        link.download = 'image.jpg';  // 设置合适的扩展名
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    //} else {
     //   console.error('URL does not point to a valid image file.');
   // }
}



function uploadImagesForBackgroundReplacement(pageNumber) {
    const foregroundInput = document.getElementById(`upload-foreground-${pageNumber}`);
    const backgroundInput = document.getElementById(`upload-background-${pageNumber}`);
    
    const foregroundFile = foregroundInput.files[0];
    const backgroundFile = backgroundInput.files[0];

    if (!foregroundFile || !backgroundFile) {
        alert("请同时选择前景和背景图片。");
        return;
    }

    const formData = new FormData();
    formData.append('foreground', foregroundFile);
    formData.append('background', backgroundFile);
    formData.append('function_id', pageNumber);
    formData.append('image', foregroundFile);

    // Preview the uploaded images
    const uploadedForegroundUrl = URL.createObjectURL(foregroundFile);
    const uploadedForeground = document.getElementById(`uploaded-foreground-${pageNumber}`);
    uploadedForeground.src = uploadedForegroundUrl;
    uploadedForeground.style.display = 'block';

    console.log(foregroundFile);
    console.log(backgroundFile);

    fetch('/process_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById(`processed-image-${pageNumber}`).src = imageUrl;
    })
    .catch(error => {
        console.error('错误:', error);
    });
}
// Function to open the camera dialog when "拍照" is pressed
function openCameraDialog(pageNumber) {
    const modal = document.getElementById('cameraModal');  // 获取自定义弹窗
    const modalVideo = document.getElementById('modalVideo');  // 获取video元素
    const takePhotoButton = document.getElementById('takePhotoButton');  // 获取拍照按钮
    const closeModalButton = document.getElementById('closeModal');  // 获取关闭按钮
    const uploadedImage = document.getElementById(`uploaded-image-${pageNumber}`);  // 获取展示拍摄图片的位置
    const cancelPhotoButton = document.getElementById('cancelPhotoButton');  // 获取取消按钮
    let stream;  // 用于保存摄像头流

    // 摄像头流设置
    const constraints = {
        video: {
            width: 640,
            height: 480
        }
    };

    // 打开弹窗并初始化摄像头
    async function initCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia(constraints);  // 请求访问摄像头
            modalVideo.srcObject = stream;  // 将摄像头流赋给video元素
            modal.style.display = 'block';  // 显示弹窗
        } catch (e) {
            console.error('Error accessing camera:', e);
        }
    }

    // 拍照并显示图片
    takePhotoButton.onclick = function () {
        const canvas = document.createElement('canvas');
        canvas.width = 640;
        canvas.height = 480;
        const context = canvas.getContext('2d');
        context.drawImage(modalVideo, 0, 0, canvas.width, canvas.height);  // 将视频流绘制到画布上
        const imageDataURL = canvas.toDataURL('image/jpeg');  // 获取图片的base64数据
        uploadedImage.src = imageDataURL;  // 显示拍摄的图片
        uploadedImage.style.display = 'block';

        //将canvas转换为图片文件
        canvas.toBlob(function (blob) {
            const file = new File([blob], 'image.jpg', { type: 'image/jpeg' });
            const formData = new FormData();
            formData.append('image', file);
            formData.append('function_id', pageNumber);

            fetch('/process_image', {
                method: 'POST',
                body: formData
            })
            .then(response => response.blob())
            .then(blob => {
                const imageUrl = URL.createObjectURL(blob);
                document.getElementById(`processed-image-${pageNumber}`).src = imageUrl;
            })
            .catch(error => {
                console.error('上传错误:', error);
            });
        });

        // 关闭弹窗并停止摄像头
        closeModal();
    };

    // 关闭弹窗并停止摄像头流
    function closeModal() {
        modal.style.display = 'none';
        if (stream) {
            stream.getTracks().forEach(track => track.stop());  // 停止摄像头流
        }
    }

    // 点击关闭按钮时关闭弹窗
    closeModalButton.onclick = closeModal;

    cancelPhotoButton.onclick = closeModal;

    // 初始化摄像头
    initCamera();
}
