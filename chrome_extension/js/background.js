var GMAIL_OPEN_EMAIL_URL_PATTERN = /https:\/\/mail.google.com\/mail\/.*\/.*\/#inbox\/.*/;

chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab){
  if(!changeInfo.hasOwnProperty('url')){
    return;
  }

  var url = changeInfo.url;
  if(GMAIL_OPEN_EMAIL_URL_PATTERN.test(url)){
    chrome.tabs.sendMessage(tabId, {"action": "button"});
  }
});
