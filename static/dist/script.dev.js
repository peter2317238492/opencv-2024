"use strict";

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance"); }

function _iterableToArray(iter) { if (Symbol.iterator in Object(iter) || Object.prototype.toString.call(iter) === "[object Arguments]") return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = new Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } }

// JavaScript代码，处理图像上传
function uploadImage(pageNumber) {
  var fileInput = document.getElementById("upload-image-".concat(pageNumber));
  var file = fileInput.files[0];

  if (!file) {
    alert("请先选择一张图片。");
    return;
  }

  var formData = new FormData();
  formData.append('image', file);
  formData.append('function_id', pageNumber); // 对于图像分割功能，传递阈值

  if (pageNumber === 2) {
    var threshold = document.getElementById('threshold-value').value;
    formData.append('threshold', threshold);
  } //对于证件照功能，传递背景颜色和照片尺寸


  if (pageNumber === 3) {
    var backgroundColor = document.getElementById('background-color-3').value;
    var photoSize = document.getElementById('photo-size-3').value;
    formData.append('background_color', backgroundColor);
    formData.append('photo_size', photoSize);
  } //对于图像旋转功能,传递角度


  if (pageNumber === 6) {
    var angle = document.getElementById('angle-value').value;
    formData.append('angle', angle);
  } //对于图像翻转功能,传递翻转方向


  if (pageNumber === 7) {
    var flipDirection = document.getElementById('flip-direction').value;
    formData.append('flip_direction', flipDirection);
  }

  var uploadedImageUrl = URL.createObjectURL(file); // 本地预览

  var uploadedImage = document.getElementById("uploaded-image-".concat(pageNumber)); // 显示上传的图像

  uploadedImage.src = uploadedImageUrl; // 显示上传的图像

  uploadedImage.style.display = 'block'; // 显示上传的图像

  fetch('/process_image', {
    method: 'POST',
    body: formData
  }) //// 向服务器发送图像
  .then(function (response) {
    return response.blob();
  }).then(function (blob) {
    var imageUrl = URL.createObjectURL(blob);
    document.getElementById("processed-image-".concat(pageNumber)).src = imageUrl;
  })["catch"](function (error) {
    console.error('错误:', error);
  });
} // uploadImage


function showSubPage(pageNumber) {
  var pages = document.querySelectorAll('.page');
  pages.forEach(function (page) {
    return page.style.display = 'none';
  });
  document.getElementById("sub-page-".concat(pageNumber)).style.display = 'block';
  var buttons = document.querySelectorAll('.toolbar button');
  buttons.forEach(function (button) {
    return button.classList.remove('active');
  });
  document.getElementById("btn-".concat(pageNumber)).classList.add('active');
} // showSubPage


function downloadImage(pageNumber) {
  var image = document.getElementById("processed-image-".concat(pageNumber));
  var url = image.src; // 检查是否是图片资源
  // if (url.endsWith('.jpg') || url.endsWith('.jpeg') || url.endsWith('.png')) {

  var link = document.createElement('a');
  link.href = url;
  link.download = 'image.jpg'; // 设置合适的扩展名

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link); //} else {
  //   console.error('URL does not point to a valid image file.');
  // }
}

function uploadImagesForBackgroundReplacement(pageNumber) {
  var foregroundInput = document.getElementById("upload-foreground-".concat(pageNumber));
  var backgroundInput = document.getElementById("upload-background-".concat(pageNumber));
  var foregroundFile = foregroundInput.files[0];
  var backgroundFile = backgroundInput.files[0];

  if (!foregroundFile || !backgroundFile) {
    alert("请同时选择前景和背景图片。");
    return;
  }

  var formData = new FormData();
  formData.append('foreground', foregroundFile);
  formData.append('background', backgroundFile);
  formData.append('function_id', pageNumber);
  formData.append('image', foregroundFile); // Preview the uploaded images

  var uploadedForegroundUrl = URL.createObjectURL(foregroundFile);
  var uploadedForeground = document.getElementById("uploaded-foreground-".concat(pageNumber));
  uploadedForeground.src = uploadedForegroundUrl;
  uploadedForeground.style.display = 'block';
  console.log(foregroundFile);
  console.log(backgroundFile);
  fetch('/process_image', {
    method: 'POST',
    body: formData
  }).then(function (response) {
    return response.blob();
  }).then(function (blob) {
    var imageUrl = URL.createObjectURL(blob);
    document.getElementById("processed-image-".concat(pageNumber)).src = imageUrl;
  })["catch"](function (error) {
    console.error('错误:', error);
  });
} // Function to open the camera dialog when "拍照" is pressed


