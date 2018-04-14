from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import cross_val_score
import datetime as dt
import numpy as np
import joblib
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn import tree
first_field = lambda row:row[0]
cur_time = lambda : str(dt.datetime.now()).replace(':','_')
get_data = lambda file_name: np.loadtxt(file_name,skiprows=1,delimiter=',')
# make_cae_from_file = lambda file_name,save_to: make_cae(get_data(file_name),save_to)
# make_tweetwise_cnn_from_file = lambda file_name,save_to: make_tweetwise_cnn(get_data(file_name)[:-3],get_data(file_name)[-3:],save_to)
mean_pool= lambda matrix: np.mean(matrix,axis=0)

def labelof(pos, neg, neu):
    if pos == 0 and neg == 0:
        return 0
    if pos > neg:
        return 1
    if neg >= pos:
        return -1
    return 0

def make_tweetwise_format(cae_data_x, train_data_x, train_data_y):
    assert len(cae_data_x) == len(train_data_x) and len(train_data_x) == len(train_data_y)
    cae_data_x = sorted(cae_data_x,key=first_field)
    train_data_x = sorted(train_data_x,key= first_field)
    train_data_y = sorted(train_data_y,key= first_field)
    data_x = list()
    data_y = list()
    data_id = list()
    for i in range(len(cae_data_x)):
        assert cae_data_x[i][0] == train_data_x[i][0] and cae_data_x[i][0] == train_data_y[i][0]
        data_x.append(cae_data_x[i][1:]+train_data_x[i][1:])
        try:
            data_y.append(1 if int(train_data_y[i][1])==1 else (-1 if int(train_data_y[i][2])==1 else (0 if int(train_data_y[i][3])==1 else 2)))
        except ValueError:
            data_y.append(2)
        data_id.append(cae_data_x[i][0])
    return data_x, data_y, data_id

def make_cae(train_data,save_to='./models/cae_model.cnn'):
    print('Data shape:',np.shape(train_data)) 
    cae_model = MLPRegressor(hidden_layer_sizes=(1,),activation='logistic',solver='sgd', max_iter=10000)
    cae_model.fit(train_data,train_data)
    print('training info:',cae_model.n_iter_,cae_model.loss_)
    if save_to is not None:
        joblib.dump(cae_model,save_to)
    return cae_model

def make_model(train_data_x, train_data_y, mlpmodel, save_to=None, cross_val=5):
    print('data shape:',np.shape(train_data_x),np.shape(train_data_y))
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    model = OneVsRestClassifier(mlpmodel)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores:',scores)
        print('mean score:',np.mean(scores))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model, scores
from sklearn.neighbors import KNeighborsClassifier

def make_knn(train_data_x, train_data_y, save_to=None, cross_val=5):
    print('data shape:',np.shape(train_data_x),np.shape(train_data_y))
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    model = KNeighborsClassifier()
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores:',scores)
        print('mean score:',np.mean(scores))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model, scores

def make_dnn(train_data_x, train_data_y, save_to=None, cross_val=5):
    print('data shape:',np.shape(train_data_x),np.shape(train_data_y))
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    mlpmodel = MLPClassifier(hidden_layer_sizes=(np.shape(train_data_x)[1],),activation='logistic',solver='sgd',max_iter=10000)
    model = OneVsRestClassifier(mlpmodel)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores:',scores)
        print('mean score:',np.mean(scores))
        # model.fit(train_data_x[:int(len(train_data_x)*7/10)],train_data_y[:int(len(train_data_x)*7/10)])
        # for mod in model.estimators_:
        #     print('training info:',mod.n_iter_,mod.loss_)
        # print('accuracy:',model.score(np.array(train_data_x[int(len(train_data_x)*7/10):]),np.array(train_data_y[int(len(train_data_x)*7/10):])))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model, scores
def make_svm(train_data_x, train_data_y, save_to = None, cross_val=5):
    print('data shape:',np.shape(train_data_x),np.shape(train_data_y))
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    mlpmodel = svm.SVC()
    model = OneVsRestClassifier(mlpmodel)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores:',scores)
        print('mean score:',np.mean(scores))
        # model.fit(train_data_x[:int(len(train_data_x)*7/10)],train_data_y[:int(len(train_data_x)*7/10)])
        # for mod in model.estimators_:
        #     print('training info:',mod.n_iter_,mod.loss_)
        # print('accuracy:',model.score(np.array(train_data_x[int(len(train_data_x)*7/10):]),np.array(train_data_y[int(len(train_data_x)*7/10):])))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model, scores

def make_lr(train_data_x, train_data_y, save_to = None, cross_val=5):
    print('data shape:',np.shape(train_data_x),np.shape(train_data_y))
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    mlpmodel = LogisticRegression()
    model = OneVsRestClassifier(mlpmodel)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores:',scores)
        print('mean score:',np.mean(scores))
        # model.fit(train_data_x[:int(len(train_data_x)*7/10)],train_data_y[:int(len(train_data_x)*7/10)])
        # for mod in model.estimators_:
        #     print('training info:',mod.n_iter_,mod.loss_)
        # print('accuracy:',model.score(np.array(train_data_x[int(len(train_data_x)*7/10):]),np.array(train_data_y[int(len(train_data_x)*7/10):])))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model, scores
def make_dtree(train_data_x, train_data_y, save_to = None, cross_val=5):
    print('data shape:',np.shape(train_data_x),np.shape(train_data_y))
    assert np.shape(train_data_x)[0] == np.shape(train_data_y)[0]
    mlpmodel = tree.DecisionTreeClassifier()
    model = OneVsRestClassifier(mlpmodel)
    if cross_val > 0 and cross_val <=10:
        scores = cross_val_score(model, train_data_x, train_data_y, cv=cross_val)
        print('scores:',scores)
        print('mean score:',np.mean(scores))
        # model.fit(train_data_x[:int(len(train_data_x)*7/10)],train_data_y[:int(len(train_data_x)*7/10)])
        # for mod in model.estimators_:
        #     print('training info:',mod.n_iter_,mod.loss_)
        # print('accuracy:',model.score(np.array(train_data_x[int(len(train_data_x)*7/10):]),np.array(train_data_y[int(len(train_data_x)*7/10):])))
    model.fit(train_data_x,train_data_y)
    if save_to is not None:
        joblib.dump(model,save_to)
    return model,scores

def fill_modalities(data_body, cae_model):
    """
        'data_body' data with out header
    """
    data_body = sorted(data_body,key=lambda row:row[0])

    ids_list = list()
    input_data = list()
    for row in data_body:
        ids_list.append(row[0])
        input_data.append(row[1:])
    result_data = cae_model.predict(input_data)
    processed_data = list()
    for i in range(len(result_data)):
        processed_data.append([ids_list[i]]+list(result_data[i]))
    return processed_data
