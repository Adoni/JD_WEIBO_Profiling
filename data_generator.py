#coding:utf8
import urllib2
import numpy
import json
import pickle
import sys
from my_progress_bar import progress_bar

access_token = '2.00L9khmFlxpd6C91aec9ef010s3KCc'
word_vector_size=500
time_vector_size=24
GLOBAL_PATH='/mnt/data1/adoni/jd_data/matrixes/'

def save_vector_to_text(vector, file_name, folder):
    import os
    path=GLOBAL_PATH+folder+'/'
    print 'Try to save vector in '+path+file_name
    if not os.path.exists(path):
        os.makedirs(path)
    if type(vector)==list:
        fout=open(path+file_name,'w')
        for item in vector:
            fout.write(str(item)+'\n')
        return
    if type(vector)==numpy.ndarray:
        numpy.savetxt(path+file_name,vector)
        return
    print 'Fail to save vector'
    print 'Vector type should be list or numpy.ndarray'

def load_vector_from_text(file_name, folder, file_type):
    import os
    path=GLOBAL_PATH+folder+'/'
    print 'Try to load vector in '+path+file_name
    if file_type=='list':
        fout=open(path+file_name)
        vector=[line[:-1] for line in open(path+file_name)]
        return vector
    if file_type=='NParray':
        vector=numpy.loadtxt(path+file_name)
        return vector
    print 'Fail to load vector'
    print 'Vector type should be list or numpy.ndarray'
    return None

def get_vectors(file_name):
    print 'Getting vectors...'
    f=open(file_name)
    vectors=dict()
    for line in f:
        line=line
        line=line.split(' ')
        try:
            line.remove('\n')
        except Exception as e:
            pass
        key=line[0]
        vector=[0]*(len(line)-1)
        for i in range(1,len(line)):
            vector[i-1]=float(line[i])
        vectors[key]=numpy.array(vector)
    print 'Done'
    return vectors

def dump_vectors():
    word_vectors=get_vectors('./word_vectors.data')
    print 'dump'
    pickle.dump(word_vectors,open('parameters.bin','wb'))
    print 'dump done'

def get_one_hot_vector(features, feature_map):
    vector=numpy.zeros((max(feature_map.values())+1))
    for f in features:
        try:
            vector[feature_map[f]]+=1.0
        except:
            continue
    if sum(vector)==0.0:
        return vector
    #vector/=sum(vector)
    return vector

def dump_user_vector(x,y,uids,folder):
    print 'DUMP DATA'
    print 'X dimention:'+str(len(x[0]))
    if not len(x)==len(y):
        raise Exception('x not equal with y')
    if not len(x)==len(uids):
        raise Exception('x not equal with uids')
    save_vector_to_text(x,'x.matrix',folder)
    save_vector_to_text(y,'y.vector',folder)
    save_vector_to_text(uids,'uids.vector',folder)
    #pickle.dump((uids,user_vector),open('/mnt/data1/adoni/jd_data/matrixes/'+file_name+'.matrix','wb'))

def dump_train_valid_test(x,y,uids):
    print 'Dump'
    if not len(x)==len(y):
        raise Exception('The size of x is not equel with that of y')

    #数据集平衡
    counts=[0]*(max(y)+1)
    for value in y:
        if value==-1:
            continue
        counts[value]+=1
    print counts
    MAX_COUNT=min(counts)

    #构建平衡数据集
    all_x=[]
    all_y=[]
    all_uids=[]
    counts=[0]*(max(y)+1)
    for i in range(0,len(x)):
        if y[i]==-1:
            continue
        if not numpy.any(x[i]):
            continue
        if counts[y[i]]<MAX_COUNT:
            all_x.append(x[i])
            all_y.append(y[i])
            all_uids.append(uids[i])
            counts[y[i]]+=1
    if not len(all_x)==len(all_y):
        raise Exception('The size of x is not equel with that of y')
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)

    #进行归一化
    b=numpy.max(all_x,axis=0)
    c=numpy.min(all_x,axis=0)
    pickle.dump((b,c),open('./normal','wb'))
    for i in range(all_x.shape[1]):
        if b[i]==c[i]:
            all_x[:,i]=all_x[:,i]-all_x[:,i]
        else:
            all_x[:,i]=(all_x[:,i]-c[i])/(b[i]-c[i])

    print "Items Count: %d"%len(all_x)
    print "Dimention: %d"%len(all_x[0])
    print "Counts: %s"%str(counts)
    return all_uids,all_x,all_y

def get_all_item():
    from pymongo import Connection
    jd_users=Connection().jd.jd_users
    items=dict()
    for user in jd_users.find():
        for behavior in user['bahaviors']:
            try:
                items[behavior['item']]+=1
            except:
                items[behavior['item']]=1
    return items

