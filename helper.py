def get_mentions():
    file_name='./features/mention.feature'
    mentions=[]
    for line in open(file_name):
        mentions+=line[:-1].decode('utf8').split(':')[1].split(',')
    return mentions

if __name__=='__main__':
    get_mentions()
