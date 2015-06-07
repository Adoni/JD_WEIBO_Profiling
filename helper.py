import random
MATRIX_PATH='/mnt/data1/adoni/jd_data/matrixes/'
VECTORS_PATH='/mnt/data1/adoni/jd_data/vectors/'
RAW_DATA_PATH='/mnt/data1/adoni/jd_data/raw_data/'
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

    def add_attribute_edges(self, attributes, ratio, weight):
        print set(attributes.values())
        nodes=self.graph.keys()
        for attribute in set(attributes.values()):
            self.graph[attribute]={
                    'neibors':[],
                    'weights':[],
                    }
        for node in nodes:
            if node not in attributes:
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

def get_attributes(attribute, ratio):
    from pymongo import Connection
    attributes=dict()
    users=Connection().jd.weibo_users
    for user in users.find():
        try:
            attributes[user['_id']]=attribute+str(user['profile'][attribute].index(1))
        except:
            attributes[user['_id']]=attribute+'None'
        if random.random()>ratio:
            attributes[user['_id']]=attribute+'None'
    return attributes

def deep_walk(total_nodes_count, attribute_ratio,attribute_type):
    print attribute_ratio
    import sys
    import random
    import os
    attributes=get_attributes(attribute_type,attribute_ratio)
    none_attributes=filter(lambda x:x[1]==attribute_type+'None',attributes.items())
    none_attributes=map(lambda x:x[0].encode('utf8'),none_attributes)
    attributes=dict(filter(lambda x:x[1]!=attribute_type+'None',attributes.items()))
    print 'Get attributes done'
    print set(attributes.values())
    graph=Graph('/mnt/data1/adoni/jd_data/raw_data/jd_graph_from_shopping_record.data')
    #graph.add_attribute_edges(attributes,ratio=attribute_ratio,weight=1)
    graph.to_list_graph()
    print 'Get graph done'
    pathes=[]
    while total_nodes_count>0:
        length=100
        pathes.append(get_a_random_path_from_graph(graph, length))
        total_nodes_count-=length
        sys.stdout.write('\r%d'%total_nodes_count)
        sys.stdout.flush()
    raw_file_name=RAW_DATA_PATH+'user_path_with_attributes_%0.2f'%attribute_ratio
    embedding_file_name=VECTORS_PATH+'user_embedding_from_path_with_attributes_%0.2f'%attribute_ratio
    fout_with_attribute=open(raw_file_name,'w')
    for path in pathes:
        #fout_with_attribute.write(' '.join(path)+'\n')
        new_path=[]
        for node in path:
            new_path.append(node)
            if node not in none_attributes:
                new_path.append(attributes[node])
        fout_with_attribute.write(' '.join(new_path)+'\n')
    print '\nEmbedding...'
    command='./word2vec -train %s.data -output %s.data -cbow 0 -size 200 -window 7 -negative 0 -hs 1 -sample 1e-3 -threads 20 -binary 0'%(raw_file_name,embedding_file_name)
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
    deep_walk(10000000,1.0,'gender')
    deep_walk(10000000,0.8,'gender')
    deep_walk(10000000,0.6,'gender')
    deep_walk(10000000,0.4,'gender')
    deep_walk(10000000,0.2,'gender')
    deep_walk(10000000,0.0,'gender')