def get_location_class(location,location_map):
    if location is None:
        return -1
    location=location.split(' ')[0]
    if location in location_map:
        return location_map[location]
    else:
        return -1

def get_age_class(birthday):
    if birthday is None:
        return -1
    if u'年' not in birthday:
        return -1
    age=birthday[0:birthday.find(u'年')]
    if len(age)==2:
        age='19'+age
    age=int(age)
    if age<1990:
        return 0
    else:
        return 1

def get_gender_class(gender):
    if gender==u'男':
        return 1
    if gender==u'女':
        return 0
    return -1

def get_user_embedding(file_name):
    import sys
    import gensim
    from pymongo import Connection

    users=Connection().jd.jd_users
    dimensionality_size=200
    window_size=8
    workers=5
    min_count=5

    # load sentences
    finish_count=0
    total_count=users.find({'got_review':True}).count()
    #total_count=users.count()
    sentences = []
    print total_count
    old_review=''
    for user in users.find({'got_review':True}):
    #for user in users.find():
        if finish_count%10000==0:
            sys.stdout.write("\r%f"%(finish_count*1.0/total_count))
            sys.stdout.flush()
        finish_count+=1
        content=[]
        for behavior in user['behaviors']:
            #content.append(str(behavior['item']))
            #content.append(behavior['item_class'][0])
            review=' '.join(behavior['review']['parsed_review_general'])
            if review==old_review:
                continue
            old_review==review
            content+=review.split()
        for ch in [' ','\n','\r','\u3000']:
            while 1:
                try:
                    content.remove(ch)
                except:
                    break
        #print ' '.join(content)
        if len(content)<10:
            continue
        sentence = gensim.models.doc2vec.LabeledSentence(words=content,labels=['USER_%d'%user['_id']])
        sentences.append(sentence)

    print 'load corpus completed...'

    # train word2vc
    model = gensim.models.Doc2Vec(sentences,size=200,window=7, workers=20,min_count=3,sample=1e-3)
    model.save_word2vec_format('/mnt/data1/adoni/jd_data/vectors/'+file_name+'.data',binary=False)
    print 'embedding done'
    return model

def load_user_embedding(file_name):
    import gensim
    print 'Loading user embedding'
    embedding=gensim.models.Word2Vec.load_word2vec_format('/mnt/data1/adoni/jd_data/'+file_name+'.data',binary=False)
    print 'Done'
    return embedding

def load_graph_embedding(uids,file_name):
    print 'Loading graph embedding'
    #file_name='/mnt/data1/adoni/jd_data/jd_graph_normalize2.data'
    #file_name='/mnt/data1/adoni/jd_data/graph_vectors_from_review.data'
    file_name='/mnt/data1/adoni/jd_data/'+file_name+'.data'#'graph_vectors.data'
    graph_embedding=dict()
    last_index=0
    for index, line in enumerate(open(file_name)):
        if index==0:
            continue
        if index-last_index==10000:
            print index
            last_index=index
        if line[0]=='P':
            continue
        line=line.replace('\n','').replace('\r','').split(' ')
        if line[0] not in uids:
            continue
        if line[-1]=='':
            line=line[:-1]
        for i in range(1,len(line)):
            line[i]=float(line[i])
        graph_embedding[line[0]]=line[1:]
    print 'Loaded graph embedding'
    return graph_embedding

def load_review_words():
    file_name='./review.feature'
    review_words=dict()
    review_words_class=dict()
    total_index=0
    for index, line in enumerate(open(file_name)):
        line=line[:-1].split(':')
        words=line[1]
        for word in words.split(','):
            review_words[word]=total_index
            total_index+=1
            review_words_class[word]=index
    return review_words,review_words_class

def load_user_user_graph_propagate_vector(order):
    vectors=pickle.load(open('./vectors%d.data'%order, 'rb'))
    return vectors

def output_simple_matrix(feature_length=10000):
    from pymongo import Connection
    feature_map={}
    f=open('./product.feature').readlines()
    key_map=dict()
    for line in open('./location_class.data'):
        line=line.replace('\n','').replace('\r','').split(' ')
        key_map[line[0].decode('utf8')]=int(line[1])
    for i in range(0,len(f)):
        if i>=feature_length:
            break
        feature_map[f[i].decode('utf8').split(' ')[0]]=i
    all_x=[]
    all_y=[]
    index=0
    #进度条相关参数
    users=Connection().jd.weibo_users
    total_count=users.count()
    bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    for user in users.find():
        features=[]
        for behavior in user['behaviors']:
            feature=str(behavior['item'])
            features.append(feature)
        vector=get_one_hot_vector(features, feature_map)
        if not vector.any():
            continue
        #y=get_location_class(user['location'],key_map)
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    #dump_user_vector(all_x,all_y,uids,'jd_user_simple')
    return all_x,all_y,uids
    return dump_train_valid_test(all_x, all_y, 'jd_user_simple')

