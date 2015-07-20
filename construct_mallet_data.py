from settings import MATRIXES_DIR
from data_generator import get_y
from helper import balance
import numpy

def convert_to_mallet_format(name):
    from my_progress_bar import progress_bar
    light_list=[
            'jd_user_simple',
            'jd_review_simple'
            ]
    if name in light_list:
        x=map(lambda line:''+line[:-1].replace(' ',' '),open(MATRIXES_DIR+name+'/x.matrix'))
    else:
        x=numpy.loadtxt(MATRIXES_DIR+name+'/x.matrix')
    uids=map(lambda line:line[:-1],open(MATRIXES_DIR+name+'/uids.vector'))
    print 'Try to get y'
    all_y=get_y('gender')
    y=map(lambda uid:all_y[uid],uids)
    print 'Get y done'
    data=zip(uids,x,y)
    data=filter(lambda d:not d[2]==-1, data)
    data=balance(data,target_index=2)
    fout=open(MATRIXES_DIR+'mallet/%s.mallet'%name,'w')
    bar=progress_bar(len(data))
    for index,d in enumerate(data):
        fout.write('%s %d %s\n'%(d[0],d[2],d[1]))
        bar.draw(index)


def construct_mallet_data(profile_key):
    from pymongo import Connection
    from my_progress_bar import progress_bar
    from collections import Counter
    users=Connection().jd.weibo_users
    bar=progress_bar(users.count())
    fout=open(MATRIXES_DIR+'mallet/construced_data.mallet','w')
    data=[]
    for index,user in enumerate(users.find()):
        try:
            label=user['profile'][profile_key].index(1)
        except:
            continue
        reviews=[]
        for behavior in user['behaviors']:
            #reviews.append('Pro'+str(behavior['item']))
            reviews+=behavior['parsed_review']['review_general']
        reviews=Counter(reviews)
        reviews=' '.join(map(lambda word:'%s:%d'%(word,reviews[word]),reviews.keys()))
        line='%s %d %s\n'%(user['_id'],label,reviews)
        data.append((label,line))
    data=balance(data,target_index=0)
    #balanced_data=data
    for label,line in balanced_data:
        fout.write(line.encode('utf8'))
        bar.draw(index)


if __name__=='__main__':
    convert_to_mallet_format('jd_user_simple')
    #convert_to_mallet_format('jd_review_simple')
    #construct_mallet_data('gender')
