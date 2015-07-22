from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BaseNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from data_generator import merge_different_vectors
import numpy
from itertools import combinations
from sklearn import cross_validation
import datetime

def disarrange_data(data):
    import random
    size=len(data[0])
    print len(data[0])
    print len(data[1])
    print len(data[2])
    print data[2][:100]
    for index in range(size-1):
        i=index
        j=random.randint(index+1,size-1)
        data[0][i],data[0][j]=data[0][j],data[0][i]
        data[1][i],data[1][j]=data[1][j],data[1][i]
        data[2][i],data[2][j]=data[2][j],data[2][i]
    print data[2][:100]
    return data

def disarrange_data2(data):
    disarranged_data=[
            [[],[],[]],
            [[],[],[]]
            ]
    size=len(data[0])
    for i in range(size):
        gender=data[2][i]
        disarranged_data[gender][0].append(data[0][i])
        disarranged_data[gender][1].append(data[1][i])
        disarranged_data[gender][2].append(data[2][i])
    data=[[],[],[]]
    for i in range(size/2):
        data[0].append(disarranged_data[0][0][i])
        data[1].append(disarranged_data[0][1][i])
        data[2].append(disarranged_data[0][2][i])
        data[0].append(disarranged_data[1][0][i])
        data[1].append(disarranged_data[1][1][i])
        data[2].append(disarranged_data[1][2][i])
    return data

def single_test(feature, attribute):
    from sklearn.metrics import f1_score
    from sklearn.metrics import recall_score
    from sklearn.metrics import accuracy_score
    from data_generator import load_vector_from_text
    import random
    data=merge_different_vectors([feature],attribute)
    none_attribute_uids=load_vector_from_text('uids_none_attributes.vector',feature,'list')
    none_attribute_uids=filter(lambda x:x in data[0],none_attribute_uids)
    alpha=0.2*len(data[0])/len(none_attribute_uids)
    train_data=[[],[]]
    test_data=[[],[]]
    for index,uid in enumerate(data[0]):
        if uid in none_attribute_uids and random.random()<alpha:
        #if random.random()<0.2:
            test_data[0].append(data[1][index])
            test_data[1].append(data[2][index])
        else:
            train_data[0].append(data[1][index])
            train_data[1].append(data[2][index])
    print len(test_data[1]),sum(test_data[1]),len(train_data[1]),sum(train_data[1])
    clf=LogisticRegression()
    clf.fit(train_data[0], train_data[1])
    predicted_y=clf.predict(test_data[0])
    test_accuracy=accuracy_score(test_data[1],predicted_y)
    test_recall=recall_score(test_data[1],predicted_y)
    test_f1=f1_score(test_data[1],predicted_y)
    print 'F1 of test data (%d %d): %0.2f'%(sum(test_data[1]),len(test_data[1])-sum(test_data[1]),test_f1)
    print 'Accuracy of test data (%d %d): %0.2f'%(sum(test_data[1]),len(test_data[1])-sum(test_data[1]),test_accuracy)
    predicted_y=clf.predict(train_data[0])
    train_accuracy=accuracy_score(train_data[1],predicted_y)
    train_recall=recall_score(train_data[1],predicted_y)
    train_f1=f1_score(train_data[1],predicted_y)
    print 'F1 of train data (%d %d): %0.2f'%(sum(train_data[1]),len(train_data[1])-sum(train_data[1]),train_f1)
    return [test_accuracy,test_recall,test_f1,train_accuracy,train_recall,train_f1]

