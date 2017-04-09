import re
import enchant
from enchant.tokenize import get_tokenizer, EmailFilter
from fuzzywuzzy import fuzz

SCORE = 0
EMAIL_BODY = ''
EMAIL_LINKS = []
# key: link text, value: actual link
EMAIL_HYPERLINKS = {}
BAD_SALUTATIONS = [
    'valued customer',
    'dear customer',
    'dear valued customer'
]

def spellcheck():
    dictionary = enchant.Dict("en_US")
    word_list = get_tokenizer("en_US", [EmailFilter])
    has_mispellings = any((not dictionary.check(word)) and word[0].islower() for word in word_list)

    if has_mispellings:
        # add value
        pass

def salutation_check():
    # this is hopefully the salutation
    first_line = EMAIL_BODY.splitlines()[0]
    has_bad_salutation = any(fuzz.ratio(first_line, bad_salutation) > 90 for bad_salutation in BAD_SALUTATIONS)

    if has_bad_salutation:
        # add value
        pass
