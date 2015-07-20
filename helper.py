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

if __name__=='__main__':
    output_mention_and_number()
