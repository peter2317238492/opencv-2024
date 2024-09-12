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

let startX, startY, endX, endY;
let cropping = false;
const uploadedImage = document.getElementById('uploaded-image-9');
const cropDialog = document.getElementById('crop-dialog');
const cropImage = document.getElementById('crop-image');
const selectionBox = document.getElementById('selection-box');
let scaleX, scaleY;  // 用于计算实际的图像缩放比例

function openCropDialog() {
    const imageSrc = uploadedImage.src;
    if (!imageSrc) {
        alert('请先上传图片！');
        return;
    }
    
    cropImage.src = imageSrc;  // 使用上传的图片作为裁剪对象
    cropDialog.style.display = 'block';  // 显示裁剪弹出框
    
    cropImage.onload = () => {
        // 计算缩放比例
        const naturalWidth = cropImage.naturalWidth;
        const naturalHeight = cropImage.naturalHeight;
        const displayWidth = cropImage.clientWidth;
        const displayHeight = cropImage.clientHeight;

        scaleX = naturalWidth / displayWidth;
        scaleY = naturalHeight / displayHeight;

        // 开始裁剪逻辑
        startCrop(); 
    };
}

function closeCropDialog() {
    cropDialog.style.display = 'none';
}

function startCrop() {
    selectionBox.style.display = 'none';  // 重置裁剪框
    
    cropImage.addEventListener('mousedown', startSelection);
    document.addEventListener('mousemove', resizeSelection);
    document.addEventListener('mouseup', endSelection);
}

function startSelection(event) {
    cropping = true;  // 标记为正在裁剪
    const rect = cropImage.getBoundingClientRect();
    startX = event.clientX - rect.left;
    startY = event.clientY - rect.top;

    // 显示裁剪框
    selectionBox.style.left = startX + 'px';
    selectionBox.style.top = startY + 'px';
    selectionBox.style.width = '0px';
    selectionBox.style.height = '0px';
    selectionBox.style.display = 'block';
}

function resizeSelection(event) {
    if (!cropping) return;  // 如果未按下鼠标，则不进行裁剪
    
    const rect = cropImage.getBoundingClientRect();
    endX = event.clientX - rect.left;
    endY = event.clientY - rect.top;

    // 仅当鼠标按下时，更新裁剪框大小
    selectionBox.style.width = Math.abs(endX - startX) + 'px';
    selectionBox.style.height = Math.abs(endY - startY) + 'px';
    selectionBox.style.left = Math.min(startX, endX) + 'px';
    selectionBox.style.top = Math.min(startY, endY) + 'px';
}

function endSelection() {
    cropping = false;  // 结束裁剪
    // 移除事件监听
    document.removeEventListener('mousemove', resizeSelection);
    document.removeEventListener('mouseup', endSelection);
}

function performCrop() {
    // 获取裁剪坐标并转换为原始图像坐标
    const x_start = Math.min(startX, endX) * scaleX;
    const y_start = Math.min(startY, endY) * scaleY;
    const x_end = Math.max(startX, endX) * scaleX;
    const y_end = Math.max(startY, endY) * scaleY;

    const formData = new FormData();
    formData.append('function_id', '9');
    formData.append('x_start', x_start);
    formData.append('y_start', y_start);
    formData.append('x_end', x_end);
    formData.append('y_end', y_end);

    const imageFile = document.getElementById('upload-image-9').files[0];
    if (imageFile) {
        formData.append('image', imageFile);
    }

    fetch('/process_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        document.getElementById('processed-image-9').src = url;
        closeCropDialog();  // 关闭裁剪对话框
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
////////

function adjustImage() {
    const contrast = document.getElementById('contrast-slider').value;
    const brightness = document.getElementById('brightness-slider').value;
    const gamma = document.getElementById('gamma-slider').value;

    const formData = new FormData();
    const fileInput = document.getElementById('upload-image-10');
    const file = fileInput.files[0];
    formData.append('image', file);
    formData.append('contrast', contrast);
    formData.append('brightness', brightness);
    formData.append('gamma', gamma);

    fetch('/adjust_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const imageUrl = URL.createObjectURL(blob);
        const processedImageElement = document.getElementById('processed-image-10');
        processedImageElement.src = imageUrl;

        // Once the image is loaded, draw the histogram
        processedImageElement.onload = function () {
            drawHistogram(processedImageElement);
        };
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function drawHistogram(imageElement) {
    const canvas = document.getElementById('histogram');
    const ctx = canvas.getContext('2d');
    const image = new Image();
    image.src = imageElement.src;

    image.onload = function () {
        // Draw the image on a hidden canvas to get pixel data
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        tempCanvas.width = image.width;
        tempCanvas.height = image.height;
        tempCtx.drawImage(image, 0, 0);

        // Get the image data
        const imageData = tempCtx.getImageData(0, 0, image.width, image.height);
        const data = imageData.data;

        // Initialize histograms for red, green, and blue channels
        const redHistogram = new Array(256).fill(0);
        const greenHistogram = new Array(256).fill(0);
        const blueHistogram = new Array(256).fill(0);

        // Calculate histograms
        for (let i = 0; i < data.length; i += 4) {
            redHistogram[data[i]]++;
            greenHistogram[data[i + 1]]++;
            blueHistogram[data[i + 2]]++;
        }

        // Find the maximum value for normalization
        const maxRed = Math.max(...redHistogram);
        const maxGreen = Math.max(...greenHistogram);
        const maxBlue = Math.max(...blueHistogram);
        const max = Math.max(maxRed, maxGreen, maxBlue);

        // Clear the canvas before drawing histograms
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Set bar width
        const barWidth = 2;

        // Draw the red, green, and blue histograms with transparency
        for (let i = 0; i < 256; i++) {
            const redHeight = (redHistogram[i] / max) * canvas.height;
            const greenHeight = (greenHistogram[i] / max) * canvas.height;
            const blueHeight = (blueHistogram[i] / max) * canvas.height;

            // Red channel
            ctx.fillStyle = 'rgba(255, 0, 0, 0.6)';
            ctx.fillRect(i * barWidth, canvas.height - redHeight, barWidth, redHeight);

            // Green channel
            ctx.fillStyle = 'rgba(0, 255, 0, 0.6)';
            ctx.fillRect(i * barWidth, canvas.height - greenHeight, barWidth, greenHeight);

            // Blue channel
            ctx.fillStyle = 'rgba(0, 0, 255, 0.6)';
            ctx.fillRect(i * barWidth, canvas.height - blueHeight, barWidth, blueHeight);
        }

        // Optionally add a border around the histogram
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 1;
        ctx.strokeRect(0, 0, canvas.width, canvas.height);
    };
}




function autoAdjust() {
    const fileInput = document.getElementById('upload-image-10');
    const file = fileInput.files[0];

    if (!file) {
        alert("请先上传一张图片");
        return;
    }

    const formData = new FormData();
    formData.append('image', file);

    fetch('/auto_adjust', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById('processed-image-10').src = imageUrl;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function undoAdjust() {
    const fileInput = document.getElementById('upload-image-10');
    const file = fileInput.files[0];

    if (!file) {
        alert("请先上传一张图片");
        return;
    }

    const formData = new FormData();
    formData.append('image', file);

    fetch('/undo_adjust', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById('processed-image-10').src = imageUrl;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}