def output_simple_review_matrix(feature_length=10000):
    from pymongo import Connection
    feature_map={}
    f=open('./review_word.feature').readlines()
    for i in range(0,len(f)):
        if i>=feature_length:
            break
        feature_map[f[i].decode('utf8').split(' ')[0]]=i
    all_x=[]
    all_y=[]
    index=0
    #进度条相关参数
    users=Connection().jd.weibo_users
    total_count=users.count()
    #bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    for user in users.find():
        features=[]
        for behavior in user['behaviors']:
            for word in behavior['parsed_review']['review_general']:
                feature=word
                features.append(feature)
        vector=get_one_hot_vector(features, feature_map)
        if not vector.any():
            continue
        #y=get_location_class(user['location'],key_map)
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        #bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    return all_x,all_y,uids
    #dump_user_vector(all_x,all_y,uids,'jd_review_simple')
    #return dump_train_valid_test(all_x, all_y, uids)

def output_shopping_tf_matrix(feature_length=3):
    from pymongo import Connection
    all_x=[]
    all_y=[]
    index=0
    #进度条相关参数
    users=Connection().jd.weibo_users
    total_count=users.count()
    bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    count_male=0
    for user in users.find():
        vector=numpy.zeros((feature_length))
        tf=dict()
        for behavior in user['behaviors']:
            try:
                tf[behavior['timestamp']]+=1
            except:
                tf[behavior['timestamp']]=1
        if len(tf)<feature_length:
            continue
        tf=sorted(tf.iteritems(), key=lambda d:d[1], reverse=True)
        for i in range(0,feature_length):
            vector[i]=tf[i][1]
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    return dump_train_valid_test(all_x, all_y, 'jd_user_simple')

def output_sentence_embedding_matrix(file_name1,file_name2):
    from pymongo import Connection
    all_x=[]
    all_y=[]
    index=0
    embedding=get_user_embedding(file_name1)
    #embedding=load_user_embedding(file_name1)
    #进度条相关参数
    users=Connection().jd.weibo_users
    total_count=users.count()
    bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    count_male=0
    for user in users.find():
        try:
            vector=embedding['USER_%d'%user['jd_id']]
        except:
            continue
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    #return dump_train_valid_test(all_x, all_y, 'jd_user_embedding')
    #dump_user_vector(all_x, all_y, uids, 'jd_user_embedding_with_item_class')
    dump_user_vector(all_x, all_y, uids, file_name2)

def output_graph_embedding_matrix(file_name1,file_name2,manual=False):
    from pymongo import Connection
    all_x=[]
    all_y=[]
    index=0
    users=Connection().jd.weibo_users
    uids=[]
    for user in users.find():
        if file_name1=='jd_graph_normalize2':
            uids.append('U'+str(user['jd_id']))
        else:
            uids.append(str(user['jd_id']))
    print 'Got uids'
    embedding=load_graph_embedding(set(uids),file_name1)
    #进度条相关参数
    users=Connection().jd.weibo_users
    total_count=users.count()
    bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    count_male=0
    for user in users.find():
        try:
            if file_name1=='jd_graph_normalize2':
                vector=embedding['U'+str(user['jd_id'])]
            else:
                vector=embedding[str(user['jd_id'])]
        except Exception as e:
            print e
            continue
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    #return dump_train_valid_test(all_x, all_y, 'jd_graph_embedding')
    dump_user_vector(all_x, all_y, uids, file_name2)
    #dump_user_vector(all_x, all_y, uids, 'jd_graph_embedding_from_review')
    #dump_user_vector(all_x, all_y, uids, 'jd_graph_embedding_from_user_and_product')

def output_goods_class_markov_matrix(manual=False):
    from pymongo import Connection
    feature_map={}
    f=open('./goods_class.feature1').readlines()
    tmp_feature=[]
    for index,line in enumerate(f):
        tmp_feature.append(line.decode('utf8').split(' ')[0])
    for index1,f1 in enumerate(tmp_feature):
        for index2,f2 in enumerate(tmp_feature):
            feature_map[(f1,f2)]=index1*len(tmp_feature)+index2
    all_x=[]
    all_y=[]
    index=0
    #进度条相关参数
    users=Connection().jd.weibo_users
    total_count=users.count()
    bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    for user in users.find():
        features=[]
        behaviors=user['behaviors']
        for i in range(len(behaviors)-1):
            feature1=behaviors[i]['item_class'][0]
            feature2=behaviors[i+1]['item_class'][0]
            features.append((feature1,feature2))
        vector=get_one_hot_vector(features,feature_map)
        if not vector.any():
            continue
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    dump_user_vector(all_x,all_y,uids,'jd_good_Markov')
    return
    return dump_train_valid_test(all_x, all_y, 'jd_user_simple')

