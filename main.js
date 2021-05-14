window.onload =  function() {

  document.getElementById('initialize').onclick = function () {
    import('./automation.js?queryToInvalidateCache=' + Date.now());
  };
  
  document.getElementById('screenshot').onclick = function () {
    const canvas = document.getElementById('emulator-container').querySelector('canvas');
    const dataURL = canvas.toDataURL("image/png");
    const newTab = window.open('about:blank','image from canvas');
    newTab.document.write("<img src='" + dataURL + "' alt='from canvas'/>");
  };
};