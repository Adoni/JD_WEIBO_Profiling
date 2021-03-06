#coding:utf8
import urllib2
import numpy
import json
import pickle
import sys
from my_progress_bar import progress_bar
from tools import save_vector_to_text
from tools import load_vector_from_text
from tools import doc2vec_embedding
from tools import load_doc2vec_embedding
from collections import Counter

def get_one_hot_vector(features, feature_map):
    vector=numpy.zeros((max(feature_map.values())+1))
    for f in features:
        try:
            vector[feature_map[f]]+=1.0
        except:
            continue
    if sum(vector)==0.0:
        return vector
    return vector

def get_one_hot_light_vector(features, feature_map):
    vector=dict()
    features=Counter(features)
    for f in features:
        if not f in feature_map:
            continue
        vector[feature_map[f]]=features[f]
    return vector

def dump_user_vector(x,uids,folder,dimention=0):
    print dimention
    print type(x[0])
    assert dimention>0 or type(x[0])!=dict
    print 'DUMP DATA'
    print 'X dimention:'+str(len(x[0]))
    if not len(x)==len(uids):
        raise Exception('x not equal with uids')
    save_vector_to_text(x,'x.matrix',folder,dimention=dimention)
    save_vector_to_text(uids,'uids.vector',folder)

def dump_train_valid_test(x,y,uids):
    from helper import balance
    from helper import balance2
    from collections import Counter
    print 'Dump'
    data=zip(uids,x,y)
    data=filter(lambda d:not d[2]==-1,data)
    data=balance(data,target_index=2)
    all_uids=map(lambda d:d[0],data)
    all_x=map(lambda d:d[1],data)
    all_y=map(lambda d:d[2],data)
    all_x=numpy.array(all_x)
    all_y=numpy.array(all_y)

    #进行归一化
    #b=numpy.max(all_x,axis=0)
    #c=numpy.min(all_x,axis=0)
    #pickle.dump((b,c),open('./normal','wb'))
    #for i in range(all_x.shape[1]):
    #    if b[i]==c[i]:
    #        all_x[:,i]=all_x[:,i]-all_x[:,i]
    #    else:
    #        all_x[:,i]=(all_x[:,i]-c[i])/(b[i]-c[i])

    print "Items Count: %d"%len(all_x)
    print "Dimention: %d"%len(all_x[0])
    print 'Count: '+str(Counter(all_y))
    return all_uids,all_x,all_y

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

def load_user_user_graph_propagate_vector(order):
    vectors=pickle.load(open('./vectors%d.data'%order, 'rb'))
    return vectors

def output_simple_matrix(feature_length=10000):
    from pymongo import Connection
    from collections import Counter
    feature_map={}
    f=open('./features/product.feature').readlines()
    for i in range(0,len(f)):
        if feature_length is not None and i>=feature_length:
            break
        feature_map[f[i].decode('utf8').split(' ')[0]]=i
    all_x=[]
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
            feature=str(int(behavior['item']))
            features.append(feature)
        vector=get_one_hot_light_vector(features, feature_map)
        if len(vector)==0:
            continue
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    dump_user_vector(all_x,uids,'jd_user_simple',dimention=len(feature_map))
    return all_x,uids

def output_simple_review_matrix(feature_length=10000):
    from pymongo import Connection
    feature_map={}
    f=open('./features/review_word.feature').readlines()
    for i in range(0,len(f)):
        if feature_length is not None and i>=feature_length:
            break
        word=f[i].decode('utf8').split(' ')[0]
        #feature_map[word]=word.encode('utf8')
        feature_map[word]=i
    all_x=[]
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
            for word in behavior['parsed_review']['review_general']:
                feature=word
                features.append(feature)
        vector=get_one_hot_light_vector(features, feature_map)
        #vector=get_one_hot_vector(features, feature_map)
        if len(vector)==0:
            continue
        #if not vector.any():
        #    continue
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    #return all_x,uids
    dump_user_vector(all_x,uids,'jd_review_simple',dimention=len(feature_map))
    #return dump_train_valid_test(all_x, all_y, uids)

def output_shopping_tf_matrix(feature_length=3):
    from pymongo import Connection
    all_x=[]
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
    index=0
    embedding=doc2vec_embedding(file_name1)
    #embedding=load_doc2vec_embedding(file_name1)
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
        #if y==-1:
        #    continue
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    #return dump_train_valid_test(all_x, all_y, 'jd_user_embedding')
    #dump_user_vector(all_x, all_y, uids, 'jd_user_embedding_with_item_class')
    dump_user_vector(all_x, uids, file_name2)

