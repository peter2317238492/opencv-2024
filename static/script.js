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