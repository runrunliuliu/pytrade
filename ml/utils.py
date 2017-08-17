# coding:utf-8
import datetime
import re
import numpy as np
from datetime import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
from xgboost import plot_tree
import xgboost as xgb
import operator


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

    # Write Weight
    wtrain = open(path + '/' + code + '.train.csv.weight', 'w')
    wtest  = open(path + '/' + code + '.test.csv.weight', 'w')

    sday = dt.strptime(splitDay, "%Y-%m-%d")
    for line in open(path + '/' + code + '.raw.csv.weight'):
        arr = line.strip().split(',')
        cday = dt.strptime(arr[0], "%Y-%m-%d")
        if cday < sday:
            wtrain.write(arr[1] + '\n')
        else:
            wtest.write(arr[1] + '\n')
    wtrain.close()
    wtest.close()

    # For DEBUG
    ftest_d  = open(path + '/' + code + '.test.csv.debug', 'w')
    ftest_i  = open(path + '/' + code + '.test.csv.index', 'w')
    sday     = dt.strptime(splitDay, "%Y-%m-%d")
    linenum  = 0
    for line in open(path + '/' + code + '.raw.csv.debug'):
        arr = line.strip().split(',')
        cday = dt.strptime(arr[0], "%Y-%m-%d")
        if cday >= sday:
            # tmpday = cday.strftime('%m%d')
            tmpday = cday.strftime('%Y%m%d')
            ftest_d.write(str(linenum) + arr[1] + '\n')
            ftest_i.write(str(linenum) + arr[1].split(' ')[0] + ',' + tmpday + '\n')

            linenum = linenum + 1
    ftest_d.close()
    ftest_i.close()

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


def loadWeight(filename):
    weights = []
    for line in open(filename + '.weight'):
        w = float(line.strip())
        weights.append(w)
    return weights


def loadFtDict(path, code):
    fts    = []
    ftname = dict()
    ftdesc = dict()
    for line in open(path + '/' + code + '.ft.dict'):
        arr = line.strip().split(',')
        ftname['f' + arr[0]] = arr[1]
        fts.append(arr[0])

    for line in open('./conf/ft.dictname'):
        arr = line.strip().split(',')
        ftdesc[arr[0]] = arr[1]

    return (fts, ftname, ftdesc)


def featureImportance(path, code, bst):
    (fts, ftname, ftdesc) = loadFtDict(path, code)
    (ax, tuples)  = xgb.plot_importance(bst, importance_type="gain", ftname=ftname)
    plt.savefig('importance.png')

    f = open(path + '/' + code + '.ft.score.csv', 'w')
    for i in range(1, len(tuples) + 1):
        find  = tuples[-1 * i][0]
        score = tuples[-1 * i][1]
        fname = ftname[find]
        fdesc = ftdesc[fname]
        f.write(str(find) + ',' + fname + ',' + fdesc + ',' + str(score) + '\n')
    f.close()

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


def forwardCheck(mkey, for_map, dicts):
    used = set()
    arr  = []
    for i in range(1, 4):
        key = mkey + i
        if key < len(for_map) and for_map[key] in dicts:
            if for_map[key] in used:
                continue
            else:
                used.add(for_map[key])
                arr.append((for_map[key], i))
    if len(used) > 0:
        return arr 
    else:
        return None 


def showTree(bst, ntree):
    xgb.plot_tree(bst, num_trees=ntree, fontsize='24', rankdir='LR', size="7.75,10.25")
    plt.savefig('tree.png')


def debugTree(bst, xg_test, index):
    linenum = 0
    debugTree = bst.predict(xg_test, pred_leaf=True)
    #nsample = debugTree.shape[0]
    nsample = index + 1 

    _NODEPAT = re.compile(r'(\d+):\[(.+)\]')
    _LEAFPAT = re.compile(r'(\d+):(leaf=.+)')
    _EDGEPAT = re.compile(r'yes=(\d+),no=(\d+),missing=(\d+)')
    # _EDGEPAT = re.compile(r'yes=(\d+),no=(\d+),missing=(\d+),gain=(\d+.\d+)')
    # _EDGEPAT2 = re.compile(r'yes=(\d+),no=(\d+)')

    arrNodes = []
    arrEdges = []
    leafdict = dict()

    def _parse_node(text):
        match = _NODEPAT.match(text)
        if match is not None:
            node = match.group(1)
            # print 'Node:', node, text
            arrNodes.append(text)
        match = _LEAFPAT.match(text)
        if match is not None:
            node = match.group(1)
            # print 'Leaf:', node, text
            leafdict[node] = text

    def travelTree(leafnode):
        nids  = set()
        dnode = dict()
        dnode['0'] = 'ROOT' 
        for i in range(0, len(arrNodes)):
            (yes, no, missing) = arrEdges[i]
            nd                 = arrNodes[i]

            arch_Y = '|Y|'
            if yes == missing:
                arch_Y = '|Y|M|'
            arch_N = '|N|'
            if no == missing:
                arch_N = '|N|M|'
 
            dnode[yes] = nd + arch_Y
            dnode[no] = nd + arch_N

            nids.add(yes)
            nids.add(no)
        output = ''
        ntext = dnode[leafnode]
        pid   = ntext.split(':')[0]
        nodes = [] 
        while 1:
            output = ntext + '-->' + output
            if pid == '0':
                break
            ntext = dnode[pid] 
            pid   = ntext.split(':')[0]
            nodes.append(ntext.split(':')[1])
        ldesc = leafdict[leafnode]
        return (output + 'Leaf_' + ldesc, ldesc.split("=")[1], nodes)

    for d in debugTree:
        linenum = linenum + 1
        if linenum == nsample:
            score = []
            fposdict = dict()
            fnegdict = dict()
            negnodes = dict()
            posnodes = dict()
            for i in range(0, len(d)):
                if i % 2 == 1:
                    continue
                tree = bst.get_dump(with_stats=False)[i].split()
                for k, text in enumerate(tree):
                    if text[0].isdigit():
                        _parse_node(text) 
                    else:
                        if k == 0:
                            raise ValueError('Unable to parse given string as tree')
                        match = _EDGEPAT.match(text)
                        if match is not None:
                            yes, no, missing = match.groups()
                        arrEdges.append((yes, no, missing))
                (desc, lscore, nodes) = travelTree(str(d[i]))
                def add2nodes(nodes, dictnodes, score, fdict):
                    for n in nodes:
                        cnt = 1
                        if n in dictnodes:
                            cnt = dictnodes[n] + 1
                        dictnodes[n] = cnt

                        tscore = 0.0
                        findex = n.split('<')[0][1:]
                        if findex in fdict:
                            tscore = fdict[findex]
                        tscore = tscore + score
                        fdict[findex] = tscore

                if float(lscore) > 0:
                    add2nodes(nodes, posnodes, float(lscore), fposdict)
                if float(lscore) < 0:
                    add2nodes(nodes, negnodes, float(lscore), fnegdict)

                score.append(float(lscore))

            # Positive Score means BAODIE
            # flag 1,  偏多
            # flag 0,  中性
            # flag -1, 偏空
            ft_flag = dict()
            for k, v in fposdict.iteritems():
                if k in fnegdict:
                    flag  = 0
                    ratio = abs(fnegdict[k]) / v
                    if ratio > 1.2:
                        flag = 1
                    if ratio < 0.8: 
                        flag = -1
                    if ratio >=0.8 and ratio<= 1.2:
                        flag = 0
                    ft_flag[k] = flag 
            return ft_flag
            break
#
