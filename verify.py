import re
import enchant
from enchant.tokenize import get_tokenizer, EmailFilter
from fuzzywuzzy import fuzz
import urllib2
import re
from flask import Flask, request, jsonify
import json

SCORE = 0
EMAIL_BODY = ''
EMAIL_LINKS = []
# key: link text, value: actual link
EMAIL_HYPERLINKS = {}
WOT_BAD_CODES = ['101', '102', '103', '104', '105']
BAD_SALUTATIONS = [
    'valued customer',
    'dear customer',
    'dear valued customer'
]
PHISHING_FLAGS = []
WOT_APIKEY = 'cdec02776c185c47e12d6787bd81267cd8187f27'
THREATENING_LANGUAGE = [
    'unauthorized login attempt',
    'account suspended',
    'imminent action required'
]
PERSONAL_CREDENTIALS = [
    'ssn',
    'social security',
    'credit card',
    'password',
    'maiden name',
    'account number'
]
MISSPELL_SCORE = 10
SALUTATION_SCORE = 30
THREATENING_LANGUAGE_SCORE = 20
ATTACHMENT_SCORE = 40
HYPERLINK_NOT_MATCH_SCORE = 40
PERSONAL_CREDENTIALS_SCORE = 30
WOT_BAD_SITE_SCORE = 100

app = Flask(__name__)

def check_if_trusted_site():
    s = 'http://api.mywot.com/0.4/public_link_json2?hosts=www.example.COM/www.EXAMPLE.NET/&callback=process&' \
        'key={}'.format(WOT_APIKEY)
 
    global SCORE

    response = urllib2.urlopen(s).read()

    if any(code in response for code in WOT_BAD_CODES):
        SCORE += WOT_BAD_SITE_SCORE
        global PHISHING_FLAGS
        PHISHING_FLAGS.append('Untrusted Site')
    

def hyperlink_match():
    global SCORE
    for key, value in EMAIL_HYPERLINKS.iteritems():
        if key != value:
            if key.startswith('www') or key.startswith('http'):
                continue
            SCORE += HYPERLINK_NOT_MATCH_SCORE
            global PHISHING_FLAGS
            PHISHING_FLAGS.append('Hyperlink does not match actual link')
            return


def spellcheck():
    global SCORE
    dictionary = enchant.Dict("en_US")
    tokenizer = get_tokenizer("en_US")
    # has_mispellings = any((not dictionary.check(word)) and word[0].islower() for word in word_list)
    for word in tokenizer(EMAIL_BODY):
        word = word[0]
        if not dictionary.check(word):
            print word
            misspelled = True
        else:
            misspelled = False

        if word[0].islower():
            weirdly_cased = False
        else:
            weirdly_cased = True

        if misspelled == True and weirdly_cased == False: # ONLY increment score when mispelled, not capitalized
            SCORE += MISSPELL_SCORE
            global PHISHING_FLAGS
            PHISHING_FLAGS.append('Misspelled word(s)')
            return

    return


def salutation_check():
    # this is hopefully the salutation
    global SCORE
    '''
    first_line = EMAIL_BODY.splitlines()[0]
    has_bad_salutation = any(fuzz.ratio(first_line, bad_salutation) > 90 for bad_salutation in BAD_SALUTATIONS)
    '''

    for salutation in BAD_SALUTATIONS:
        if salutation in EMAIL_BODY:
            has_bad_salutation = True

    if has_bad_salutation:
        SCORE += SALUTATION_SCORE
        global PHISHING_FLAGS
        PHISHING_FLAGS.append('Suspicious Salutation')


def threatening_language_check():
    global SCORE
    '''
    for line in EMAIL_BODY.splitlines():
        if any(fuzz.ratio(line, threatening_language) > 90 for threatening_language in THREATENING_LANGUAGE):
            SCORE += THREATENING_LANGUAGE_SCORE
    '''
    for threat in THREATENING_LANGUAGE:
        if threat in EMAIL_BODY:
            SCORE += THREATENING_LANGUAGE_SCORE
            global PHISHING_FLAGS
            PHISHING_FLAGS.append('Threatening Language in this email')
            return


def personal_credentials_check():
    global SCORE
    '''
    for line in EMAIL_BODY.splitlines():
        if any(fuzz.ratio(line, personal_credentials) > 90 for personal_credentials in PERSONAL_CREDENTIALS):
    '''
    for credential in PERSONAL_CREDENTIALS:
        if credential in EMAIL_BODY:
            SCORE += PERSONAL_CREDENTIALS_SCORE
            global PHISHING_FLAGS
            PHISHING_FLAGS.append('They mention personal credentials')
            return

def attachment_check():
    # check for attachment somehow?
    global SCORE
    has_attachment = False
    if has_attachment:
        SCORE += ATTACHMENT_SCORE

def create_global_data(data):
    print data['emailBody']
    global EMAIL_BODY, EMAIL_LINKS, EMAIL_HYPERLINKS
    EMAIL_BODY = data['emailBody']
    EMAIL_LINKS = data['links']
    EMAIL_HYPERLINKS = data['hyperlinks']

    
    
@app.route("/phish", methods=['POST'])
def phish():
    create_global_data(json.loads(request.data))
    spellcheck()
    personal_credentials_check()
    threatening_language_check()
    salutation_check()
    check_if_trusted_site()
    hyperlink_match()
    
    return jsonify({'Score':str(SCORE),
                    'Report': PHISHING_FLAGS}) 

if __name__ == "__main__":
    app.run(debug=True)
