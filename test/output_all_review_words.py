from pymongo import Connection
from collections import Counter
from my_progress_bar import progress_bar

def output_all_review_words():
    users=Connection().jd.weibo_users
    all_reviews=[]
    for user in users.find():
        for behavior in user['behaviors']:
            for word in behavior['parsed_review']['review_general']:
                all_reviews.append(word)
    all_reviews=Counter(all_reviews)
    all_reviews=sorted(all_reviews.items(), key=lambda d:d[1], reverse=True)
    fout=open('./review.feature','w')
    for word in all_reviews:
        fout.write('%s %d\n'%(word[0].encode('utf8'),word[1]))

def output_all_shopping_items():
    users=Connection().jd.weibo_users
    all_items=[]
    bar=progress_bar(users.count())
    for index,user in enumerate(users.find()):
        for behavior in user['behaviors']:
            all_items.append(behavior['item'])
        bar.draw(index+1)
    all_items=Counter(all_items)
    all_items=sorted(all_items.items(), key=lambda d:d[1], reverse=True)
    fout=open('./review.feature','w')
    for word in all_items:
        fout.write('%d %d\n'%(word[0],word[1]))

def output_all_item_classes(order):
    users=Connection().jd.weibo_users
    all_items=[]
    bar=progress_bar(users.count())
    for index,user in enumerate(users.find()):
        for behavior in user['behaviors']:
            try:
                all_items.append(behavior['item_class'][order])
            except:
                continue
        bar.draw(index+1)
    all_items=Counter(all_items)
    all_items=sorted(all_items.items(), key=lambda d:d[1], reverse=True)
    fout=open('./item_class_order_%d.feature'%order,'w')
    for word in all_items:
        fout.write('%s %d\n'%(word[0].encode('utf8'),word[1]))

if __name__=='__main__':
    output_all_item_classes(2)
