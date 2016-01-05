var addParam = function(url, params) {
  if (typeof params !== 'object') {
    return url;
  }
  var _add = function(url, key, value) {
    var joint;
    joint = url.indexOf('?') > -1 ? '&' : '?';
    key = encodeURIComponent(key);
    value = encodeURIComponent(value);
    url = url + joint + key + '=' + value;
    return url;
  };
  for (var k in params) {
    var v = params[k];
    if (typeof v === 'object' && typeof v.length === 'number') {
      for (var i = 0, len = v.length; i < len; i++) {
        var item = v[i];
        url = _add(url, k, item);
      }
    } else {
      url = _add(url, k, v);
    }
  }
  return url;
};

var parse_response = function(xhr, headers) {
  var data;
  var resp_type = xhr.responseType
  if (resp_type === 'json') {
    data = xhr.response;
  } else if (resp_type === 'blob' || resp_type === 'arraybuffer') {
    data = xhr.response;
  } else if (resp_type === 'document') {
    data = xhr.responseXML;
  } else if (resp_type === '' || resp_type === 'text') {
    data = xhr.responseText;
  }
  var result = {
    data: data,
    headers: xhr.getAllResponseHeaders(),
    status: xhr.status,
    statusText: xhr.statusText,
    responseType: xhr.responseType,
    responseURL: xhr.responseURL
  };
  return result;
};
  
var ajax = function(request) {

  var xhr = new XMLHttpRequest();
  var url = addParam(request.url, request.params);
  var type = request.type
  xhr.open(type, url || '', true);
  xhr.responseType = request.responseType || 'json';
  xhr.withCredentials = Boolean(request.withCredentials);
  xhr.setRequestHeader('Content-Type', 'application/json');
  if (typeof request.headers === 'object') {
    for (var k in request.headers) {
      var v = request.headers[k];
      xhr.setRequestHeader(k, v);
    }
  }

  promise = new Promise(function(resolve, reject){
    var ready = function(e) {
      var result;
      xhr = this;
      if (xhr.readyState === xhr.DONE) {
        xhr.removeEventListener('readystatechange', ready);
        result = parse_response(xhr);
        if (xhr.status >= 200 && xhr.status < 399) {
          return resolve(result.data);
        } else {
          return reject(result);
        }
      }
    };
    xhr.addEventListener('readystatechange', ready);
  })

  if (type === 'GET' || type === 'DELETE') {
    xhr.send();
  } else {
    try {
      var send_data = JSON.stringify(request.data || {});
    } catch (error) {
      throw error;
    }
    xhr.send(send_data);
  }
  
  return promise
};