function openCameraDialog(pageNumber) {
  var modal = document.getElementById('cameraModal'); // 获取自定义弹窗

  var modalVideo = document.getElementById('modalVideo'); // 获取video元素

  var takePhotoButton = document.getElementById('takePhotoButton'); // 获取拍照按钮

  var closeModalButton = document.getElementById('closeModal'); // 获取关闭按钮

  var uploadedImage = document.getElementById("uploaded-image-".concat(pageNumber)); // 获取展示拍摄图片的位置

  var cancelPhotoButton = document.getElementById('cancelPhotoButton'); // 获取取消按钮

  var stream; // 用于保存摄像头流
  // 摄像头流设置

  var constraints = {
    video: {
      width: 640,
      height: 480
    }
  }; // 打开弹窗并初始化摄像头

  function initCamera() {
    return regeneratorRuntime.async(function initCamera$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            _context.prev = 0;
            _context.next = 3;
            return regeneratorRuntime.awrap(navigator.mediaDevices.getUserMedia(constraints));

          case 3:
            stream = _context.sent;
            // 请求访问摄像头
            modalVideo.srcObject = stream; // 将摄像头流赋给video元素

            modal.style.display = 'block'; // 显示弹窗

            _context.next = 11;
            break;

          case 8:
            _context.prev = 8;
            _context.t0 = _context["catch"](0);
            console.error('Error accessing camera:', _context.t0);

          case 11:
          case "end":
            return _context.stop();
        }
      }
    }, null, null, [[0, 8]]);
  } // 拍照并显示图片


  takePhotoButton.onclick = function () {
    var canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 480;
    var context = canvas.getContext('2d');
    context.drawImage(modalVideo, 0, 0, canvas.width, canvas.height); // 将视频流绘制到画布上

    var imageDataURL = canvas.toDataURL('image/jpeg'); // 获取图片的base64数据

    uploadedImage.src = imageDataURL; // 显示拍摄的图片

    uploadedImage.style.display = 'block'; //将canvas转换为图片文件

    canvas.toBlob(function (blob) {
      var file = new File([blob], 'image.jpg', {
        type: 'image/jpeg'
      });
      var formData = new FormData();
      formData.append('image', file);
      formData.append('function_id', pageNumber); // 对于图像分割功能，传递阈值

      if (pageNumber === 2) {
        var threshold = document.getElementById('threshold-value').value;
        formData.append('threshold', threshold);
      } //对于证件照功能，传递背景颜色和照片尺寸


      if (pageNumber === 3) {
        var backgroundColor = document.getElementById('background-color-3').value;
        var photoSize = document.getElementById('photo-size-3').value;
        formData.append('background_color', backgroundColor);
        formData.append('photo_size', photoSize);
      } //对于图像旋转功能,传递角度


      if (pageNumber === 6) {
        var angle = document.getElementById('angle-value').value;
        formData.append('angle', angle);
      } //对于图像翻转功能,传递翻转方向


      if (pageNumber === 7) {
        var flipDirection = document.getElementById('flip-direction').value;
        formData.append('flip_direction', flipDirection);
      }

      fetch('/process_image', {
        method: 'POST',
        body: formData
      }).then(function (response) {
        return response.blob();
      }).then(function (blob) {
        var imageUrl = URL.createObjectURL(blob);
        document.getElementById("processed-image-".concat(pageNumber)).src = imageUrl;
      })["catch"](function (error) {
        console.error('上传错误:', error);
      });
    }); // 关闭弹窗并停止摄像头

    closeModal();
  }; // 关闭弹窗并停止摄像头流


  function closeModal() {
    modal.style.display = 'none';

    if (stream) {
      stream.getTracks().forEach(function (track) {
        return track.stop();
      }); // 停止摄像头流
    }
  } // 点击关闭按钮时关闭弹窗


  closeModalButton.onclick = closeModal;
  cancelPhotoButton.onclick = closeModal; // 初始化摄像头

  initCamera();
}

var startX, startY, endX, endY;
startX, startY, endX, endY = 0;
var cropping = false;
var uploadedImage = document.getElementById('uploaded-image-9');
var cropDialog = document.getElementById('crop-dialog');
var cropImage = document.getElementById('crop-image');
var selectionBox = document.getElementById('selection-box');
var scaleX, scaleY; // 用于计算实际的图像缩放比例

