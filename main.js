window.onload =  function() {

  import('./automation.js');
  
  document.getElementById('reload').onclick = function () {
    import('./automation.js?queryToInvalidateCache=' + Date.now());
  };
  
};