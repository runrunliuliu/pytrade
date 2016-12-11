# coding:utf-8
import sys
import getopt
import re
from ml.merge import Merge 
from ml.fteng import FTeng 
import ml.utils as mutils
import xgboost as xgb
import numpy as np
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import classification_report 
import pandas as pd
from sklearn.grid_search import GridSearchCV
from numpy import loadtxt


def train(path, code):

    trainfile = path + '/' + code + '.train.csv'
    testfile  = path + '/' + code + '.test.csv'

    tweights = mutils.loadWeight(trainfile)

    xg_train = xgb.DMatrix(trainfile, missing=1024201, weight=tweights)
    xg_test = xgb.DMatrix(testfile)

    # CV
    # param = {'max_depth':2, 'eta':1, 'silent':1, \
    #          'objective':'multi:softprob', 'alpha':1, \
    #          'num_class':2}

    # res = xgb.cv(param, xg_train, num_round, nfold=5,\
    #              metrics={'merror'}, seed = 1,\
    #              callbacks=[xgb.callback.print_evaluation(show_stdv=True)])

    # Grid Searh
    # train_pd = path + '/' + code + '.train.pd.csv'
    # train = pd.read_csv(train_pd)

    # parameters = {
    #     'nthread':[4],
    #     'learning_rate': [0.1,0.15,0.2],
    #     'max_depth': [10,20,50,100,200,300],
    #     'min_child_weight': [3,11],
    #     'silent': [1],
    #     'subsample': [0.9],
    #     'colsample_bytree': [0.5],
    #     'n_estimators': [300],
    #     'seed': [1337]
    # }
    # xgb_model = xgb.XGBClassifier(objective="multi:softprob")

    # clf = GridSearchCV(xgb_model, parameters, n_jobs=4, verbose=2, refit=True)
    # clf.fit(train[train.columns[1:]], train["0"])

    # best_parameters, score, _ = max(clf.grid_scores_, key=lambda x: x[1])
    # print('Raw AUC score:', score)
    # for param_name in sorted(best_parameters.keys()):
    #         print("%s: %r" % (param_name, best_parameters[param_name]))

    # # setup parameters for xgboost
    param = {}
    # use softmax multi-class classification
    # scale weight of positive examples
    param['eta']               = 0.10
    num_round                  = 100
    param['subsample']         = 1.0
    param['colsample_bytree']  = 0.7 
    param['colsample_bylevel'] = 0.8 
    param['alpha']            = 2
    param['max_depth']        = 200
    param['silent']           = 0
    param['nthread']          = 1
    param['num_class']        = 2
    param['min_child_weight'] = 1
    predict_threshold         = 0.50
    
    watchlist = [(xg_train,'train'), (xg_test, 'test')]
    test_Y = xg_test.get_label()

    # do the same thing again, but output probabilities
    param['objective'] = 'multi:softprob'
    bst = xgb.train(param, xg_train, num_round, watchlist, )
    # # Note: this convention has been changed since xgboost-unity
    # # get prediction, this is in 1D array, need reshape to (ndata, nclass)
    yprob  = bst.predict(xg_test)
    ylabel = np.argmax(yprob, axis=1)

    PredictDebug(path, code, bst, predict_threshold)
   
    print confusion_matrix(test_Y, ylabel)

    print classification_report(test_Y, ylabel)
    print ('predicting, classification error=%f' % (sum( int(ylabel[i]) != test_Y[i] for i in range(len(test_Y))) / float(len(test_Y)) ))

    # Feature Importance Show
    mutils.featureImportance(path, code, bst)

    # mutils.showTree(bst, 0)
    # print bst.get_dump(with_stats=True)
    # print bst.get_split_value_histogram('f46')

    # ------------------------- DEBUG ---------------------------- #
    # mutils.debugTree(bst, xg_test)
    bst.save_model('output/models/' + code + '.model')


