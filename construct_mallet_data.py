from settings import MATRIXES_DIR
from data_generator import get_y
from helper import balance
import numpy
def construct(name):
    x=numpy.loadtxt(MATRIXES_DIR+name+'/x.matrix')
    uids=map(lambda line:line[:-1],open(MATRIXES_DIR+name+'/uids.vector'))
    all_y=get_y('gender')
    y=map(lambda uid:all_y[uid],uids)
    data=zip(uids,x,y)
    data=filter(lambda d:not d[2]==-1, data)
    data=balance(data,target_index=2)
    fout=open(MATRIXES_DIR+'mallet/data.mallet','w')
    for d in data:
        #fout.write('%s %d'%(d[0],d[2]))
        fout.write(str(d[2]))
        for index,value in enumerate(d[1]):
            fout.write(' %d:%0.8f'%(index,value))
        fout.write('\n')


if __name__=='__main__':
    construct('jd_user_simple')
