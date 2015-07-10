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

if __name__=='__main__':
    x=[1,2,3,4,5,6,7,8]
    y=[1,1,0,1,1,0,1,1]
    print balance(zip(x,y),target_index=1)
