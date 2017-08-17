import sys
import getopt
import json
import re
from db.dbexport import dbexport
from db.dbimport import dbimport
from utils import utils
from utils.utils import FileUtils


def parseopt(argv):
    dbserv    = 1
    inputfile = ''
    table     = ''
    action    = ''
    uptime    = 0

    try:
        opts, args = getopt.getopt(argv,"hi:d:t:a:m:",["ifile=","db=","table=","action="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-d", "--db"):
            dbserv    = int(arg)
        elif opt in ("-t", "--table"):
            table     = arg
        elif opt in ("-a", "--action"):
            action    = arg
        elif opt in ("-m", "--time"):
            uptime    = int(arg)

    return[dbserv, inputfile, table, action, uptime]


def replace(db,table,action,inputfile):
    if table == 'guping':
        jout = db.parseGP(inputfile)
        db.import2db(table,action,jout)
    if table == 'tb_dtboard_raw':
        jout = db.parseDT(inputfile)
        db.import2db(table,action,jout)
    if table == 'tb_dapan_bd_day_list':
        jout = db.parseDapan(inputfile)
        db.import2db(table,action,jout)
    if table == 'tb_dapan_bd_day_feature_list':
        jout = db.parseFT(inputfile)
        db.import2db(table,action,jout)
    if table == 'gubaeast':
        outdir = '.'
        fs = utils.FileUtils(inputfile,'gubastats',outdir)
        fs.loadones()
        paths = fs.loadfiles()
        for p in paths:
            tmp = p.split('/')
            code = tmp[-3]
            year = tmp[-2]
            ymd  = tmp[-1][:-4]
            jout = [] 
            for j in db.loadata(p):
                j['authorlist'] = re.sub('\'','','\001'.join(j['authorlist']))
                j['views'] = str(j['views'])
                j['threads'] = str(j['threads'])
                j['replies'] = str(j['replies'])
                j['opinion'] = str(j['opinion'])
                j['nviews'] = str(j['nviews'])
                j['nreplies'] = str(j['nreplies'])
                jout.append(json.dumps(j))

            db.import2db(table,action,jout)
            fs.donedict[code + '/' + year + '/' + ymd + '.done']  =  code + '/' + year 
        fs.doneflag()


def main(argv):
    [dbserv, inputfile, table, action, uptime] = parseopt(argv)
    if action == 'replace':
        db = dbimport(dbserv, uptime)
        replace(db, table, action, inputfile)
        
    if action == 'fetchall':
        db = dbexport()
        db.fetchAll()

    if action == 'fetchdt':
        db = dbexport()
        db.fetchdtboard()

    if action == 'fetchdtrade':
        db = dbexport()
        db.fetchDtrade()

    if action == 'fetchinfo':
        db = dbexport()
        db.fetchStockInfo()

    if action == 'fetchyd':
        db = dbexport()
        db.fetchyd()

    if action == 'fetchindex':
        db = dbexport()
        db.fetchIndex()

    if action == 'fetchfinance':
        db = dbexport()
        db.fetchfinance()

    if action == 'stockid':
        db = dbexport()
        db.fetchStockID()

if __name__ == "__main__":
    
    main(sys.argv[1:])


#