function openCropDialog() {
  var imageSrc = uploadedImage.src;

  if (!imageSrc) {
    alert('请先上传图片！');
    return;
  }

  cropImage.src = imageSrc; // 使用上传的图片作为裁剪对象

  cropDialog.style.display = 'block'; // 显示裁剪弹出框

  cropImage.onload = function () {
    // 计算缩放比例
    var naturalWidth = cropImage.naturalWidth;
    var naturalHeight = cropImage.naturalHeight;
    var displayWidth = cropImage.clientWidth;
    var displayHeight = cropImage.clientHeight;
    scaleX = naturalWidth / displayWidth;
    scaleY = naturalHeight / displayHeight; // 开始裁剪逻辑

    startCrop();
  };
}

function closeCropDialog() {
  cropDialog.style.display = 'none';
}

function startCrop() {
  selectionBox.style.display = 'none'; // 重置裁剪框

  cropImage.addEventListener('click', startSelection, {
    once: true
  });
  document.addEventListener('click', resizeSelection);
  document.addEventListener('mouseup', endSelection);
}

function startSelection(event) {
  cropping = true; // 标记为正在裁剪

  var rect = cropImage.getBoundingClientRect();
  startX = event.clientX - rect.left;
  startY = event.clientY - rect.top; // 显示裁剪框

  selectionBox.style.left = startX + 'px';
  selectionBox.style.top = startY + 'px';
  selectionBox.style.width = '0px';
  selectionBox.style.height = '0px';
  selectionBox.style.display = 'block';
  console.log('Start X:', startX, 'Start Y:', startY);
  console.log('End X:', endX, 'End Y:', endY);
}

function resizeSelection(event) {
  if (!cropping) return; // 如果未按下鼠标，则不进行裁剪

  var rect = cropImage.getBoundingClientRect();
  endX = event.clientX - rect.left;
  endY = event.clientY - rect.top; // 仅当鼠标按下时，更新裁剪框大小

  selectionBox.style.width = Math.abs(endX - startX) + 'px';
  selectionBox.style.height = Math.abs(endY - startY) + 'px';
  selectionBox.style.left = Math.min(startX, endX) + 'px';
  selectionBox.style.top = Math.min(startY, endY) + 'px';
  console.log('Start X:', startX, 'Start Y:', startY);
  console.log('End X:', endX, 'End Y:', endY);
}

function endSelection() {
  cropping = false; // 结束裁剪
  // 移除事件监听

  document.removeEventListener('mousemove', resizeSelection);
  document.removeEventListener('mouseup', endSelection);
}

function performCrop() {
  if (isNaN(startX) || isNaN(startY) || isNaN(endX) || isNaN(endY)) {
    alert('裁剪坐标无效，请重新选择裁剪区域！');
    return;
  } // 获取裁剪坐标并转换为原始图像坐标


  var x_start = Math.min(startX, endX) * scaleX;
  var y_start = Math.min(startY, endY) * scaleY;
  var x_end = Math.max(startX, endX) * scaleX;
  var y_end = Math.max(startY, endY) * scaleY;
  var formData = new FormData();
  formData.append('function_id', '9');
  formData.append('x_start', x_start);
  formData.append('y_start', y_start);
  formData.append('x_end', x_end);
  formData.append('y_end', y_end);
  var imageFile = document.getElementById('upload-image-9').files[0];

  if (imageFile) {
    formData.append('image', imageFile);
  }

  fetch('/process_image', {
    method: 'POST',
    body: formData
  }).then(function (response) {
    return response.blob();
  }).then(function (blob) {
    var url = URL.createObjectURL(blob);
    document.getElementById('processed-image-9').src = url;
    closeCropDialog(); // 关闭裁剪对话框
    //显示裁剪后的图片

    var processedImage = document.getElementById('processed-image-9');
    processedImage.style.display = 'block';
  })["catch"](function (error) {
    console.error('Error:', error);
  });
} ////////


