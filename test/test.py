#coding:utf8
from pymongo import Connection
def show_location():
    users=Connection().jd.weibo_users
    locations=dict()
    for user in users.find():
        if user['location'] is None:
            continue
        location=user['location'].split(' ')[0]
        try:
            locations[location]+=1
        except:
            locations[location]=1
    locations=sorted(locations.iteritems(), key=lambda d:d[1], reverse=True)
    for i in locations:
        print i[0],i[1]


def show_age():
    users=Connection().jd.weibo_users
    ages=dict()
    for user in users.find():
        if user['birthday'] is None:
            continue
        if u'年' not in user['birthday']:
            continue
        age=user['birthday']
        age=age[0:age.find(u'年')]
        if len(age)<4:
            age='19'+age
        try:
            ages[int(age)]+=1
        except:
            ages[int(age)]=1
    ages=sorted(ages.iteritems(), key=lambda d:d[0], reverse=False)
    print ages

def insert_age_vector():
    from collections import Counter
    users=Connection().jd.weibo_users
    all_vec=[]
    for user in users.find():
        profile=user['profile']
        if user['birthday'] is None:
            age_vec=[0,0]
            profile['age']=age_vec
            users.update({'_id':user['_id']},{'$set':{'profile':profile}})
            continue
        if u'年' not in user['birthday']:
            age_vec=[0,0]
            profile['age']=age_vec
            users.update({'_id':user['_id']},{'$set':{'profile':profile}})
            continue
        age=user['birthday']
        age=age[0:age.find(u'年')]
        if len(age)<4:
            age='19'+age
        age=int(age)
        if age<1950 or age>2010:
            age_vec=[0,0]
            profile['age']=age_vec
            users.update({'_id':user['_id']},{'$set':{'profile':profile}})
            continue
        if age<1988:
            age_vec=[1,0]
        else:
            age_vec=[0,1]
        profile['age']=age_vec
        users.update({'_id':user['_id']},{'$set':{'profile':profile}})
        all_vec.append(str(age_vec))
    print Counter(all_vec)

if __name__=='__main__':
    #show_location()
    show_age()
    #insert_age_vector()
