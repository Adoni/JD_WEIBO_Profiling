import numpy
fname='/mnt/data1/adoni/jd_data/matrixes/user_embedding_with_LINE/x.matrix'
from my_vector_reader import read_vectors
vocab,embedding=read_vectors('/mnt/data1/adoni/jd_data/raw_data/user_embedding_with_LINE_from_record_knn.data','utf8')
x=embedding
for xx in x:
    if not numpy.isfinite(xx.sum()):
        print xx
