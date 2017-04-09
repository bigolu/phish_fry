import re
import enchant
from enchant.tokenize import get_tokenizer, EmailFilter
from fuzzywuzzy import fuzz
import urllib2
import re

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
MISSPELL_SCORE = 30
SALUTATION_SCORE = 50
THREATENING_LANGUAGE_SCORE = 40
ATTACHMENT_SCORE = 40
HYPERLINK_NOT_MATCH_SCORE = 40
PERSONAL_CREDENTIALS_SCORE = 20
WOT_BAD_SITE_SCORE = 70


def check_if_trusted_site():
    s = 'http://api.mywot.com/0.4/public_link_json2?hosts=www.example.COM/www.EXAMPLE.NET/&callback=process&' \
        'key={}'.format(WOT_APIKEY)

    global SCORE

    response = urllib2.urlopen(s).read()

    if any(code in response for code in WOT_BAD_CODES):
        SCORE += WOT_BAD_SITE_SCORE


def hyperlink_match():
    global SCORE
    for key, value in EMAIL_HYPERLINKS:
        if key != value:
            if key.startswith('www') or key.startswith('http'):
                continue
            SCORE += HYPERLINK_NOT_MATCH_SCORE
            return


def spellcheck():
    global SCORE
    dictionary = enchant.Dict("en_US")
    word_list = get_tokenizer("en_US", [EmailFilter])
    # has_mispellings = any((not dictionary.check(word)) and word[0].islower() for word in word_list)
    for word in word_list:
        if not dictionary.check(word):
            misspelled = True
        else:
            misspelled = False
        if word[0].islower():
            weirdly_cased = True
        else:
            weirdly_cased = False

        if misspelled and weirdly_cased is False: # ONLY increment score when mispelled, not capitalized
            SCORE += MISSPELL_SCORE

    return


def salutation_check():
    # this is hopefully the salutation
    global SCORE
    first_line = EMAIL_BODY.splitlines()[0]
    has_bad_salutation = any(fuzz.ratio(first_line, bad_salutation) > 90 for bad_salutation in BAD_SALUTATIONS)

    if has_bad_salutation:
        SCORE += SALUTATION_SCORE


def threatening_language_check():
    global SCORE
    for line in EMAIL_BODY.splitlines():
        if any(fuzz.ratio(line, threatening_language) > 90 for threatening_language in THREATENING_LANGUAGE):
            SCORE += THREATENING_LANGUAGE_SCORE
            return


def personal_credentials_check():
    global SCORE
    for line in EMAIL_BODY.splitlines():
        if any(fuzz.ratio(line, personal_credentials) > 90 for personal_credentials in PERSONAL_CREDENTIALS):
            SCORE += PERSONAL_CREDENTIALS_SCORE
            return


def attachment_check():
    # check for attachment somehow?
    global SCORE
    has_attachment = False
    if has_attachment:
        SCORE += ATTACHMENT_SCORE
