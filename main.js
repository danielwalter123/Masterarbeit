window.onload =  function() {

  document.getElementById('initialize').onclick = function () {
    import('./automation.js?queryToInvalidateCache=' + Date.now());
  };
  
};