def output_graph_embedding_matrix(file_name1,file_name2,manual=False):
    from pymongo import Connection
    all_x=[]
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
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    #return dump_train_valid_test(all_x, all_y, 'jd_graph_embedding')
    dump_user_vector(all_x, uids, file_name2)
    #dump_user_vector(all_x, all_y, uids, 'jd_graph_embedding_from_review')
    #dump_user_vector(all_x, all_y, uids, 'jd_graph_embedding_from_user_and_product')

def output_goods_class_markov_matrix(manual=False):
    from pymongo import Connection
    feature_map={}
    f=open('./features/goods_class.feature1').readlines()
    tmp_feature=[]
    for index,line in enumerate(f):
        tmp_feature.append(line.decode('utf8').split(' ')[0])
    for index1,f1 in enumerate(tmp_feature):
        for index2,f2 in enumerate(tmp_feature):
            feature_map[(f1,f2)]=index1*len(tmp_feature)+index2
    all_x=[]
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
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    dump_user_vector(all_x,uids,'jd_good_Markov')
    return
    return dump_train_valid_test(all_x, all_y, 'jd_user_simple')

def output_goods_class_matrix(order=0):
    from pymongo import Connection
    feature_map={}
    f=open('./features/item_class_order_%d.feature'%order).readlines()
    tmp_feature=[]
    for index,line in enumerate(f):
        tmp_feature.append(line.decode('utf8').split(' ')[0])
    for index,f in enumerate(tmp_feature):
        feature_map[f]=index
    all_x=[]
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
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    dump_user_vector(all_x,uids,'jd_item_class_order_'+str(order))
    return

def output_review_matrix(order,feature_length=1000):
    from pymongo import Connection
    feature_map1={}
    feature_map2={}
    index1=0
    index2=0
    for line in open('./features/review.feature'):
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
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    dump_user_vector(all_x,uids,'jd_review%d'%order)
    #return dump_train_valid_test(all_x, all_y, 'jd_review2')

def output_review_length_matrix(feature_length=1000):
    from pymongo import Connection
    all_x=[]
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
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    dump_user_vector(all_x,uids,'jd_review_length')
    return
    return dump_train_valid_test(all_x, all_y, 'jd_review_length')

def output_review_star_matrix(feature_length=1000):
    from pymongo import Connection
    feature_map={}
    for i in range(0,6):
        feature_map[str(i)]=i
    all_x=[]
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
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    dump_user_vector(all_x,uids,'jd_review_star')
    return
    return dump_train_valid_test(all_x, all_y, 'jd_review_star')

def output_user_user_propagate_vectors(order):
    from pymongo import Connection
    all_x=[]
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
        all_x.append(vector)
        uids.append(user['_id'])
        index+=1
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    dump_user_vector(all_x,uids,'jd_user_user_propagate'+str(order))
    return
    return dump_train_valid_test(all_x, all_y, 'jd_user_user_propagate')

def output_review_embedding_matrix():
    from helper import get_mentions
    from pymongo import Connection
    from my_vector_reader import read_vectors
    all_x=[]
    #进度条相关参数
    users=Connection().jd.weibo_users
    bar=progress_bar(users.count())
    finish_count=0
    uids=[]
    mentions=get_mentions()
    #review_vocab,review_embedding=read_vectors('/mnt/data1/adoni/jd_data/vectors/word_vectors.data','utf8')
    review_vocab,review_embedding=read_vectors('../myword2vec/word_vectors.data','utf8')
    mentions=filter(lambda d:d in review_vocab,mentions)
    mention_embedding=map(lambda x:review_embedding[review_vocab.index(x)],mentions)
    vector_size=len(mention_embedding[0])
    for user in users.find():
        x=numpy.zeros(vector_size)
        review=' '.join(map(lambda d:d['review']['review_general'],user['behaviors']))
        for index,mention in enumerate(mentions):
            count=review.count(mention)
            x+=count*mention_embedding[index]
        if not x.any():
            continue
        all_x.append(x)
        uids.append(user['_id'])
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    dump_user_vector(all_x,uids,'user_review_embedding')

def output_user_embedding_with_LINE():
    from pymongo import Connection
    from my_vector_reader import read_vectors
    all_x=[]
    users=Connection().jd.weibo_users
    bar=progress_bar(users.count())
    finish_count=0
    uids=[]
    vocab,embedding=read_vectors('/mnt/data1/adoni/jd_data/raw_data/user_embedding_with_LINE_from_record_knn.data','utf8')
    embedding=zip(vocab,embedding)
    embedding=filter(lambda e:numpy.isfinite(e[1].sum()),embedding)
    embedding=dict(embedding)
    for user in users.find():
        if user['_id'] in embedding:
            x=embedding[user['_id']]
        else:
            print 'not in vocab'
            continue
        all_x.append(x)
        uids.append(user['_id'])
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    dump_user_vector(all_x,uids,'user_embedding_with_LINE')

