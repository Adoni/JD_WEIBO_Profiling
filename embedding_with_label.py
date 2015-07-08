import random
import numpy
from my_progress_bar import progress_bar
MATRIX_PATH='/mnt/data1/adoni/jd_data/matrixes/'
VECTORS_PATH='/mnt/data1/adoni/jd_data/vectors/'
RAW_DATA_PATH='/mnt/data1/adoni/jd_data/raw_data/'

def get_labels(attribute,ratio):
    from pymongo import Connection
    users=Connection().jd.weibo_users
    labels=dict()
    uids_without_labels=[]
    bar=progress_bar(users.count())
    finish_count=0
    for user in users.find():
        try:
            label=user['profile'][attribute].index(1)
            if random.random()<ratio:
                labels[user['_id']]=label
            else:
                uids_without_labels.append(user['_id'])
        except:
            continue
        finish_count+=1
        bar.draw(finish_count)
    return labels,uids_without_labels

def embedding_with_labels(attribute_ratio,beta):
    import os
    labels,uids_without_labels=get_labels('gender',attribute_ratio)
    raw_file_name='user_path_with_attributes_0.00'
    label_file_name='labels'
    f_label=open(RAW_DATA_PATH+label_file_name+'.data','w')
    for uid in labels:
        f_label.write("%s %d\n"%(uid,labels[uid]))
    #embedding_file_name='user_embedding_from_path_and_labels_%0.2f_%0.2f'%(attribute_ratio,beta)
    embedding_file_name='user_embedding_from_path_and_labels_%0.2f_%0.2f'%(attribute_ratio,beta)
    command='~/myword2vec/myword2vec -train %s.data -labels %s.data -beta %f -output %s.data -cbow 1 -size 100 -window 5 -negative 0 -hs 1 -sample 1e-3 -threads 20 -binary 0'%(RAW_DATA_PATH+raw_file_name,RAW_DATA_PATH+label_file_name,beta, VECTORS_PATH+embedding_file_name)
    os.system(command)
    output_matrix(embedding_file_name,embedding_file_name)
    from data_generator import save_vector_to_text
    save_vector_to_text(uids_without_labels,'uids_none_attributes.vector',embedding_file_name)

def get_all_uids():
    from pymongo import Connection
    users=Connection().jd.weibo_users
    uids=[]
    for user in users.find({},{'_id':1}):
        uids.append(user['_id'].encode('utf8'))
    return uids

def output_matrix(file_name,folder):
    import numpy
    from data_generator import save_vector_to_text
    from my_vector_reader import read_vectors
    file_name=VECTORS_PATH+file_name+'.data'
    X=[]
    vocab=[]
    all_uids=get_all_uids()
    vectors=read_vectors(file_name,'utf8','DICT')
    uids=filter(lambda uid:uid in vectors, all_uids)
    X=numpy.array(map(lambda uid:vectors[uid], uids))
    save_vector_to_text(X,'x.matrix',folder)
    save_vector_to_text(uids,'uids.vector',folder)

def main():
    #for beta in [0.0,0.3,0.6,0.9]:
    for beta in [0.5]:
        for ratio in numpy.arange(0.00,0.85,0.10):
            embedding_with_labels(ratio,beta)

if __name__=='__main__':
    #get_review_edges()
    main()
    import os
    #os.system('python svm.py')
    #review_deep_walk()