def PredictDebug(odir, code, bst, threshold):
    key_value = loadtxt(odir + '/' + code + '.actday.csv', delimiter=",")
    actdays   = { int(k):float(v) for k,v in key_value }

    key_value = loadtxt(odir + '/' + code + '.test.csv.index', delimiter=",")
    test_ind  = { int(k):int(v) for k,v in key_value }
    indexdays = [ int(v) for k,v in key_value ] 
    dictdays  = { v[0]:v[1] for v in zip(indexdays, range(0, len(indexdays))) }

    test_pred  = open(odir + '/' + code + '.test.pred.csv', 'w')
    test_debug = odir + '/' + code + '.test.csv.debug'

    xg_testd = xgb.DMatrix(test_debug)
    yprob  = bst.predict(xg_testd)
    ylabel = np.argmax(yprob, axis=1)
    test_Y = xg_testd.get_label()

    nylabel = []
    ntest_Y = []

    bd_Y       = [] 
    match_pred = [] 

    test_pred.write('day,true,predict,npredict\n')
    for i in range(0, len(yprob)):
        tmp     = str(int(test_Y[i]))
        index   = tmp[0:-1]

        test_day = test_ind[int(tmp)] 
       
        # START STATISTIC
        label   = tmp[-1:]
        plabel  = ylabel[i]
        nplabel = plabel

        if yprob[i][0] < threshold and yprob[i][1] < 0.5:
            nplabel = 2

        if test_day < 20160301:
            print 'DEBUG_Predict: ignore:', tmp, index, test_day
        else:
            if test_day in actdays:
                bd_Y.append(test_day)
            if nplabel == 0:
                tmatch = mutils.forwardCheck(dictdays[test_day], indexdays, actdays)
                if tmatch is not None:
                    match_pred.append((test_day, tmatch))

        test_pred.write(str(test_day) + ',' + str(label) + ',' + str(plabel) + ',' + str(nplabel))
        
        test_pred.write('\n')

        nylabel.append(int(label))
        ntest_Y.append(nplabel)
    test_pred.close()

    ddays = set()
    for m in match_pred:
        for k in m[1]:
            print m[0], k[0], k[1]
            ddays.add(k[0])
    miss_bd = 0
    for bd in bd_Y:
        if bd not in ddays:
            print 'MISS:', bd
            miss_bd = miss_bd + 1
    print 'MISS_RATE:', miss_bd / (len(ddays) + 0.0)

    print confusion_matrix(nylabel, ntest_Y)
    print classification_report(nylabel, ntest_Y)


def predict(path, code):
    key_value = loadtxt(path + '/' + code + '.test.csv.index', delimiter=",")
    test_ind  = { int(k):int(v) for k,v in key_value }

    test_debug = path + '/' + code + '.test.csv.debug'
    xg_testd = xgb.DMatrix(test_debug)
    bst = xgb.Booster({'nthread':4})
    bst.load_model("output/models/" + code + '.model')
    yprob  = bst.predict(xg_testd)
    ylabel = np.argmax(yprob, axis=1)
    test_Y = xg_testd.get_label()
    
    for i in range(0, len(yprob)):
        tmp     = str(int(test_Y[i]))
        test_day = test_ind[int(tmp)] 
        plabel  = ylabel[i]
        print test_day, plabel, yprob[i][plabel]


# Main
def main(plot, argv):
    mode = ''
    try:
        opts, args = getopt.getopt(argv,"h:m:",["mode="])
    except getopt.GetoptError:
        print 'test.py -d <time>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -t <time> -o <outputfile>'
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg

    code = 'ZS000001'
    odir = './output/fts'

    # Load Data
    mg = Merge(code, './data/', odir)
    mg.combFeatures()

    # Feature Engineering
    startday = '2001-01-01'
    ft = FTeng(odir, code, startday)
    ft.dumpft()

    # Data Split
    splitday = '2016-01-01'
    mutils.datasplit(code, odir, splitday)

    if mode == 'train':
        train(odir, code)
    if mode == 'predict':
        predict(odir, code)


if __name__ == "__main__":
    main(True, sys.argv[1:])
