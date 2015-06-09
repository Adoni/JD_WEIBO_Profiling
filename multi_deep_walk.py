import random
import numpy
MATRIX_PATH='/mnt/data1/adoni/jd_data/matrixes/'
VECTORS_PATH='/mnt/data1/adoni/jd_data/vectors/'
RAW_DATA_PATH='/mnt/data1/adoni/jd_data/raw_data/'
class Graph:
    def __init__(self, edges):
        self.graph=[]
        dict_graph=dict()
        for edge in edges:
            try:
                dict_graph[edge[0]]['neibors'].append(edge[1])
                dict_graph[edge[0]]['weights'].append(float(edge[2]))
            except Exception as e:
                dict_graph[edge[0]]={
                        'neibors':[edge[1]],
                        'weights':[float(edge[2])],
                        }
        self.graph=dict_graph
        self.to_list_graph()

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

    def add_attribute_edges(self, attributes, ratio, weight):
        #print set(attributes.values())
        nodes=self.graph.keys()
        for attribute in set(attributes.values()):
            self.graph[attribute]={
                    'neibors':[],
                    'weights':[],
                    }
        for node in nodes:
            if node not in attributes:
                continue
            if 'None' in attribute:
                continue
            self.graph[node]['neibors'].append(attributes[node])
            self.graph[node]['weights'].append(weight*sum(self.graph[node]['weights']))
            self.graph[attributes[node]]['neibors'].append(node)
            self.graph[attributes[node]]['weights'].append(1)

    def index_of(self, node_name):
        return self.indexes[node_name]

def weighted_random_select(weights):
    if weights==[]:
        return None
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        #print i
        #print w
        rnd -= w
        if rnd < 0:
            return i

def get_a_random_path_from_graph(graph,length):
    path=[]
    node_index=weighted_random_select(graph.degrees)
    if node_index is None:
        return []
    try:
        node=graph[node_index]
    except:
        print node
    path.append(node[0])
    for i in range(length-1):
        neibor=node[1]['neibors'][weighted_random_select(node[1]['weights'])]
        node_index=graph.index_of(neibor)
        if node_index is None:
            continue
        node=graph[node_index]
        path.append(node[0])
    return path

def get_attributes_edges(attribute, ratio):
    #ratio is the ratio of the count of users with attribute
    from pymongo import Connection
    users=Connection().jd.weibo_users
    edges=[]
    none_attribute_uids=[]
    for user in users.find():
        try:
            attribute_value=attribute+str(user['profile'][attribute].index(1))
            edge=[
                    [user['_id'],attribute_value,1],
                    [attribute_value,user['_id'],1],
                    ]
            if random.random()>ratio:
                none_attribute_uids.append(user['_id'])
            else:
                edges+=edge
        except:
            continue
            #none_attribute_uids.append(user['_id'])
    return edges,none_attribute_uids

def deep_walk(graph, total_nodes_count):
    from my_progress_bar import progress_bar
    import sys
    import random
    import os
    bar=progress_bar(total_nodes_count)
    finish_count=0
    pathes=[]
    while finish_count<total_nodes_count:
        length=100
        pathes.append(get_a_random_path_from_graph(graph, length))
        finish_count+=length
        bar.draw(finish_count)
    return pathes

def output_pathes(pathes,file_name):
    fout=open(RAW_DATA_PATH+file_name+'.data','w')
    for path in pathes:
        fout.write(' '.join(path)+'\n')

def multi_deep_walk(attribute_ratio):
    import os
    graphs=[]
    graphs.append(Graph(map(lambda line:line[:-1].split(' '),open('/mnt/data1/adoni/jd_data/raw_data/jd_graph_from_shopping_record.data'))))
    attribute_edges,none_attribute_uids=get_attributes_edges('gender',attribute_ratio)
    graphs.append(Graph(attribute_edges))
    pathes=[]
    pathes+=deep_walk(graphs[0],5000000)
    pathes+=deep_walk(graphs[0],1000000)
    raw_file_name='multi_user_path_with_attributes_%0.2f'%attribute_ratio
    embedding_file_name='multi_user_embedding_from_path_with_attributes_%0.2f'%attribute_ratio
    output_pathes(pathes,raw_file_name)
    command='./word2vec -train %s.data -output %s.data -cbow 0 -size 200 -window 5 -negative 0 -hs 1 -sample 1e-3 -threads 20 -binary 0'%(RAW_DATA_PATH+raw_file_name, VECTORS_PATH+embedding_file_name)
    os.system(command)
    output_matrix(embedding_file_name,embedding_file_name)
    from data_generator import save_vector_to_text
    save_vector_to_text(none_attribute_uids,'uids_none_attributes.vector',embedding_file_name)

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
    for ratio in numpy.arange(0.0,0.85,0.05):
        multi_deep_walk(ratio)
