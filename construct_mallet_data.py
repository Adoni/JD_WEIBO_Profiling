from settings import MATRIXES_DIR
from data_generator import get_y
from my_progress_bar import progress_bar
from helper import balance
import random
import numpy

def split_train_test(data,train_ration):
    train=[]
    test=[]
    for d in data:
        if random.random()<train_ration:
            train.append(d)
        else:
            test.append(d)
    return train,test

def convert_to_mallet_format(name):
    light_list=[
            'jd_user_simple',
            'jd_review_simple'
            ]
    if name in light_list:
        x=[line[:-1].replace(':',' ') for line in open(MATRIXES_DIR+name+'/x.matrix')]
        x=x[1:]
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
<<<<<<< HEAD
=======
    train,test=split_train_test(data,train_ration=0.8)
    output_date_set(train,'review_train')
    output_date_set(test,'review_test')

def convert_to_mallet_format_with_filter(name):
    light_list=[
            'jd_user_simple',
            'jd_review_simple'
            ]
    if name in light_list:
        x=[map(lambda l:l.split(':'),line[:-1].split(' ')) for line in open(MATRIXES_DIR+name+'/x.matrix')]
        dimention=int(x[0][0][0])
        x=x[1:]
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
    train,test=split_train_test(data,train_ration=0.8)
    train_keys=[]
    for d in train:
        for c in d[1]:
            train_keys.append(c[0])
    train_keys=set(train_keys)
    print len(train_keys)
    for i in xrange(len(test)):
        for c in test[i][1]:
            if c[0] not in train_keys:
                test[i][1].remove(c)
    output_date_set(train,'review_train',dimention=dimention)
    output_date_set(test,'review_test')

def output_date_set(data,name='data',dimention=-1):
>>>>>>> f82e8d5f92eb2574d9101b29d7d69ce90d10ebc1
    fout=open(MATRIXES_DIR+'mallet/%s.mallet'%name,'w')
    bar=progress_bar(len(data))
    for index,d in enumerate(data):
        #fout.write('%d %s\n'%(d[2],d[1]))
        if d[1]==[]:
            continue
        s=' '.join(map(lambda c:'%s %s'%(c[0],c[1]),d[1]))
        if random.random()<1.5:
            if dimention>0:
                if d[2]==0:
                    s+=' %d 9'%dimention
                else:
                    s+=' %d 9'%(dimention+1)
        fout.write('%s %d %s\n'%(d[0],d[2],s))
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
<<<<<<< HEAD
    convert_to_mallet_format('jd_user_simple')
    #convert_to_mallet_format('jd_review_simple')
=======
    #convert_to_mallet_format('jd_user_simple')
    #convert_to_mallet_format('jd_review_simple')
    convert_to_mallet_format_with_filter('jd_review_simple')
>>>>>>> f82e8d5f92eb2574d9101b29d7d69ce90d10ebc1
    #construct_mallet_data('gender')
