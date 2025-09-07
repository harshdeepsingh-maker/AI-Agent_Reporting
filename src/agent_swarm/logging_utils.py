import json,datetime,sys

def log(level,msg,**kw):
    print(json.dumps({'ts':datetime.datetime.utcnow().isoformat()+'Z','level':level,'msg':msg,**kw}))
    sys.stdout.flush()

def info(m,**k):log('info',m,**k)

def warn(m,**k):log('warn',m,**k)

def error(m,**k):log('error',m,**k)
