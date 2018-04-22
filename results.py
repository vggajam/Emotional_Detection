import csv

import joblib
import numpy as np
import pandas as pd

from ml_models import make_dnn, make_dtree, make_knn, make_lr,make_svm
from sklearn.metrics import confusion_matrix
tweet_attr = ['fposemo','fnegemo','fposemoji','fnegemoji','fperiod','fqmark','fexclaim','f3dots','fdeg_adv','fadv_cnt','ffct1','ffct2','ffct3','ffct4','ffct5','ffct6','ffct7','ffct8','ffct9','ffct10','ffct11','ffct12','ffct13','ffct14','ffct15','fsat_mean','fsat_contrast','fbrit_mean','fbrit_contrast','fwarm_cool','fclear_dull','freplies_cnt','fretweets_cnt','flikes_cnt']
behave = ['mentions_cnt','retweet_cnt','reply_cnt','hour0','hour1','hour2','hour3','hour4','hour5','hour6','hour7','hour8','hour9','hour10','hour11','hour12','hour13','hour14','hour15','hour16','hour17','hour18','hour19','hour20','hour21','hour22','hour23','imagetweet_cnt','originalTweet_cnt','query_cnt','sharingtweet_cnt']
liwc_cat = ['ppron','home','work','money','relig','death','health','ingest','friend','family','reward','achieve','affiliation','swear']
prons = ['i','you','shehe','we','they']
replies = ['rfamily','rfriend','rposemo','raffect','rleisure','rsad','rdeath','rauxverb','ranger','rnegemo','rposemoji','rnegemoji']
past_tweets = ['ppos','pneg','pneu']
dayfile = './datasets/db2_daywise_cae.csv'


print('Week wise:')
weekfile = './datasets/db2_weekwise_cae.csv'
weekdf = pd.read_csv(weekfile)
data_tweet = weekdf[tweet_attr].values/7
data_pron = np.array([ [row[0]+row[1]+row[2] , row[3]+row[4]] for row in weekdf[prons].values])
data_behave_liwc = weekdf[behave+liwc_cat+replies+past_tweets].values
data_x = np.append(np.append(data_tweet,data_pron,axis=1),data_behave_liwc,axis=1)
data_y = weekdf['label']

print('Dnn:')
model,scores,cm = make_dnn(data_x,data_y,3)
print(cm)
print('SVM:')
model,scores,cm = make_svm(data_x,data_y)
print(cm)

print('Day wise:')
daydf = pd.read_csv(dayfile)
data_tweet = daydf[tweet_attr].values/7
data_pron = np.array([ [row[0]+row[1]+row[2] , row[3]+row[4]] for row in daydf[prons].values])
data_behave_liwc = daydf[behave+liwc_cat+replies+past_tweets].values
data_x = np.append(np.append(data_tweet,data_pron,axis=1),data_behave_liwc,axis=1)
data_y = daydf['label']

print('Dnn:')
model,scores,cm = make_dnn(data_x,data_y,3)
print(cm)
print('SVM:')
model,scores,cm = make_svm(data_x,data_y)
print(cm)

exit()
print('Dtree:')
model,_ = make_dtree(data_x,data_y)
data_y_pred = model.predict(data_x)
cm = confusion_matrix(data_y,data_y_pred,[1,-1,0])
print(cm)
print('KNN:')
model,_ = make_knn(data_x,data_y)
data_y_pred = model.predict(data_x)
cm = confusion_matrix(data_y,data_y_pred,[1,-1,0])
print(cm)
print('Lr')
model,_ = make_lr(data_x,data_y)
data_y_pred = model.predict(data_x)
cm = confusion_matrix(data_y,data_y_pred,[1,-1,0])
print(cm)
print('svm')
model,_,_ = make_svm(data_x,data_y)
data_y_pred = model.predict(data_x)
cm = confusion_matrix(data_y,data_y_pred,[1,-1,0])
print(cm)