def batch_test(attribute, min_size=1, max_size=1):
    print '\n'
    print 'Attribute: %s'%attribute
    print '\n'
    all_features=[
        'jd_user_simple',
        'jd_review_simple',
        #'jd_user_embedding',
        #'jd_user_embedding_with_item_class',
        #'jd_user_embedding_from_review',
        #'graph_embedding_from_shopping_sequence',
        #'graph_embedding_from_review',
        #'graph_embedding_from_user_product',
        #'jd_good_Markov',
        #'jd_item_class_order_2',
        #'jd_review1',
        #'jd_review2',
        #'jd_review_star',
        #'jd_review_length',
        #'jd_user_user_propagate1',
        #'jd_user_user_propagate2',
        #'user_embedding_from_path_with_attributes_1.00',
        #'user_embedding_from_path_with_attributes_0.90',
        #'user_embedding_from_path_with_attributes_0.80',
        #'user_embedding_from_path_with_attributes_0.70',
        #'user_embedding_from_path_with_attributes_0.60',
        #'user_embedding_from_path_with_attributes_0.50',
        #'user_embedding_from_path_with_attributes_0.40',
        #'user_embedding_from_path_with_attributes_0.30',
        #'user_embedding_from_path_with_attributes_0.20',
        #'user_embedding_from_path_with_attributes_0.10',
        #'user_embedding_from_path_with_attributes_0.00',
        #'new_user_embedding_from_path_with_attributes_0.00',
        #'multi_user_embedding_100_0.80',
        #'multi_user_embedding_001_0.80',
        #'multi_user_embedding_101_0.80',
        #'review_deep_walk_embedding',
        #'user_embedding_from_path_and_labels_0.00',
        #'user_embedding_from_path_and_labels_0.20',
        #'user_embedding_from_path_and_labels_0.40',
        #'user_embedding_from_path_and_labels_0.60',
        #'user_embedding_from_path_and_labels_0.80',
        #'user_review_embedding',
        #'user_embedding_with_LINE',
        #'user_embedding_from_DeepWalk_cluster',
        #'user_embedding_from_DeepWalk_cluster_0.40',
        #'user_embedding_from_DeepWalk_cluster_0.80',
        #'user_embedding_with_LINE',
        #'user_embedding_from_path_with_attributes_0.00',
        #'user_embedding_from_path_with_attributes_0.10',
        #'user_embedding_from_path_with_attributes_0.80',
        ]
    fout=open('./results/Experiments_results_%s.result'%attribute,'a')
    fout.write('='*30+'\n')
    fout.write(str(datetime.datetime.today())+'\n')
    f=open('heh.data','w')
    for count in range(min_size,max_size+1):
        fout.write('-'*20+'\n')
        fout.write('Feature Count: %d\n'%count)
        for features in combinations(all_features,count):
            data=merge_different_vectors(features,attribute)
            #data=disarrange_data2(data)
            #data=disarrange_data(data)
            #clf=LogisticRegression()
            #clf=BaseNB()
            #clf=GaussianNB()
            clf=SVC()
            #clf=MultinomialNB()
            score_f1=cross_validation.cross_val_score(clf, data[1],data[2],cv=5,scoring='f1')
            score_accuracy=cross_validation.cross_val_score(clf, data[1],data[2],cv=5,scoring='accuracy')
            result='F1: %0.2f (+/- %0.2f) || Accuracy: %0.2f (+/- %0.2f) || Features:%s\n'%(score_f1.mean(), score_f1.std()*2, score_accuracy.mean(), score_accuracy.std()*2, str(features))
            print result
            fout.write(result)

def test_embedding():
    for beta in [0.5]:
    #for beta in [0.0,0.3,0.6,0.9]:
        x=[]
        y=[]
        for ratio in numpy.arange(0.0,0.85,0.10):
            print ratio
            tmpy=[]
            for i in range(1):
                tmpy.append(single_test('user_embedding_from_path_and_labels_%0.2f_%0.2f'%(ratio,beta),'gender'))
                #tmpy.append(single_test('user_embedding_from_path_with_attributes_%0.2f'%(ratio),'gender'))
            x.append(ratio)
            y.append(list(numpy.average(tmpy,axis=0)))
        fout=open('./results/single.result','a')
        fout.write(str(beta)+'\n')
        fout.write(str(x)+'\n')
        fout.write(str(y)+'\n')

if __name__=='__main__':
    print 'Test'
    #single_test('new_user_embedding_from_path_with_attributes_1.00','gender')
    #single_test('new_user_embedding_from_path_with_attributes_0.80','gender')
    #single_test('new_user_embedding_from_path_with_attributes_0.60','gender')
    #single_test('new_user_embedding_from_path_with_attributes_0.40','gender')
    #single_test('new_user_embedding_from_path_with_attributes_0.20','gender')
    #single_test('new_user_embedding_from_path_with_attributes_0.00','gender')
    #single_test('user_embedding_from_path_with_attributes_0.00','gender')
    #single_test('user_embedding_from_path_with_attributes_0.80','gender')
    #single_test('jd_user_simple','gender')
    batch_test('gender',1,1)
    batch_test('age',1,1)
    batch_test('location',1,1)
    #batch_test('age',1,1)
    #batch_test('new_age',1,1)
    #batch_test('location',1,1)
    #test_embedding()