def output_goods_class_matrix(order=1):
    from pymongo import Connection
    feature_map={}
    f=open('./goods_class.feature'+str(order)).readlines()
    tmp_feature=[]
    for index,line in enumerate(f):
        tmp_feature.append(line.decode('utf8').split(' ')[0])
    for index,f in enumerate(tmp_feature):
        feature_map[f]=index
    all_x=[]
    all_y=[]
    index=0
    #进度条相关参数
    users=Connection().jd.weibo_users
    total_count=users.count()
    bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    for user in users.find():
        features=[]
        behaviors=user['behaviors']
        for behavior in behaviors:
            feature=behavior['item_class'][order-1]
            features.append(feature)
        vector=get_one_hot_vector(features,feature_map)
        if not vector.any():
            continue
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    dump_user_vector(all_x,all_y,uids,'jd_good_class'+str(order))
    return
    return dump_train_valid_test(all_x, all_y, 'jd_user_simple')

def output_review_matrix(order,feature_length=1000):
    from pymongo import Connection
    feature_map1={}
    feature_map2={}
    index1=0
    index2=0
    for line in open('./review.feature'):
        line=line.decode('utf8')
        line=line.replace('\n','').replace('\r','').split(':')[1].split(',')
        for feature in line:
            feature_map1[feature]=index1
            feature_map2[feature]=index2
            index2+=1
        index1+=1
    print index1
    print index2
    all_x=[]
    all_y=[]
    index=0
    #进度条相关参数
    users=Connection().jd.weibo_users
    total_count=users.count()
    bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    for user in users.find():
        features=[]
        for behavior in user['behaviors']:
            review=behavior['review']
            review=review['review_title']+review['review_general']
            for feature in feature_map1:
                if feature in review:
                    features.append(feature)
        if features==[]:
            continue
        if order==1:
            vector=get_one_hot_vector(features, feature_map1)
        else:
            vector=get_one_hot_vector(features, feature_map2)
        #if sum(vector)<10:
        #    continue
        #if not vector.any():
        #    continue
        #y=get_location_class(user['location'],key_map)
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    dump_user_vector(all_x,all_y,uids,'jd_review%d'%order)
    #return dump_train_valid_test(all_x, all_y, 'jd_review2')

def output_review_length_matrix(feature_length=1000):
    from pymongo import Connection
    all_x=[]
    all_y=[]
    index=0
    #进度条相关参数
    users=Connection().jd.weibo_users
    total_count=users.count()
    bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    for user in users.find():
        features1=[]
        features2=[]
        for behavior in user['behaviors']:
            review=behavior['review']
            features1.append(len(review['review_general']))
            features2.append(len(review['review_title']))
        if features1==[]:
            continue
        if features2==[]:
            continue
        vector=[
                #numpy.max(features),
                numpy.mean(features1),
                numpy.var(features1),
                numpy.max(features2),
                numpy.min(features2),
                numpy.mean(features2),
                numpy.var(features2),
                ]
        vector=numpy.array(vector)
        if not vector.any():
            continue
        #y=get_location_class(user['location'],key_map)
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    dump_user_vector(all_x,all_y,uids,'jd_review_length')
    return
    return dump_train_valid_test(all_x, all_y, 'jd_review_length')

def output_review_star_matrix(feature_length=1000):
    from pymongo import Connection
    feature_map={}
    for i in range(0,6):
        feature_map[str(i)]=i
    all_x=[]
    all_y=[]
    index=0
    #进度条相关参数
    users=Connection().jd.weibo_users
    total_count=users.count()
    bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    for user in users.find():
        features=[]
        for behavior in user['behaviors']:
            feature=str(behavior['review']['review_stars'])
            features.append(feature)
        if features==[]:
            continue
        vector=get_one_hot_vector(features, feature_map)
        if not vector.any():
            continue
        #y=get_location_class(user['location'],key_map)
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    dump_user_vector(all_x,all_y,uids,'jd_review_star')
    return
    return dump_train_valid_test(all_x, all_y, 'jd_review_star')

