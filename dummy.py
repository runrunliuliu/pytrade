
for line in open('tmp.tmp'):
    line = line.strip()
    tmp = line.split(',')
    # if float(tmp[4]) < -0.0:
    if float(tmp[4]) > 0.0:
        code = tmp[2]
        fname = 'data/dayk/mtime/' + code + '.cxshort.csv'
        xingtai = []
        for l2 in open(fname):
            arr = l2.strip().split(',')
            if len(xingtai) == 0:
                xingtai.append(arr[9])
            else:
                if xingtai[-1] != arr[9]:
                    xingtai.append(arr[9])
            if arr[0] == tmp[0]:
                # print line, arr[0], arr[9], xingtai[-3:]
                print ','.join(xingtai[-2:])