function adjustImage() {
  var contrast = document.getElementById('contrast-slider').value;
  var brightness = document.getElementById('brightness-slider').value;
  var gamma = document.getElementById('gamma-slider').value;
  var formData = new FormData();
  var fileInput = document.getElementById('upload-image-10');
  var file = fileInput.files[0];
  formData.append('image', file);
  formData.append('contrast', contrast);
  formData.append('brightness', brightness);
  formData.append('gamma', gamma);
  fetch('/adjust_image', {
    method: 'POST',
    body: formData
  }).then(function (response) {
    return response.blob();
  }).then(function (blob) {
    var imageUrl = URL.createObjectURL(blob);
    var processedImageElement = document.getElementById('processed-image-10');
    processedImageElement.src = imageUrl; // Once the image is loaded, draw the histogram

    processedImageElement.onload = function () {
      drawHistogram(processedImageElement);
    };
  })["catch"](function (error) {
    console.error('Error:', error);
  });
}

function drawHistogram(imageElement) {
  var canvas = document.getElementById('histogram');
  var ctx = canvas.getContext('2d');
  var image = new Image();
  image.src = imageElement.src;

  image.onload = function () {
    // Draw the image on a hidden canvas to get pixel data
    var tempCanvas = document.createElement('canvas');
    var tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = image.width;
    tempCanvas.height = image.height;
    tempCtx.drawImage(image, 0, 0); // Get the image data

    var imageData = tempCtx.getImageData(0, 0, image.width, image.height);
    var data = imageData.data; // Initialize histograms for red, green, and blue channels

    var redHistogram = new Array(256).fill(0);
    var greenHistogram = new Array(256).fill(0);
    var blueHistogram = new Array(256).fill(0); // Calculate histograms

    for (var i = 0; i < data.length; i += 4) {
      redHistogram[data[i]]++;
      greenHistogram[data[i + 1]]++;
      blueHistogram[data[i + 2]]++;
    } // Find the maximum value for normalization


    var maxRed = Math.max.apply(Math, _toConsumableArray(redHistogram));
    var maxGreen = Math.max.apply(Math, _toConsumableArray(greenHistogram));
    var maxBlue = Math.max.apply(Math, _toConsumableArray(blueHistogram));
    var max = Math.max(maxRed, maxGreen, maxBlue); // Clear the canvas before drawing histograms

    ctx.clearRect(0, 0, canvas.width, canvas.height); // Set bar width

    var barWidth = 2; // Draw the red, green, and blue histograms with transparency

    for (var _i = 0; _i < 256; _i++) {
      var redHeight = redHistogram[_i] / max * canvas.height;
      var greenHeight = greenHistogram[_i] / max * canvas.height;
      var blueHeight = blueHistogram[_i] / max * canvas.height; // Red channel

      ctx.fillStyle = 'rgba(255, 0, 0, 0.6)';
      ctx.fillRect(_i * barWidth, canvas.height - redHeight, barWidth, redHeight); // Green channel

      ctx.fillStyle = 'rgba(0, 255, 0, 0.6)';
      ctx.fillRect(_i * barWidth, canvas.height - greenHeight, barWidth, greenHeight); // Blue channel

      ctx.fillStyle = 'rgba(0, 0, 255, 0.6)';
      ctx.fillRect(_i * barWidth, canvas.height - blueHeight, barWidth, blueHeight);
    } // Optionally add a border around the histogram


    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 1;
    ctx.strokeRect(0, 0, canvas.width, canvas.height);
  };
}

function autoAdjust() {
  var fileInput = document.getElementById('upload-image-10');
  var file = fileInput.files[0];

  if (!file) {
    alert("请先上传一张图片");
    return;
  }

  var formData = new FormData();
  formData.append('image', file);
  fetch('/auto_adjust', {
    method: 'POST',
    body: formData
  }).then(function (response) {
    return response.blob();
  }).then(function (blob) {
    var imageUrl = URL.createObjectURL(blob);
    document.getElementById('processed-image-10').src = imageUrl;
  })["catch"](function (error) {
    console.error('Error:', error);
  });
}

function undoAdjust() {
  var fileInput = document.getElementById('upload-image-10');
  var file = fileInput.files[0];

  if (!file) {
    alert("请先上传一张图片");
    return;
  }

  var formData = new FormData();
  formData.append('image', file);
  fetch('/undo_adjust', {
    method: 'POST',
    body: formData
  }).then(function (response) {
    return response.blob();
  }).then(function (blob) {
    var imageUrl = URL.createObjectURL(blob);
    document.getElementById('processed-image-10').src = imageUrl;
  })["catch"](function (error) {
    console.error('Error:', error);
  });
}