"""
    twitter preprocess tools
"""
import datetime as dt
import json
from urllib.parse import urlparse

import cv2
import numpy as np
import spacy
from nltk.tokenize import TweetTokenizer
from textblob import TextBlob

TF = "%a %b %d %H:%M:%S %z %Y"
EMOJI_POL = json.load(open('./emoji_pol.json'))
NLP = spacy.load('en')
PP = ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them']
WORD_CATS = NLP('home work money religion death health food friend family')
SIMI_THRESHOLD = 0.5

def weekno(tweet_time):
    tt = dt.datetime.strptime(tweet_time,TF)
    return(str(tt.isocalendar()[0])+'_'+str(tt.isocalendar()[1]))

def wordcat(tokens = None, text = ''):
    res = np.zeros(10)
    print(tokens)
    if tokens is None:
        tokens = NLP(text)
    for token in tokens:
        if not token.is_stop:
            if token.text in PP:
                res[0] = res[0] +1
            else:
                sim_list = np.zeros(9)
                for i in range(len(WORD_CATS)):
                    sim_list[i] = token.similarity(WORD_CATS[i])
                print(sim_list)
                idx = np.argmax(sim_list)
                print(token, WORD_CATS[idx].text, sim_list[idx])
                res[idx+1] = res[idx+1] +1
    return res

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

def adv_attr(tokens, text):
    tweet_degree = degree(text)
    adv_tot = 0
    adj_cnt = 0
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

def atostr(arr):
    """
        converts 1-d array to string for using as key
    """
    res = ''
    for i in arr:
        res = res + '|' + str(i)
    return res

def five_color_theme(hsv_mat):
    """five color theme attributes
    """
    attr_list = np.zeros(15)
    pdict = dict()
    for i in np.reshape(hsv_mat, (-1, 3)):
        tmp = atostr(i)
        if tmp in pdict.keys():
            pdict[tmp][0] = pdict[tmp][0] + 1
        else:
            pdict[tmp] = [0, i]
    plist = sorted(pdict.values(), key=lambda x: x[0], reverse=True)

    tmp_list = list()
    no_of_items = min([5, len(plist)])
    for i in plist[:no_of_items]:
        tmp_list.append([i[1]])
    attr_list[:no_of_items * 3] = np.reshape(np.array(tmp_list), (-1))
    return list(attr_list)

def ling_features(text):
    """----------------- lingistic ------------------
        0 -> positive words count
        1 -> negative words count
        2 -> positive emoji count
        3 -> negative emoji count
        4-7 -> ! ? ... . counts
        8 -> degree adverb
        9 -> cnt of emotion words
    """
    containsText = False
    attr = np.zeros(10)
    tokens = NLP(text)
    # linguistic feature extraction
    for token in tokens:
        # print(token, token.pos_)
        if token.text.startswith('https://') or token.text.startswith('http://'):
            continue
        containsText = True
        if token.text in EMOJI_POL.keys():
            if EMOJI_POL[token.text] > 0:
                attr[2] = attr[2]+1
            elif EMOJI_POL[token.text] < 0:
                attr[3] = attr[3]+1
        elif token.text == '!':
            attr[4] = attr[4]+1
        elif token.text == '?':
            attr[5] = attr[5]+1
        elif token.text == '...':
            attr[6] = attr[6]+1
        elif token.text == '.':
            attr[7] = attr[7]+1
        else:
            blob = TextBlob(token.text)
            if blob.polarity > 0:
                attr[0] = attr[0]+1
            elif blob.polarity < 0:
                attr[1] = attr[1]+1
    if containsText:
        attr[8:10] = adv_attr(tokens, text)
        return list(attr)
    else:
        return None

