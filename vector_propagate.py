import numpy

def get_vectors(path):
    vectors=dict()
    uids=[line[:-1] for line in open(path+'/'+'uids.vector')]
    x=numpy.loadtxt(path+'/'+'x.matrix')
    for index, uid in enumerate(uids):
        vectors[int(uid)]=numpy.array(x[index])
    return vectors

def get_graph(file_name):
    graph=dict()
    for index,line in enumerate(open(file_name)):
        print index
        line=line[:-1].split(' ')
        try:
            graph[int(line[0])][int(line[1])]=float(line[2])
        except:
            graph[int(line[0])]=dict()
            graph[int(line[0])][int(line[1])]=float(line[2])
    return graph

def propagate(vectors,graph,max_step,alpha):
    vectors_new=dict()
    vector_size=len(vectors[vectors.keys()[0]])
    print vector_size
    # Remove uids in vectors which not included in graph
    for uid in vectors.keys():
        if uid not in graph:
            vectors.pop(uid)

    # Calculate the sum of the eages of node i
    weights=dict()
    for uid in vectors.keys():
        weight=0.0
        for neibor,w in graph[uid].iteritems():
            if neibor not in vectors:
                continue
            weight+=w
        if weight==0.0:
            vectors.pop(uid)
            continue
        weights[uid]=weight

    # Initialize the vectors_new
    for uid in vectors:
        vectors_new[uid]=numpy.zeros((vector_size))
    for step in range(max_step):
        print 'Iteration: %d'%step
        for uid in vectors_new:
            vector=alpha*vectors[uid]
            weight=weights[uid]
            for neibor,w in graph[uid].iteritems():
                if neibor not in vectors:
                    continue
                vector+=(1-alpha)*w/weight*vectors[neibor]
            vectors_new[uid]=vector
        for uid in vectors_new:
            vectors[uid]=vectors_new[uid]
    import pickle
    pickle.dump(vectors,open('./vectors1.data','wb'))

if __name__=='__main__':
    vectors=get_vectors('/mnt/data1/adoni/jd_data/matrixes/jd_review2')
    graph=get_graph('/mnt/data1/adoni/jd_data/user_user_graph.data')
    print len(vectors.keys())
    print len(graph.keys())
    propagate(vectors, graph, 10, 0.9)
