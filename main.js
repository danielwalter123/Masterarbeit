const { createScheduler, createWorker, PSM } = Tesseract;


async function selectVideoSource () {
  const stream = await navigator.mediaDevices.getDisplayMedia({
    video: { mediaSource: "screen", video: true }
  });
  
  const video = document.getElementById('video');
  video.srcObject = stream;
}


window.onload = function() {
  const video = document.getElementById('video');
  const canvas = document.getElementById('output');
  const context = canvas.getContext('2d');
  const scheduler = createScheduler();
  
  (async () => {
    for (let i = 0; i < 4; i++) {
      const worker = createWorker({
        logger: m => console.log(m)
      });
      await worker.load();
      await worker.loadLanguage('eng+deu');
      await worker.initialize('eng+deu');
      await worker.setParameters({
        tessedit_pageseg_mode: PSM.SPARSE_TEXT
      });
      scheduler.addWorker(worker);
    }
  })();

  
  document.getElementById('start').onclick = function () {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
    
    /*
    var processedImageData = context.getImageData(0, 0, canvas.width, canvas.height);
    invertColors(processedImageData.data);
    context.putImageData(processedImageData, 0, 0);
    */
    
    (async () => {
      
      let { data: { words } } = await scheduler.addJob('recognize', canvas);
      words = words.filter(word => word.confidence > 40 && word.text.length > 1)
      console.log(words);
      
      context.strokeStyle = 'red';
      
      for (let word of words) {
        context.beginPath();
        context.rect(word.bbox.x0, word.bbox.y0, word.bbox.x1 - word.bbox.x0, word.bbox.y1 - word.bbox.y0);
        context.stroke();
      }
      
    })();
    
  };
  
  /*
  canvas.width = img.width;
  canvas.height = img.height;
  context.drawImage(img, 0, 0);
  var processedImageData = context.getImageData(0, 0, img.width, img.height);
  

  //blurARGB(processedImageData.data, canvas, 0.5)
  //thresholdFilter(processedImageData.data, level=0.5);
  //dilate(processedImageData.data, canvas)
  context.putImageData(processedImageData, 0, 0);
  */
  
/*
  cv['onRuntimeInitialized'] = function () {
    let src = cv.imread(imgElement);
    let dst = new cv.Mat();
    cv.cvtColor(src, src, cv.COLOR_RGBA2GRAY, 0);
    cv.adaptiveThreshold(src, dst, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 5, 20);
    cv.imshow("output", dst);
    src.delete();
    dst.delete();
  }
  */

}

