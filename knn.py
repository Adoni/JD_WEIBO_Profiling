#coding:utf8
import operator
import time
from numpy import *
from math import sqrt
from my_progress_bar import progress_bar
from settings import RAW_DATA_DIR

def construct_knn():
    from pymongo import Connection
    users=Connection().jd.weibo_users
    bar=progress_bar(users.count())
    shopping_record={}
    for index,user in enumerate(users.find()):
        uid=int(user['_id'])
        items=map(lambda behavior:behavior['item'],user['behaviors'])
        shopping_record[uid]=set(items)
        bar.draw(index+1)

    finish_count=0
    bar=progress_bar(len(shopping_record))
    fout=open(RAW_DATA_DIR+'knn_graph_from_shopping_record.data','w')
    print len(shopping_record)
    for uid1 in shopping_record:
        finish_count+=1
        score=dict()
        for uid2 in shopping_record:
            n=len(shopping_record[uid1] & shopping_record[uid2])
            if n==0:
                continue
            score[uid2]=1.0*n/(len(shopping_record[uid1])+len(shopping_record[uid2])- n)
        score = sorted(score.items(), key=lambda d:d[1], reverse=True)
        for edge in score:
            #if edge[1]==1.00:
                #print ''
                #print uid1
                #print edge[0]
                #print shopping_record[uid1]
                #print shopping_record[edge[0]]
            line='%d %d %f\n'%(uid1, edge[0], edge[1])
            fout.write(line)
        bar.draw(finish_count)

if __name__ == '__main__':
    construct_knn()
