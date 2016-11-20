# coding:utf-8
from ml.merge import Merge 
from ml.fteng import FTeng 
import ml.utils as mutils
import sys
import xgboost as xgb
import numpy as np
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import classification_report 
import pandas as pd
from sklearn.grid_search import GridSearchCV


def train(path, code):

    trainfile = path + '/' + code + '.train.csv'
    testfile  = path + '/' + code + '.test.csv'

    xg_train = xgb.DMatrix(trainfile, missing=1024201)
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
    param['eta']               = 0.1
    num_round                  = 500 
    param['subsample']         = 1.0 
    param['colsample_bytree']  = 0.7
    param['colsample_bylevel'] = 1.0 
    param['alpha']            = 1 
    param['max_depth']        = 500 
    param['silent']           = 0 
    param['nthread']          = 1 
    param['num_class']        = 3 
    param['min_child_weight'] = 1 
    
    watchlist = [(xg_train,'train'), (xg_test, 'test')]
    test_Y = xg_test.get_label()

    # do the same thing again, but output probabilities
    param['objective'] = 'multi:softprob'
    bst = xgb.train(param, xg_train, num_round, watchlist, )
    # Note: this convention has been changed since xgboost-unity
    # get prediction, this is in 1D array, need reshape to (ndata, nclass)
    yprob = bst.predict(xg_test)
    ylabel = np.argmax(yprob, axis=1)

    # PredictDebug(path, code, bst)
   
    print confusion_matrix(test_Y, ylabel)

    print classification_report(test_Y, ylabel)
    print ('predicting, classification error=%f' % (sum( int(ylabel[i]) != test_Y[i] for i in range(len(test_Y))) / float(len(test_Y)) ))

    # Feature Importance Show
    mutils.featureImportance(path, code, bst)
    # mutils.showTree(bst)


def PredictDebug(odir, code, bst):
    test_pred  = open(odir + '/' + code + '.test.pred.csv', 'w')
    test_debug = odir + '/' + code + '.test.csv.debug'
    xg_testd = xgb.DMatrix(test_debug)

    yprob  = bst.predict(xg_testd)
    ylabel = np.argmax(yprob, axis=1)

    test_Y = xg_testd.get_label()

    nylabel = []
    ntest_Y = []
    yzhi  = 0.71

    test_pred.write('day,true,predict\n')
    for i in range(0, len(yprob)):
        tmp     = str(int(test_Y[i]))
        day     = tmp[0:-1]
        label   = tmp[-1:]
        prob    = yprob[i]
        plabel  = ylabel[i]
        nplabel = plabel

        if prob[0] < yzhi and prob[1] < yzhi:
            nplabel = 2

        test_pred.write(day + ',' + str(label) + ',' + str(plabel) + ',' + str(nplabel))
        test_pred.write('\n')

        nylabel.append(int(label))
        ntest_Y.append(nplabel)

    test_pred.close()

    print confusion_matrix(ntest_Y, nylabel)
    print classification_report(ntest_Y, nylabel)


# Main
def main(plot, argv):

    code = 'ZS000001'
    odir = './output/fts'

    # Load Data
    mg = Merge(code, './data/', odir)
    mg.combFeatures()

    # Feature Engineering
    startday = '2001-01-03'
    ft = FTeng(odir, code, startday)
    ft.dumpft()

    # Data Split
    splitday = '2016-01-01'
    mutils.datasplit(code, odir, splitday)

    train(odir, code)

if __name__ == "__main__":
    main(True, sys.argv[1:])
