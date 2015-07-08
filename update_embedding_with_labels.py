from my_vector_reader import read_vectors
VECTOR_DIR='/mnt/data1/adoni/jd_data/vectors/'
def get_labels_and_review():
    from pymongo import Connection
    users=Connection().jd.weibo_users
def update_embedding():
    pass
def get_reviews():
    pass
def logistic_regression():
    vocab,embedding=read_vectors(VECTOR_DIR+'word_vectors.data','utf8')

if __name__=='__main__':
    logistic_regression()