def output_user_embedding_with_DeepWalk_cluster(ratio):
    from pymongo import Connection
    from my_vector_reader import simple_embedding_cluster_viewer
    all_x=[]
    users=Connection().jd.weibo_users
    bar=progress_bar(users.count())
    finish_count=0
    uids=[]
    viewer=simple_embedding_cluster_viewer('/mnt/data1/adoni/jd_data/vectors/user_embedding_from_path_and_labels_%0.2f.data'%ratio,'utf8')
    for user in users.find():
        neibors=viewer.get_closest_words(user['_id'])
        if neibors==[]:
            continue
        x=numpy.sum(map(lambda w:viewer[w],neibors),axis=0)
        all_x.append(x)
        uids.append(user['_id'])
        finish_count+=1
        bar.draw(value=finish_count)
    all_x=numpy.array(all_x)
    dump_user_vector(all_x,uids,'user_embedding_from_DeepWalk_cluster_%0.2f'%ratio)

def get_y(profile_key):
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
    return all_y

def merge_different_vectors(vector_folders, profile_key):
    all_uids=[]
    all_x=[]
    light_folers=[
            'jd_user_simple',
            'jd_review_simple',
            ]
    print ' '.join(vector_folders)
    for folder in vector_folders:
        print folder
        all_uids.append(load_vector_from_text('uids.vector',folder,'list'))
        if folder in light_folers:
            all_x.append(load_vector_from_text('x.matrix',folder,'LightArray'))
        else:
            all_x.append(load_vector_from_text('x.matrix',folder,'NParray'))
    print 'Load Done'
    if len(all_uids)==1:
        all_y=get_y(profile_key)
        all_y=map(lambda uid:all_y[uid], all_uids[0])
        return dump_train_valid_test(all_x[0],all_y,all_uids[0])
    uids_order=all_uids[0]
    for uids in all_uids:
        uids_order=filter(lambda x:x in uids_order, uids)
    all_y=get_y(profile_key)
    uids_order=filter(lambda x:x in all_y.keys(), uids_order)
    x=[]
    y=[]
    bar=progress_bar(len(uids_order))
    print '=============='
    print len(all_uids)
    print len(all_y)
    print len(uids_order)
    print '=============='
    for finish_count,uid in enumerate(uids_order):
        tmp_x=[]
        for i,uids in enumerate(all_uids):
            index=uids.index(uid)
            tmp_x+=list(all_x[i][index])
        x.append(tmp_x)
        y.append(all_y[uid])
        bar.draw(finish_count)
    return dump_train_valid_test(x,y,uids_order)

if __name__=='__main__':
    print '=================Data Generator================='
    #output_simple_matrix(None)
    #output_simple_review_matrix(None)
    #output_graph_embedding_matrix('graph_vectors', 'graph_embedding_from_shopping_sequence')
    #output_graph_embedding_matrix('graph_vectors_from_review','graph_embedding_from_review')
    #output_graph_embedding_matrix('jd_graph_normalize2','graph_embedding_from_user_product')
    #output_goods_class_matrix(1)
    #output_goods_class_matrix(2)
<<<<<<< HEAD
    output_goods_class_matrix(2)
=======
    #output_goods_class_matrix(2)
>>>>>>> f82e8d5f92eb2574d9101b29d7d69ce90d10ebc1
    #output_goods_class_markov_matrix()
    #output_sentence_embedding_matrix('user_embedding_from_shopping_sequence','jd_user_embedding')
    #output_sentence_embedding_matrix('user_embedding_from_shopping_sequence_with_item_class','jd_user_embedding_with_item_class')
    #output_sentence_embedding_matrix('user_embedding_from_review','jd_user_embedding_from_review')
    #output_review_matrix(1)
    #output_review_matrix(2)
    #output_review_star_matrix()
    #output_review_length_matrix()
    #test()
    #output_user_user_propagate_vectors(1)
    #output_user_user_propagate_vectors(2)
    #merge_different_vectors(['jd_good_class1'],'age')
    #pca_process()
    #output_review_embedding_matrix()
    #output_user_embedding_with_LINE()
    #output_user_embedding_with_DeepWalk_cluster(0.00)
    #output_user_embedding_with_DeepWalk_cluster(0.40)
    #output_user_embedding_with_DeepWalk_cluster(0.80)
