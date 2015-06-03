from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
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

def batch_test(attribute):
    all_features=[
        #'jd_user_simple',
        #'jd_review_simple',
        'jd_user_embedding',
        'jd_user_embedding_with_item_class',
        'jd_user_embedding_from_review',
        'graph_embedding_from_shopping_sequence',
        'graph_embedding_from_review',
        'graph_embedding_from_user_product',
        'jd_good_Markov',
        'jd_good_class1',
        'jd_good_class2',
        'jd_good_class3',
        'jd_review1',
        'jd_review2',
        'jd_review_star',
        'jd_review_length',
        'jd_user_user_propagate1',
        'jd_user_user_propagate2',
        'user_embedding_from_path_with_attributes_1.00',
        'user_embedding_from_path_with_attributes_0.75',
        'user_embedding_from_path_with_attributes_0.50',
        'user_embedding_from_path_with_attributes_0.25',
        'user_embedding_from_path_with_attributes_0.00',
        ]
    fout=open('./results/Experiments_results_%s.result'%attribute,'a')
    fout.write('='*30+'\n')
    fout.write(str(datetime.datetime.today())+'\n')
    f=open('heh.data','w')
    for count in range(2,3):
        fout.write('-'*20+'\n')
        fout.write('Feature Count: %d\n'%count)
        for features in combinations(all_features,count):
            data=merge_different_vectors(features,attribute)
            #data=disarrange_data2(data)
            #data=disarrange_data(data)
            for i in range(len(data[0])):
                f.write('%s %d\n'%(data[0][i],data[2][i]))
            clf=LogisticRegression()
            score=cross_validation.cross_val_score(clf, data[1],data[2],cv=10,scoring='accuracy')
            result='F1: %0.2f (+/- %0.2f) || Features:%s\n'%(score.mean(), score.std()*2, str(features))
            print result
            fout.write(result)

if __name__=='__main__':
    batch_test('gender')
