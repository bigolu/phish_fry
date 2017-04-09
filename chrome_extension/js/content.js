var PHISHING_REPORT_ENDPOINT = null;

function injectButton(){
  var possibleEmailDivs = $("div[dir='ltr']");
  var rawEmail = $(possibleEmailDivs[possibleEmailDivs.length - 1]);

  var button = $(
    "<div> <p> biggie is here </p> </div>"
  );
  button.on('click', analyze);
  rawEmail.append(button);
}

/*
 * //TODO: describe object returned
 */
function parseEmailBody(){
  var emailContents = {
    "emailBody": null,
    "links": [],
    "hyperlinks": {}
  };
  var possibleEmailDivs = $("div[dir='ltr']");
  var rawEmail = $(possibleEmailDivs[possibleEmailDivs.length - 1]);

  emailContents["emailBody"] = rawEmail.clone().find("a").remove().end().text();

  var allLinks = rawEmail.clone().find("a");
  allLinks.each(function(){
    link = $(this)[0];
    var linkText = link.innerText;
    var actualLink = link.href;

    /* hyperlinks have a childcount of 0 whereas inline links
     * have a childcount of 1 and so we will use this to 
     * differentiate between the 2
     */
    if(link.childElementCount == 0){
      emailContents["hyperlinks"][linkText] = actualLink;
    }
    else{
      emailContents["links"].push(actualLink);
    }
  });
  
  return emailContents;
}

function getPhishingReport(emailContents){
  var xhr = new XMLHttpRequest();

  xhr.open("POST", PHISHING_REPORT_ENDPOINT, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      alert(xhr.responseText);
    }
  }
  //xhr.send(JSON.stringify(emailContents));
}

function analyze(){
  var emailContents = parseEmailBody();
  var phishingReport = getPhishingReport();
}

chrome.runtime.onMessage.addListener(function(msg){
  if(msg["action"] == "button"){
    injectButton();
  }
});
