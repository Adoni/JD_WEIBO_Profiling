import random
MATRIX_PATH='/mnt/data1/adoni/jd_data/matrixes/'
VECTORS_PATH='/mnt/data1/adoni/jd_data/vectors/'
RAW_DATA_PATH='/mnt/data1/adoni/jd_data/raw_data/'
class Graph:
    def __init__(self, file_name):
        self.graph=[]
        self.degrees=[]
        self.indexes=dict()
        graph_file=open(file_name)
        dict_graph=dict()
        for line in graph_file:
            line=line[:-1].split(' ')
            try:
                dict_graph[line[0]]['neibors'].append(line[1])
                dict_graph[line[0]]['weights'].append(float(line[2]))
            except Exception as e:
                dict_graph[line[0]]={
                        'neibors':[line[1]],
                        'weights':[float(line[2])],
                        }
        self.graph=dict_graph.items()
        for i,node in enumerate(self.graph):
            self.degrees.append(len(node[1]['neibors']))
            self.indexes[node[0]]=i
        print '========='
        print len(self.degrees)
        print len(self.graph)
        print len(self.indexes)
        print '========='

    def __getitem__(self, node_index):
        if node_index>=len(self.graph):
            print node_index
            print len(self.graph)
            print len(self.degrees)
        return self.graph[node_index]

    def index_of(self, node_name):
        return self.indexes[node_name]

def weighted_random_select(weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

def get_a_random_path_from_graph(graph,length):
    path=[]
    node_index=weighted_random_select(graph.degrees)
    try:
        node=graph[node_index]
    except:
        print node
    path.append(node[0])
    for i in range(length-1):
        neibor=node[1]['neibors'][weighted_random_select(node[1]['weights'])]
        node_index=graph.index_of(neibor)
        node=graph[node_index]
        path.append(node[0])
    return path

def get_attributes():
    from pymongo import Connection
    attributes=dict()
    users=Connection().jd.weibo_users
    for user in users.find():
        if user['gender']is None:
            attributes[user['_id']]='None'
        else:
            attributes[user['_id']]=user['gender'].encode('utf8')
    return attributes

def deep_walk(total_nodes_count, attribute_ratio):
    print attribute_ratio
    import sys
    import random
    import os
    attributes=get_attributes()
    print 'Get attributes done'
    graph=Graph('/mnt/data1/adoni/jd_data/raw_data/jd_graph_from_shopping_record.data')
    print 'Get graph done'
    pathes=[]
    while total_nodes_count>0:
        length=100
        pathes.append(get_a_random_path_from_graph(graph, length))
        total_nodes_count-=length
        sys.stdout.write('\r%d'%total_nodes_count)
        sys.stdout.flush()
    raw_file_name_1=RAW_DATA_PATH+'user_path.data'
    raw_file_name_2=RAW_DATA_PATH+'user_path_with_attributes_%0.2f.data'%attribute_ratio
    embedding_file_name_1=VECTORS_PATH+'user_embedding_from_path.data'
    embedding_file_name_2=VECTORS_PATH+'user_embedding_from_path_with_attributes_%0.2f.data'%attribute_ratio
    fout_only_user=open(raw_file_name_1,'w')
    fout_with_attribute=open(raw_file_name_2,'w')
    for path in pathes:
        fout_only_user.write(' '.join(path)+'\n')
        path_with_attribute=[]
        for node in path:
            path_with_attribute.append(node)
            if random.random()<attribute_ratio:
                path_with_attribute.append(attributes[node])
        fout_with_attribute.write(' '.join(path_with_attribute)+'\n')
    print '\nEmbedding...'
    command='./word2vec -train %s -output %s -cbow 0 -size 200 -window 7 -negative 0 -hs 1 -sample 1e-3 -threads 20 -binary 0'%(raw_file_name_2,embedding_file_name_2)
    os.system(command)
    print '\nEmbedding Done'
    output_matrix('user_embedding_from_path_with_attributes_%0.2f'%attribute_ratio,'user_embedding_from_path_with_attributes_%0.2f'%attribute_ratio)

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
    file_name='/mnt/data1/adoni/jd_data/vectors/'+file_name+'.data'
    X=[]
    vocab=[]
    uids=get_all_uids()
    for i,line in enumerate(open(file_name)):
        if line[0]=='U':
            continue
        line=line[:-1].split()
        if not len(line)==201:
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

if __name__=='__main__':
    deep_walk(10000000,1.)
    deep_walk(10000000,0.75)
    deep_walk(10000000,0.5)
    deep_walk(10000000,0.25)
    deep_walk(10000000,0.)
    #output_matrix('user_embedding_from_path','user_embedding_from_path')
    #output_matrix('user_embedding_from_path_with_attributes','user_embedding_from_path_with_attributes')
