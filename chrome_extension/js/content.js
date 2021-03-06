var PHISHING_REPORT_ENDPOINT = "https://5cc21b87.ngrok.io/phish";
var BUTTON;
var SCORE;
var REPORT;

function injectButton(){
  var possibleEmailDivs = $("div[dir='ltr']");
  var rawEmail = $(possibleEmailDivs[possibleEmailDivs.length - 1]);

  BUTTON = $(
    "<br><br><button type=\"button\" class=\"btn btn-info\"> analyze </button>"
  );
  BUTTON.on('click', analyze);
  rawEmail.append(BUTTON);
}

function parseEmailBody(){
  var emailContents = {
    emailBody: null,
    links: [],
    hyperlinks: {}
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

function showReport(){
}

function showScore(reportData){
  SCORE = reportData.Score;
  REPORT = reportData.Report;

  BUTTON.text(SCORE);
  BUTTON.removeClass('btn-info').addClass((SCORE < 100) ? 'btn-success' : 'btn-danger');
  BUTTON.on('click', showReport);
}

function getPhishingReport(emailContents){
  $.ajax({
    url: PHISHING_REPORT_ENDPOINT,
    type: "POST",
    data: JSON.stringify(emailContents),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: showScore
  });
}

function analyze(){
  var emailContents = parseEmailBody();
  var phishingReport = getPhishingReport(emailContents);
}

chrome.runtime.onMessage.addListener(function(msg){
  if(msg["action"] == "button"){
    injectButton();
  }
});
