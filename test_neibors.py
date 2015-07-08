from my_vector_reader import simple_embedding_cluster_viewer
from pymongo import Connection
viewer=simple_embedding_cluster_viewer('/mnt/data1/adoni/jd_data/vectors/user_embedding_from_path_and_labels_0.00.data','utf8')
users=Connection().jd.weibo_users
labels=dict()
for user in users.find():
    labels[user['_id']]=user['gender']
for user in users.find():
    print labels[user['_id']]
    print ' '.join(map(lambda d:labels[d], viewer.get_closest_words(user['_id'])))