def vis_features(pic_path):
    """------------------ visual --------------------
        0-14 -> five-color theme
        15-16 -> mean value of saturation and its contrast
        17-18 -> mean value of brightness and its contrast
        19 -> warm/cool: Ratio of cool colors with hue ([0-360]) in the HSV space in [30, 110]
        or for hue([0,255]) in [21.25,77.917]
        20 -> ratio of colors with brightness and saturation
    """

    mat = cv2.imread(pic_path, -1)
    hsv_mat = cv2.cvtColor(mat, cv2.COLOR_BGR2HSV)
    attr = np.zeros(21)

    hue_constr = [21.5, 77.917]
    attr[0:15] = five_color_theme(hsv_mat)

    [_, attr[15], attr[17]] = np.mean(hsv_mat, axis=(0, 1))
    [_, attr[16], attr[18]] = np.amax(hsv_mat, axis=(0, 1))-np.amin(hsv_mat, axis=(0, 1))

    neum = set()
    den = set()
    for i in range(np.shape(mat)[0]):
        for j in range(np.shape(mat)[1]):
            if mat[i][j][0] < mat[i][j][2]:
                den.add(atostr(mat[i][j]))
                if hsv_mat[i][j][0] >= hue_constr[0] and hsv_mat[i][j][0] <= hue_constr[1]:
                    neum.add(atostr(mat[i][j]))
    attr[19] = len(neum) / len(den)

    neum = set()
    den = set()
    for i in np.reshape(hsv_mat, (-1, 3)):
        den.add(atostr(i))
        if i[1] < 0.6*255:
            neum.add(atostr(i))
    attr[20] = len(neum) / len(den)
    return list(attr)

def behave_features(tweet):
    """
        posting behavior attributes
        0 -> no of mentions
        1 -> is it a retweet? 1 / 0
        2 -> is it a reply? 1 / 0

        3-26 -> tweet hour

        27 -> image tweet
        28 -> original tweet
        29 -> query tweet
        30 -> information sharing tweet

        31 -> personal pronouns
        32 -> home
        33 -> work
        34 -> money
        35 -> religion
        36 -> death
        37 -> health
        38 -> ingestion
        39 -> friends
        40 -> family
    """
    attr = np.zeros(41)
    attr[0] = len(tweet['entities']['user_mentions'])
    attr[1] = int('retweeted_status' in tweet.keys())
    attr[2] = int(tweet['in_reply_to_status_id'] != None)

    time = dt.datetime.strptime(tweet['created_at'], TF) + dt.timedelta(seconds=int(tweet['user']['utc_offset']))
    attr[3+int(time.hour)] = 1

    try:
        attr[27] = int(tweet['entities']['media'][0]['type']=='photo')
    except KeyError:
        attr[27] = 0
    attr[28] = 'retweeted_status' not in tweet.keys() and tweet['in_reply_to_status_id'] is None
    attr[29] = '?' in tweet['text']
    try:
        attr[30] = int(len(tweet['entities']['urls']) >= 1)
    except:
        attr[30] = 0

    return list(attr)

def sintrxn_features(tweet):
    """social interaction attributes
        content style:
            0 -> personal pronouns
            1 -> home
            2 -> work
            3 -> money
            4 -> religion
            5 -> death
            6 -> health
            7 -> ingestion
            8 -> friends
            9 -> family

            10 -> positive emojis
            11 -> negative emojis

        sociallization:
            dictionary with key,value pairs
                where key is user,
                    value is interaction count
    """
    attr = np.zeros(12)
    social = dict()
    tokens = NLP(tweet['text'])
    attr[:10] = wordcat(tokens)

    for token in tokens:
        if token in EMOJI_POL:
            if EMOJI_POL[token.text] > 0:
                attr[10] = attr[10] +1
            elif EMOJI_POL[token.text] < 0:
                attr[11] = attr[11] +1
    pol = int(TextBlob(tweet['text']).polarity>0)
    for mention in tweet['entities']['user_mentions']:
        if mention['screen_name'] not in social:
            social[mention['screen_name']]=[0,0]
        social[mention['screen_name']][pol] = social[mention['screen_name']][pol]+1

    return list(attr), social

