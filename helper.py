def get_mentions():
    file_name='./features/mention.feature'
    mentions=[]
    for line in open(file_name):
        mentions+=line[:-1].decode('utf8').split(':')[1].split(',')
    return mentions

def balance(data,target_index):
    from collections import Counter
    import random
    counts=Counter(map(lambda d:d[target_index],data))
    min_count=min(counts.values())
    ratio=dict()
    for target in counts:
        ratio[target]=1.0*min_count/counts[target]
    balanced_data=[]
    for d in data:
        if random.random()>ratio[d[target_index]]:
            continue
        balanced_data.append(d)
    return balanced_data

def balance2(data,target_index):
    from collections import Counter
    import random
    counts=Counter(map(lambda d:d[target_index],data))
    min_count=min(counts.values())
    ratio=dict()
    for target in counts:
        ratio[target]=0
    balanced_data=[]
    for d in data:
        if ratio[d[target_index]]>=min_count:
            continue
        balanced_data.append(d)
        ratio[d[target_index]]+=1
    return balanced_data

def output_mention_and_number():
    mentions=get_mentions()
    all_words=[line[:-1].decode('utf8').split(' ')[0] for line in open('./features/review_word.feature')]
    fout=open('./mallet-2.0.7/mention_with_number.data','w')
    for m in mentions:
        if m in all_words and all_words.index(m)<4000:
            fout.write('%s %d\n'%(m.encode('utf8'),all_words.index(m)))

def output_mention_and_count(attribute):
    from pymongo import Connection
    from my_progress_bar import progress_bar
    from collections import Counter

    mentions=get_mentions()
    mentions=dict(zip(mentions,[[0,0,0] for mention in mentions]))
    users=Connection().jd.weibo_users
    bar=progress_bar(users.count())
    values=[]
    for index,user in enumerate(users.find()):
        bar.draw(index)
        try:
            f=user['profile'][attribute].index(1)
        except:
            continue
        values.append(f)
    values=Counter(values)
    min_value=min(values.values())
    for key in values:
        values[key]=min_value*1.0/values[key]
    print values

    bar=progress_bar(users.count())
    for index,user in enumerate(users.find()):
        try:
            f=user['profile'][attribute].index(1)
        except:
            continue
        for behavior in user['behaviors']:
            for w in behavior['parsed_review']['review_general']:
                if w in mentions:
                    mentions[w][f]+=1
        bar.draw(index)
    mentions=sorted(mentions.items(),key=lambda d:sum(d[1]),reverse=True)
    print ''
    for m in mentions:
        if sum(m[1])<1000:
            break
        for i in range(len(m[1])):
            m[1][i]='%0.1f'%(m[1][i]*values[i])
        print m[0].encode('utf8'),m[1]


if __name__=='__main__':
    output_mention_and_count('gender')
    output_mention_and_count('age')
    output_mention_and_count('location')
