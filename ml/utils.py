import datetime
import numpy as np
from datetime import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
from xgboost import plot_tree
import xgboost as xgb


# Sample Data
def datasplit(code, path, splitDay):

    # LibSVM
    ftrain = open(path + '/' + code + '.train.csv', 'w')
    ftest  = open(path + '/' + code + '.test.csv', 'w')

    sday = dt.strptime(splitDay, "%Y-%m-%d")
    for line in open(path + '/' + code + '.raw.csv'):
        arr = line.strip().split(',')
        cday = dt.strptime(arr[0], "%Y-%m-%d")
        if cday < sday:
            ftrain.write(arr[1] + '\n')
        else:
            ftest.write(arr[1] + '\n')
    ftrain.close()
    ftest.close()

    ftest_d  = open(path + '/' + code + '.test.csv.debug', 'w')
    sday = dt.strptime(splitDay, "%Y-%m-%d")
    for line in open(path + '/' + code + '.raw.csv.debug'):
        arr = line.strip().split(',')
        cday = dt.strptime(arr[0], "%Y-%m-%d")
        if cday >= sday:
            tmpday = cday.strftime('%m%d')
            ftest_d.write(tmpday + arr[1] + '\n')
    ftest_d.close()

    # Pandas
    def concat(ft):
        fts = []
        arr = ft.split(" ")
        for i in range(1, len(arr)):
            fts.append(arr[i].split(":")[1])
        return arr[0] + ',' + ','.join(fts)

    ftrain = open(path + '/' + code + '.train.pd.csv', 'w')
    ftest  = open(path + '/' + code + '.test.pd.csv', 'w')

    sday = dt.strptime(splitDay, "%Y-%m-%d")
    cnt  = 0
    for line in open(path + '/' + code + '.raw.csv'):
        arr = line.strip().split(',')
        cday = dt.strptime(arr[0], "%Y-%m-%d")
        if cnt == 0:
            header = ''
            for i in range(1, len(arr[1].split(' '))):
                header = header + ',' + str(i)
            ftrain.write('0' + header + '\n')
            ftest.write('0' + header + '\n')

        if cday < sday:
            ftrain.write(arr[0] + ',' + concat(arr[1]) + '\n')
        else:
            ftest.write(arr[0] + ',' + concat(arr[1]) + '\n')
        cnt = cnt + 1
    ftrain.close()
    ftest.close()


def loadFtDict(path, code):
    fts    = []
    ftname = dict()
    for line in open(path + '/' + code + '.ft.dict'):
        arr = line.strip().split(',')
        ftname[arr[0]] = arr[1]
        fts.append(arr[0])
    return (fts, ftname)


def featureImportance(path, code, bst):
    xgb.plot_importance(bst, importance_type="gain")
    plt.savefig('importance.png')

    # (fts, ftname) = loadFtDict(path, code)
    # ftscore = bst.get_score()
    # arrftname  = []
    # arrftscore = []
    # for i in fts:
    #     key = 'f' + i
    #     if key in ftscore:
    #         arrftname.append(ftname[i])
    #         arrftscore.append(ftscore[key])
    # plt.figure(figsize=(20, 10))
    # plt.barh(range(len(arrftscore)), arrftscore)
    # plt.xlabel("importance")
    # plt.ylabel("features")
    # plt.yticks(np.arange(len(arrftname)) + 0.35, arrftname)
    # plt.show()


def showTree(bst):
    xgb.plot_tree(bst, num_trees=299, fontsize='24', rankdir='LR', size="7.75,10.25")
    plt.savefig('tree.png')
#
