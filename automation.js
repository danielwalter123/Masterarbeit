const { createScheduler, createWorker, PSM } = Tesseract;

const input = document.getElementById('emulator-container').querySelector('canvas');
const output = document.getElementById('output');
const context = output.getContext('2d');
const buttonContainer = document.getElementById('button-container');


const guac = document.querySelector('eaas-environment').client.guac;
const emulatorContainer = document.getElementById('emulator-container');


const scheduler = createScheduler();

(async () => {
  for (let i = 0; i < 1; i++) {
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
  console.log("Initialization done")
})();


// from https://github.com/processing/p5.js/blob/main/src/image/filters.js
function thresholdFilter(pixels, level) {
  if (level === undefined) {
    level = 0.5;
  }
  const thresh = Math.floor(level * 255);
  for (let i = 0; i < pixels.length; i += 4) {
    const r = pixels[i];
    const g = pixels[i + 1];
    const b = pixels[i + 2];
    const gray = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    let val;
    if (gray >= thresh) {
      val = 255;
    } else {
      val = 0;
    }
    pixels[i] = pixels[i + 1] = pixels[i + 2] = val;
  }
}


function click (x, y) {
  guac.sendMouseState(new Guacamole.Mouse.State(x, y, true));
  guac.sendMouseState(new Guacamole.Mouse.State(x, y, false));
}


function scan () {
  output.width = input.width;
  output.height = input.height;
  context.drawImage(input, 0, 0);
  
  const imageData = context.getImageData(0, 0, output.width, output.height);
  //thresholdFilter(imageData.data, 0.5);
  context.putImageData(imageData, 0, 0);
  
  (async () => {
    
    let { data: { words } } = await scheduler.addJob('recognize', output);
    // words = words.filter(word => word.confidence > 40 && word.text.length > 1)
    console.log(words);
    
    context.strokeStyle = 'red';
    buttonContainer.innerHTML = '';
    
    for (let word of words) {
      context.beginPath();
      context.rect(word.bbox.x0, word.bbox.y0, word.bbox.x1 - word.bbox.x0, word.bbox.y1 - word.bbox.y0);
      context.stroke();
      
      let button = document.createElement('button');
      button.innerHTML = word.text;
      buttonContainer.appendChild(button);
      button.onclick = () => click((word.bbox.x0 + word.bbox.x1) / 2, (word.bbox.y0 + word.bbox.y1) / 2);
    }
    
    
    
    console.log('Scan done');
  })();
}

  
document.getElementById('start').onclick = scan

console.log('Imported automation.js');
