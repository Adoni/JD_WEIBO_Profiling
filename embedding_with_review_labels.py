import random
import numpy
from my_progress_bar import progress_bar
MATRIX_PATH='/mnt/data1/adoni/jd_data/matrixes/'
VECTORS_PATH='/mnt/data1/adoni/jd_data/vectors/'
RAW_DATA_PATH='/mnt/data1/adoni/jd_data/raw_data/'

def get_labels():
    from helper
    labels=dict()
    for line in open('./features/mention.feature'):
        line=line[:-1].split(':')
        for word in line[1].split(','):
            print word+' '+line[0]

def embedding_with_labels(attribute_ratio):
    import os
    labels,uids_without_labels=get_labels('gender',attribute_ratio)
    raw_file_name='user_path_with_attributes_0.00'
    label_file_name='labels'
    f_label=open(RAW_DATA_PATH+label_file_name+'.data','w')
    for uid in labels:
        f_label.write("%s %d\n"%(uid,labels[uid]))
    embedding_file_name='user_embedding_from_path_and_labels_%0.2f'%attribute_ratio
    command='~/myword2vec/myword2vec -train %s.data -labels %s.data -output %s.data -cbow 1 -size 100 -window 5 -negative 0 -hs 1 -sample 1e-3 -threads 20 -binary 0'%(RAW_DATA_PATH+raw_file_name,RAW_DATA_PATH+label_file_name, VECTORS_PATH+embedding_file_name)
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
    file_name=VECTORS_PATH+file_name+'.data'
    X=[]
    vocab=[]
    uids=get_all_uids()
    for i,line in enumerate(open(file_name)):
        if line[0]=='U':
            continue
        line=line[:-1].split()
        if not len(line)==101:
            print len(line)
            continue
        word=line[0]
        if word not in uids:
            continue
        vector=map(lambda a:float(a), line[1:])
        X.append(vector)
        vocab.append(word)
    X=numpy.array(X)
    save_vector_to_text(X,'x.matrix',folder)
    save_vector_to_text(vocab,'uids.vector',folder)

def main():
    for ratio in numpy.arange(0.00,0.85,0.05):
        embedding_with_labels(ratio)

if __name__=='__main__':
    get_labels()