def output_user_user_propagate_vectors(order):
    from pymongo import Connection
    all_x=[]
    all_y=[]
    index=0
    #进度条相关参数
    users=Connection().jd.weibo_users
    vectors=load_user_user_graph_propagate_vector(order)
    total_count=users.count()
    bar=progress_bar(total_count)
    finish_count=0
    uids=[]
    for user in users.find():
        try:
            vector=vectors[int(user['_id'])]
        except:
            continue
        if not vector.any():
            continue
        #y=get_location_class(user['location'],key_map)
        y=get_gender_class(user['gender'])
        #if y==-1:
        #    continue
        all_y.append(y)
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)
    dump_user_vector(all_x,all_y,uids,'jd_user_user_propagate'+str(order))
    return
    return dump_train_valid_test(all_x, all_y, 'jd_user_user_propagate')

def pca_process():
    from scipy.stats import pearsonr
    from minepy import MINE
    m = MINE()
    x,y=output_simple_review_matrix(100000)
    score=dict()
    for i in range(x.shape[1]):
        print i
        m.compute_score(y, x[:,i])
        score[i]=m.mic()
    score=sorted(score.items(), key=lambda d:d[1], reverse=True)
    fout=open('./score.data','w')
    for item in score:
        fout.write("%d %f\n"%(item[0],item[1]))

def get_y(uids, profile_key):
    from pymongo import Connection
    users=Connection().jd.weibo_users
    all_y=dict()
    for user in users.find():
        value=user['profile'][profile_key]
        try:
            value=value.index(1)
        except:
            value=-1
        all_y[user['_id']]=value
    y=map(lambda x:all_y[x], uids)
    return y

def merge_different_vectors(vector_folders, profile_key):
    all_uids=[]
    all_x=[]
    slow_folers={
            'jd_user_simple':output_simple_matrix,
            'jd_review_simple':output_simple_review_matrix,
            }
    print ' '.join(vector_folders)
    for folder in vector_folders:
        print folder
        if folder in slow_folers:
            x,y,uids=slow_folers[folder]()
            all_uids.append(uids)
            all_x.append(x)
            print 'done'
        else:
            all_uids.append(load_vector_from_text('uids.vector',folder,'list'))
            all_x.append(load_vector_from_text('x.matrix',folder,'NParray'))
    uids_order=all_uids[0]
    for uids in all_uids:
        uids_order=filter(lambda x:x in uids_order, uids)
    x=[]
    for uid in uids_order:
        tmp_x=[]
        for i,uids in enumerate(all_uids):
            index=uids.index(uid)
            tmp_x+=list(all_x[i][index])
        x.append(tmp_x)
    y=get_y(uids_order,profile_key)
    return dump_train_valid_test(x,y,uids_order)

def get_data(feature_length=1000):
    #return output_simple_review_matrix(feature_length)
    return merge_different_vectors([
        #'jd_user_simple',
        #'jd_user_embedding',
        #'jd_user_embedding_with_item_class',
        #'jd_user_embedding_from_review',
        #'graph_embedding_from_shopping_sequence',
        #'graph_embedding_from_review',
        #'graph_embedding_from_user_product',
        #'jd_good_Markov',
        #'jd_good_class1',
        #'jd_good_class2',
        #'jd_good_class3',
        #'jd_review1',
        #'jd_review2',
        #'jd_review_star',
        #'jd_review_length',
        #'jd_review_simple'
        #'jd_user_user_propagate'
        ])

if __name__=='__main__':
    print '=================Data Generator================='
    #output_simple_matrix(100)
    #output_simple_review_matrix(100)
    #output_graph_embedding_matrix('graph_vectors', 'graph_embedding_from_shopping_sequence')
    #output_graph_embedding_matrix('graph_vectors_from_review','graph_embedding_from_review')
    #output_graph_embedding_matrix('jd_graph_normalize2','graph_embedding_from_user_product')
    #output_goods_class_matrix(1)
    #output_goods_class_matrix(2)
    #output_goods_class_matrix(3)
    #output_goods_class_markov_matrix()
    #output_sentence_embedding_matrix('user_embedding_from_shopping_sequence','jd_user_embedding')
    #output_sentence_embedding_matrix('user_embedding_from_shopping_sequence_with_item_class','jd_user_embedding_with_item_class')
    output_sentence_embedding_matrix('user_embedding_from_review','jd_user_embedding_from_review')
    #output_review_matrix(1)
    #output_review_matrix(2)
    #output_review_star_matrix()
    #output_review_length_matrix()
    #test()
    #output_user_user_propagate_vectors(1)
    #output_user_user_propagate_vectors(2)
    #merge_different_vectors(['jd_good_class1'],'age')
    #pca_process()
