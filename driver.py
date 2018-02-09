"""
    driver program
"""
# import csv
from textblob import TextBlob
import json
from twitter_preprocess import all_features_by_tweet

import spacy

NLP = spacy.load('en')

def degree(text):
    """
        1-3 to represent neutral, moderate, and
        severe degree of positive emotions, and the minus to represent the negative
        ones
    """
    pol = TextBlob(text).polarity * 3
    arr = [-2, -1, 0]
    for i in arr:
        if pol < i:
            return i-1
    arr = [2, 1, 0]
    for i in arr:
        if pol > i:
            return i+1
    return 0

def adv_attr(text):
    tweet_degree = degree(text)
    adv_tot = 0
    adj_cnt = 0
    tokens = NLP(text)
    for token in tokens:
        if token.dep_ == 'advmod':
            adv_tot = adv_tot+1
            if degree(token.head.text) == tweet_degree:
                adj_cnt = adj_cnt +1
        # print(token, token.dep_, token.head, token.head.pos_)
    if adv_tot:
        return [(tweet_degree*adj_cnt)/adv_tot, adj_cnt]
    else:
        return [0, 0]
if __name__ == "__main__":
    
    """
        entry point of program
    """
    # print(adv_attr('I am feeling terribly sad'))
    json.dump(all_features_by_tweet(),open('./op.json','w'))