def satnxn_features(tweet):
    """------------------ social ---------------------
        0 -> comments/reply count
        1 -> retweets count
        2 -> likes/favorites count
    """
    attr = np.zeros(3)
    attr[0] = int(tweet['reply_count'])
    attr[1] = int(tweet['retweet_count'])
    attr[2] = int(tweet['favorite_count'])
    if attr[0] == 0 and attr[1] == 0 and attr[2] == 0:
        return None
    return list(attr)

def fix_metadata(twitter_db='./twitter_db/by_query'):
    print(twitter_db)
    return

def all_features_by_tweet(tweet_id='958527757063000065', twitter_db='./twitter_db/by_tweet/'):
    """
        feature extractor function
    """
    # meta_fd = json.load(open(twitter_db+'/metadata.json'))
    tweet = json.load(open(twitter_db+'/tweets/'+tweet_id+".json"))

    features_pkt = dict()
    features_pkt['tweet_id'] = tweet_id
    features_pkt['user_id'] = tweet['user']['id_str']
    features_pkt['time'] = tweet['created_at']
    features_pkt['ling'] = ling_features(tweet['text'])
    try:
        if tweet['extended_entities']['media'][0]['type'] == 'photo':
            features_pkt['vis'] = vis_features(twitter_db+urlparse(tweet['extended_entities']['media'][0]['media_url']).path)
        else:
            features_pkt['vis'] = None
    except KeyError:
        features_pkt['vis'] = None

    features_pkt['satnxn'] = satnxn_features(tweet)
    features_pkt['behave'] = behave_features(tweet)
    features_pkt['cstyle'], features_pkt['social'] = sintrxn_features(tweet)
    return features_pkt

def user_features(user = 'venugopalgajam', db_loc='./twitter_db/by_user/', save_to_files = True):
    try:
        metadata =  json.load(open(db_loc+str(user)+'/metadata.json'))
    except FileNotFoundError:
        print('metadata file missing!!')
        return
    print(metadata)
    tweet_attrs = dict()
    user_attrs = dict()
    social_attrs = dict()
    for tweet_id in metadata:
        # tweet = json.load(open(db_loc+'/tweets/'+str(tweet_id)+".json"))        
        features = all_features_by_tweet(str(tweet_id),db_loc+'/'+str(user)+'/')
        week = weekno(features['time'])
        tweet_attrs_row = list()
        
        if features['ling'] is None:
            tweet_attrs_row = [0.0]*10
        else:
            tweet_attrs_row = features['ling']
        
        if features['vis'] is None:
            tweet_attrs_row =  tweet_attrs_row + [0.0]*21
        else:
            tweet_attrs_row = tweet_attrs_row + features['vis']

        if features['satnxn'] is None:
            tweet_attrs_row = [0.0]*3
        else:
            tweet_attrs_row = tweet_attrs_row + features['satnxn']

        if week not in tweet_attrs:
            tweet_attrs[week] =list()
        tweet_attrs[week].append([str(tweet_id)]+tweet_attrs_row)

        user_attrs_row = features['behave']+features['cstyle']
        if week not in user_attrs:
            user_attrs[week] = user_attrs_row
        else:
            for i in range(len(user_attrs[week])):
                  user_attrs[week][i] = user_attrs[week][i] + user_attrs_row[i]
    
        if week not in social_attrs:
            social_attrs[week]=features['social']
        else:
            for key in features['social']:
                if key in social_attrs[week]:
                    social_attrs[week][key] = np.add(social_attrs[week][key], features['social'][key]).tolist()
                else:
                    social_attrs[week][key] = features['social'][key]
    
    if save_to_files:
        json.dump(tweet_attrs, open(db_loc+'/'+str(user)+'/tweet_attrs.json','w',encoding='utf-8'))
        json.dump(user_attrs, open(db_loc+'/'+str(user)+'/user_attrs.json','w',encoding='utf-8'))
        json.dump(social_attrs, open(db_loc+'/'+str(user)+'/social_attrs.json','w',encoding='utf-8'))
    return tweet_attrs, user_attrs, social_attrs
