#coding:utf8
from pymongo import Connection
users=Connection().jd.weibo_users
def show_location():
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
    for age in ages:
        print age[0],age[1]

if __name__=='__main__':
    #show_location()
    show_age()
