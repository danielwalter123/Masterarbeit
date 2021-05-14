const { createScheduler, createWorker, PSM } = Tesseract;

const scheduler = createScheduler();

window.onload = async function() {
  const filterBar = document.getElementById('filter');
  for (let i = 0; i < 4; i++) {
    const workerProgress = document.createElement('div');
    filterBar.appendChild(workerProgress);
    
    const worker = createWorker({
      logger: m => {
        console.log(m);
        workerProgress.innerHTML = Math.floor(m.progress * 100) + '%';
      }
    });
    await worker.load();
    await worker.loadLanguage('eng+deu');
    await worker.initialize('eng+deu');
    //await worker.setParameters({
    //  tessedit_pageseg_mode: PSM.SPARSE_TEXT
    //});
    scheduler.addWorker(worker);
  }

  console.log("Initialization done");
  
  const scanButtons = document.getElementById('screenshots').querySelectorAll('button');
  for (let button of scanButtons) {
    button.disabled = false;
  }
  
};

function scanAll () {
  const buttons = document.getElementById('screenshots').querySelectorAll('button');
  for (let button of buttons) {
    if (button.id && !button.disabled) {
      button.click();
    }
  }
}

function scan (id) {

  
  const img = document.getElementById('img' + id);
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  
  document.getElementById('result' + id).prepend(canvas);
  
  const doUpscaling = document.getElementById('upscaling').checked
  const doBilateralFilter = document.getElementById('bilateral-filter').checked
  const doThreshold = document.getElementById('threshold').checked

  const doOCR = document.getElementById('ocr').checked

  // OpenCV preprocessing
  let src = cv.imread(img);
  
  if (doUpscaling) {
    const scaleFactor = Number(document.getElementById('upscaling-factor').value);
    const dst = new cv.Mat();
    cv.resize(src, dst, new cv.Size(0, 0), scaleFactor, scaleFactor);
    src.delete();
    src = dst;
  }
  
  if (doBilateralFilter) {
    const d = Number(document.getElementById('bilateral-filter-d').value);
    const sigmaColor = Number(document.getElementById('bilateral-filter-sigma-color').value);
    const sigmaSpace = Number(document.getElementById('bilateral-filter-sigma-space').value);
    const dst = new cv.Mat();
    cv.cvtColor(src, src, cv.COLOR_RGBA2RGB, 0);
    cv.bilateralFilter(src, dst, d, sigmaColor, sigmaSpace, cv.BORDER_DEFAULT);
    src.delete();
    src = dst;
  }

  if (doThreshold) {
    const blockSize = Number(document.getElementById('threshold-blocksize').value);
    const c = Number(document.getElementById('threshold-c').value);
    const dst = new cv.Mat();
    cv.cvtColor(src, src, cv.COLOR_RGBA2GRAY, 0);
    cv.adaptiveThreshold(src, dst, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, blockSize, c);
    src.delete();
    src = dst;
  }
  cv.imshow(canvas, src);
  src.delete();
  
  if (!doOCR) return;

  const button = document.getElementById('button' + id);
  button.disabled = true;
  button.style.background = 'red';
  button.style.color = 'white';
  
  scheduler.addJob('recognize', canvas).then(result => {
    console.log(result);
    context.strokeStyle = 'red';
    for (let word of result.data.words) {
      context.strokeStyle = 'red';
      context.fillStyle = 'white';
      context.beginPath();
      context.rect(word.bbox.x0, word.bbox.y0, word.bbox.x1 - word.bbox.x0, word.bbox.y1 - word.bbox.y0);
      context.fill();
      context.stroke();
      
      context.fillStyle = 'black';
      context.font = '12px Arial';
      context.textAlign = "center";
      context.fillText(word.text, (word.bbox.x0 + word.bbox.x1) / 2, (word.bbox.y0 + word.bbox.y1) / 2 + 6);
    }
    button.disabled = false;
    button.style.background = '';
    button.style.color = '';
  });
  
}