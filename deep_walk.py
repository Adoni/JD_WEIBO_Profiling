import random
import numpy
from settings import RAW_DATA_DIR
from settings import VECTORS_DIR
from settings import MATRIXES_DIR
class Graph:
    def __init__(self, file_name):
        self.graph=[]
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
        self.graph=dict_graph

    def to_list_graph(self):
        self.graph=self.graph.items()
        self.degrees=[]
        self.indexes=dict()
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
    if weights==[]:
        return None
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd <= 0:
            return i

def get_a_random_path_from_graph(graph,length):
    from my_progress_bar import progress_bar
    path=[]
    node_index=weighted_random_select(graph.degrees)
    node=graph[node_index]
    path.append(node[0])
    bar=progress_bar(length-1)
    for i in range(length-1):
        neibor_index=weighted_random_select(node[1]['weights'])
        neibor=node[1]['neibors'][weighted_random_select(node[1]['weights'])]
        try:
            node_index=graph.index_of(neibor)
        except:
            node_index=weighted_random_select(graph.degrees)
        if node_index is None:
            i-=1
            continue
        node=graph[node_index]
        path.append(node[0])
        bar.draw(i)
    return path

def get_attributes(attribute, ratio):
    from pymongo import Connection
    attributes=dict()
    users=Connection().jd.weibo_users
    for user in users.find():
        try:
            attributes[user['_id']]=attribute+str(user['profile'][attribute].index(1))
        except:
            continue
        if random.random()>ratio:
            attributes[user['_id']]=attribute+'None'
    return attributes

def deep_walk(total_nodes_count, attribute_ratio,attribute_type,insert_type):
    print attribute_ratio
    import random
    import os
    attributes=get_attributes(attribute_type,attribute_ratio)
    none_attributes=filter(lambda uid:'None' in attributes[uid], attributes.keys())
    attributes=dict(filter(lambda x:'None' not in x[1], attributes.items()))
    print 'Get attributes done'
    #graph=Graph(RAW_DATA_DIR+'knn_graph_from_shopping_record.data')
    graph=Graph(RAW_DATA_DIR+'knn_graph_from_review.data')
    graph.to_list_graph()
    print 'Get graph done'
    path=get_a_random_path_from_graph(graph, total_nodes_count)
    raw_file_name='user_path_with_attributes_%0.2f'%attribute_ratio
    embedding_file_name='user_embedding_from_path_with_attributes_%0.2f'%attribute_ratio
    fout_with_attribute=open(RAW_DATA_DIR+raw_file_name+'.data','w')
    #fout_with_attribute.write(' '.join(path)+'\n')
    new_path=[]
    for node in path:
        new_path.append(node)
        if node in attributes:
            new_path.append(attributes[node])
    fout_with_attribute.write(' '.join(new_path)+'\n')
    print '\nEmbedding...'
    command='~/word2vec/word2vec -train %s.data -output %s.data -cbow 0 -size 100 -window %d -negative 0 -hs 1 -sample 1e-3 \
    -threads 20 -binary 0'%(RAW_DATA_DIR+raw_file_name, VECTORS_DIR+embedding_file_name,5)
    print command
    os.system(command)
    print '\nEmbedding Done'
    output_matrix(embedding_file_name,embedding_file_name)
    from data_generator import save_vector_to_text
    save_vector_to_text(none_attributes,'uids_none_attributes.vector',embedding_file_name)

def get_all_uids():
    from pymongo import Connection
    users=Connection().jd.weibo_users
    uids=[]
    for user in users.find({},{'_id':1}):
        uids.append(user['_id'])
    return uids

def output_matrix(file_name,folder):
    import numpy
    from my_vector_reader import read_vectors
    from data_generator import save_vector_to_text
    file_name=VECTORS_DIR+file_name+'.data'
    uids=get_all_uids()
    embedding=read_vectors(file_name,'utf8','DICT')
    vocab=filter(lambda uid:uid in embedding,uids)
    X=map(lambda uid:embedding[uid],vocab)
    X=numpy.array(X)
    save_vector_to_text(X,'x.matrix',folder)
    save_vector_to_text(vocab,'uids.vector',folder)

if __name__=='__main__':
    #for ratio in numpy.arange(start=0.00,stop=0.85,step=0.10):
    #    deep_walk(10000000,ratio,'gender','old')
    deep_walk(10000000,0.0,'gender','old')
    #output_matrix('user_embedding_with_LINE_from_record_knn','user_embedding_with_LINE_from_record_knn')
