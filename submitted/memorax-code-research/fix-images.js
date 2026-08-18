(async function() {
  var urls = [
    { url: 'http://127.0.0.1:9876/images/architecture_small.png', alt: 'MemoraX Code 系统架构', selector: 'text' },
    { url: 'http://127.0.0.1:9876/images/memory-lifecycle_small.png', alt: '记忆生命周期', selector: 'text' },
    { url: 'http://127.0.0.1:9876/images/data-flow_small.png', alt: '记忆检索与写回流程', selector: 'text' }
  ];

  var dataUrls = [];
  for (var i = 0; i < urls.length; i++) {
    try {
      var resp = await fetch(urls[i].url);
      var blob = await resp.blob();
      var dataUrl = await new Promise(function(resolve) {
        var reader = new FileReader();
        reader.onloadend = function() { resolve(reader.result); };
        reader.readAsDataURL(blob);
      });
      dataUrls.push({ dataUrl: dataUrl, alt: urls[i].alt });
    } catch(e) {
      console.log('FETCH_ERROR_' + i + ':' + e.message);
      dataUrls.push(null);
    }
  }

  console.log('FETCH_DONE:' + dataUrls.length + ' images fetched');

  var editor = document.querySelector('[contenteditable=true]') || document.querySelector('.ProseMirror') || document.querySelector('#edui1_contentplaceholder') || document.querySelector('.edui-body-container');
  if (!editor) {
    var editors = document.querySelectorAll('div[contenteditable=true]');
    if (editors.length > 0) editor = editors[0];
  }

  if (!editor) {
    console.log('NO_EDITOR_FOUND');
    return;
  }

  console.log('EDITOR_FOUND:' + editor.className.substring(0, 50));

  var imgs = editor.querySelectorAll('img');
  console.log('EDITOR_IMG_COUNT:' + imgs.length);

  if (imgs.length > 0) {
    for (var i = 0; i < imgs.length && i < dataUrls.length; i++) {
      if (dataUrls[i] && dataUrls[i].dataUrl) {
        imgs[i].src = dataUrls[i].dataUrl;
        console.log('SET_IMG_SRC_' + i);
      }
    }
  } else {
    var allImgs = document.querySelectorAll('img');
    console.log('ALL_IMG_COUNT:' + allImgs.length);
    for (var i = 0; i < allImgs.length && i < dataUrls.length; i++) {
      if (dataUrls[i] && dataUrls[i].dataUrl) {
        allImgs[i].src = dataUrls[i].dataUrl;
        console.log('SET_ALL_IMG_SRC_' + i);
      }
    }

    if (allImgs.length === 0 && dataUrls.length > 0) {
      console.log('NO_IMGS_CREATING_NEW');
      for (var i = 0; i < dataUrls.length; i++) {
        if (dataUrls[i] && dataUrls[i].dataUrl) {
          var img = document.createElement('img');
          img.src = dataUrls[i].dataUrl;
          img.alt = dataUrls[i].alt;
          img.style.cssText = 'width:100%;max-width:640px;display:block;margin:20px auto;';
          editor.appendChild(img);
          console.log('CREATED_IMG_' + i);
        }
      }
    }
  }

  console.log('FIX_IMAGES_DONE');
})();
