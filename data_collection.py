"""
    data collection tools
"""

import json
from datetime import datetime
from urllib.parse import urlparse
import os

import bs4
import requests
import tweepy


class TweetsCollector:
    """
        twitterdata collector class
    """
    def __init__(self, creds_path='./secrets.json', mode='c'):
        creds = json.load(open(creds_path))
        if 'c' in mode:
            auth = tweepy.OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
        if 'a' in mode:
            auth.set_access_token(creds['access_token'], creds['access_token_secret'])
        self.api = tweepy.API(auth)

    def reply_count(self, user, tweet_id, log_fd):
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

    def save_tweet(self, tweet, label, loc, log_fd, metadata):
        """
            saves the tweet with given label at loc
        """
        if tweet['possibly_sensitive']:
            return False
        tweet['reply_count'] = self.reply_count(tweet['user']['screen_name'],
                                                tweet['id_str'], log_fd)
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
        finally:
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

        metadata = json.load(open(loc+'metadata.json'))
        with open('./logs/by_tweet '+str(datetime.now()).replace(':','-')+'.log', 'w') as log_fd:
            log_fd.write(tweet_id+' '+str(label)+'\n')
            if not self.save_tweet(self.api.get_status(tweet_id)._json, label, loc, log_fd, metadata):
                log_fd.write('sensitive content is present!!\n')
            json.dump(metadata, open(loc+'metadata.json', mode='w'))
            log_fd.write('updated metadata\n')

    def by_user(self, user, since_id='914278686517452800',
                max_id='947618370152693760',
                loc='./twitter_db/by_user/'):
        """
            collects tweets by user
        """
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
            