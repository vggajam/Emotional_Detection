"""
    data collection tools
"""

import json
import os
import time
from datetime import datetime
from urllib.parse import urlparse

import bs4
import requests
import tweepy
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def load(url):
    chrome = webdriver.Chrome()
    chrome.get(url)

    tag = chrome.find_element_by_tag_name('html')
    for i in range(300):
        print(i,end=' ')
        tag.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
    print('program ended!')

def extractTweets(file_path, save_to=None):
    doc = open(file_path,encoding='utf-8')
    soup = bs(doc,'html.parser')
    items = soup.find_all('div',class_="tweet")
    tweets_list = list()
    for item in items:
        try:
            tweets_list.append(item.attrs['data-permalink-path'])
        except KeyError:
            pass
    data_dict = dict()
    for link in tweets_list:
        arr = str(link).split('/')
        if arr[1] not in data_dict.keys():
            data_dict[str(arr[1])] = list()
        data_dict[str(arr[1])].append(str(arr[3]))
    if save_to is not None:
        json.dump(data_dict,open(save_to,'w'))
    return data_dict

def mk_db_dir(loc):
    try:
        os.makedirs(loc+'/tweets/')
    except FileExistsError:
        print(loc+'/tweets/ already exists!')

    try:
        os.makedirs(loc+'/media/')
    except FileExistsError:
        print(loc+'/media/ already exists')

    if not os.path.isfile(loc+'/metadata.json'):
        fd = open(loc+'/metadata.json','w')
        fd.write('{}')
        fd.close()

def reply_count(user, tweet_id, log_fd):
        """
            returns reply count of the tweet
        """
        res = requests.get('https://twitter.com/' + user + '/status/' + tweet_id)
        try:
            res.raise_for_status()
        except Exception as exc:
            log_fd.write('There was a problem: %s\n' % (exc))
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        return soup.select('span[data-tweet-stat-count]')[0].attrs['data-tweet-stat-count']

def combine_metadata(self, file1, file2, combinedfile = None):
    """
        combines two metadata files (file1, file2)
        stores in combinedfile
        if not given stores in file1
    """
    metadata1 = json.load(open(file1))
    metadata2 = json.load(open(file2))
    for key in metadata2.keys():
        if key in metadata1.keys():
            metadata1[key]['containsImage'] = metadata1[key]['containsImage'] or metadata2[key]['containsImage']
            metadata1[key]['label'] = str(metadata1[key]['label'] or metadata2[key]['label'])
            metadata1[key]['processed'] = metadata1[key]['processed'] or metadata2[key]['processed']
        else:
            metadata1[key] = metadata2[key]
    print('total keys:', len(metadata1.keys()))
    if combinedfile is None:
        json.dump(metadata1,open(file1,'w'))
    else:
        json.dump(metadata1,open(combinedfile,'w'))

