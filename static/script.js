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