class TweetsCollector:
    """
        twitterdata collector class
    """
    def __init__(self, creds_path='./secrets.json', app_only=True):
        creds = json.load(open(creds_path))['ggajam']
        auth = tweepy.OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
        if not app_only:
            auth.set_access_token(creds['access_token'], creds['access_token_secret'])
        self.api = tweepy.API(auth)

    
    def save_tweet(self, tweet, label, loc, log_fd, metadata):
        """
            saves the tweet with given label at loc
        """
        if 'possibly_sensitive' in tweet.keys() and tweet['possibly_sensitive']:
            return False
        tweet['reply_count'] = reply_count(tweet['user']['screen_name'],tweet['id_str'], log_fd)
        json.dump(tweet, open(loc+'tweets/'+tweet['id_str']+'.json', mode='w'))
        log_fd.write(tweet['id_str'])

        if tweet['id_str'] not in metadata.keys():
            metadata[tweet['id_str']] = dict()
        try:
            for media in tweet['extended_entities']['media']:
                if media['type'] == 'photo':
                    url_pkt = urlparse(media['media_url'])
                    with open(loc+url_pkt.path, 'wb') as imagef:
                        for chunk in requests.get(url_pkt.geturl()).iter_content(100000):
                            imagef.write(chunk)
                    metadata[tweet['id_str']]['containsImage'] = True
        except KeyError:
            pass
        
        if 'processed' not in metadata[tweet['id_str']].keys():
            metadata[tweet['id_str']]['processed'] = False
        if 'label' not in metadata[tweet['id_str']].keys():
            metadata[tweet['id_str']]['label'] = label
        # if 'containsText' not in metadata[tweet['id_str']].keys():
        #     metadata[tweet['id_str']]['containsText'] = bool(len(tweet['text']) >= 1)
        if 'containsImage' not in metadata[tweet['id_str']].keys():
            metadata[tweet['id_str']]['containsImage'] = False
        log_fd.write('saved \n')
        return True

    def by_tweet(self, tweet_id, label, loc='./twitter_db/by_tweet/'):
        """
            collects the tweet and stores
        """
        mk_db_dir(loc)
        metadata = json.load(open(loc+'metadata.json'))
        with open('./logs/by_tweet '+str(datetime.now()).replace(':','-')+'.log', 'w') as log_fd:
            log_fd.write(tweet_id+' '+str(label)+'\n')
            if not self.save_tweet(self.api.get_status(tweet_id)._json, label, loc, log_fd, metadata):
                log_fd.write('sensitive content is present!!\n')
            json.dump(metadata, open(loc+'metadata.json', mode='w'))
            log_fd.write('updated metadata\n')

    def by_user(self, user, since_id='914278686517452800',
                max_id='978852393977999360',
                loc='./twitter_db/by_user/'):
        """
            collects tweets by user
        """
        loc = loc+user+'/' 
        mk_db_dir(loc)
        metadata = json.load(open(loc+'metadata.json'))
        with open('./logs/by_user '+str(datetime.now()).replace(':','-')+'.log', 'w') as log_fd:
            log_fd.write(user+' '+since_id+' '+max_id+' '+loc+'\n')
            for tweet in tweepy.Cursor(self.api.user_timeline,
                                       id=user,
                                       since_id=since_id,
                                       max_id=max_id).items():
                self.save_tweet(tweet._json, None, loc, log_fd, metadata)
            json.dump(metadata, open(loc+'metadata.json', mode='w'))
            log_fd.write('updated metadata\n')

    def by_query(self, qry, label, cnt, loc='./twitter_db/by_query/'):
        """
            search twitter
        """
        mk_db_dir(loc)
        with open('./logs/by_query '+str(datetime.now()).replace(':','-')+'.log', 'w') as log_fd:
            log_fd.write(qry+' '+str(label)+' '+str(cnt)+' '+loc+'\n')
            metadata = json.load(open(loc+'metadata.json'))
            for status in tweepy.Cursor(self.api.search, q=qry, lang='en').items(cnt):
                    self.save_tweet(status._json, label, loc, log_fd, metadata)
            json.dump(metadata, open(loc+'metadata.json', mode='w'))
            log_fd.write('updated metadata\n')

    def image_tweets_by_query(self, qry, label, cnt, loc='./twitter_db/image_tweets_by_query/'):
        """
            search twitter
        """
        mk_db_dir(loc)
        with open('./logs/by_query '+str(datetime.now()).replace(':','-')+'.log', 'w') as log_fd:
            log_fd.write(qry+' '+str(label)+' '+str(cnt)+' '+loc+'\n')
            metadata = json.load(open(loc+'metadata.json'))
            for status in tweepy.Cursor(self.api.search, q=qry).items():
                if cnt > 0:
                    try:
                        tweet = status._json
                        for media in tweet['extended_entities']['media']:
                            if media['type'] == 'photo' and \
                                len(tweet['text']) > 0 and \
                                tweet['id_str'] not in metadata.keys() and\
                                self.save_tweet(tweet, label, loc, log_fd, metadata):
                                    cnt = cnt - 1
                                    log_fd.write(str(cnt)+'\n')
                                    print(cnt)
                    except KeyError:
                        pass
                else:
                    break
            json.dump(metadata, open(loc+'metadata.json', mode='w'))
            log_fd.write('updated metadata\n')
    
    def fix_metadata(self, loc):
        with open('./logs/fix_metadata'+str(datetime.now()).replace(':','-')+'.log','w') as log_fd:
            log_fd.write('fix_metadata '+loc+'\n')
            metadata = json.load(open(loc+'/metadata.json'))
            for x in os.listdir(loc+'./tweets'):
                if str(x[:-5]) not in metadata.keys():
                    log_fd.write(x[:-5]+'\n')
                    metadata[str(x[:-5])] = {'processed': False,#'containsText': True,\
                                            'label': None,'containsImage': None}
            json.dump(metadata, open(loc+'metadata.json','w'))
            log_fd.write('metadata fixed..\n')
            
            dirtweets = os.listdir(loc+'./tweets')
            for x in metadata.keys():
                if (x+'.json') not in dirtweets:
                    log_fd.write(x+'\n')
                    self.save_tweet(self.api.get_status(x)._json, None, loc, log_fd, metadata)
            log_fd.write('tweets dir is fixed..\n')            

    def removescrap(self, loc):
        with open('./logs/removescrap '+str(datetime.now()).replace(':','-')+'.log','w') as log_fd:
            log_fd.write('removescrap '+loc+'\n')
            self.fix_metadata(loc)
            metadata =json.load(open(loc+'/metadata.json'))
            selected_list = list()
            for x in metadata.keys():
                tweet = json.load(open(loc+'/tweets/'+x+'.json'))
                if 'possibly_sensitive' in tweet.keys() and tweet['possibly_sensitive']:
                    selected_list =  selected_list + [x]
                elif metadata[x]['containsImage']:
                    for media in tweet['extended_entities']['media']:
                        if media['type'] == 'photo':
                            url_pkt = urlparse(media['media_url'])
                            if not os.path.exists(loc+'/'+url_pkt.path):
                                # print(loc+url_pkt.path)
                                selected_list = selected_list + [x]
                                break
            for x in selected_list:
                tweet = json.load(open(loc+'/tweets/'+x+'.json'))
                if metadata[x]['containsImage']:
                    for media in tweet['extended_entities']['media']:
                        if media['type'] == 'photo':
                            url_pkt = urlparse(media['media_url'])
                            if os.path.exists(loc+'/'+url_pkt.path):
                                os.remove(loc+'/'+url_pkt.path)
                if os.path.exists(loc+'/tweets/'+x+'.json'):
                    os.remove(loc+'/tweets/'+x+'.json')
                if x in metadata.keys():
                    del metadata[x]
                log_fd.write(x+'\n')
                # print(x)
            json.dump(metadata,open(loc+'/metadata.json','w'))
            log_fd.write('updated metadata\n')
