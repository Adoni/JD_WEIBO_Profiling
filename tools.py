from settings import MATRIXES_DIR
import numpy
def save_vector_to_text(vector, file_name, folder):
    import os
    path=MATRIXES_DIR+folder+'/'
    print 'Try to save vector in '+path+file_name
    if not os.path.exists(path):
        os.makedirs(path)
    if type(vector[0])==int or type(vector[0])==str or type(vector[0])==unicode:
        fout=open(path+file_name,'w')
        for item in vector:
            fout.write(str(item)+'\n')
        return
    if type(vector[0])==numpy.ndarray:
        numpy.savetxt(path+file_name,vector)
        return
    if type(vector[0])==dict:
        fout=open(path+file_name,'w')
        for item in vector:
            item=' '.join(map(lambda x:str(x)+':'+str(item[x]),item.keys()))+'\n'
            fout.write(item)
        return
    print 'Fail to save vector'
    print 'Vector type should be list or numpy.ndarray'

def load_vector_from_text(file_name, folder, file_type):
    import os
    path=MATRIXES_DIR+folder+'/'
    print 'Try to load vector in '+path+file_name
    if file_type=='list':
        fout=open(path+file_name)
        vector=[line[:-1] for line in open(path+file_name)]
        return vector
    if file_type=='NParray':
        vector=numpy.loadtxt(path+file_name,dtype='float64')
        return vector
    if file_type=='LightArray':
        fout=open(path+file_name)
        dimension=0
        for line in fout:
            line=line[:-1].split(' ')
            line=map(lambda d:int(d.split(':')[0]),line)
            if max(line)>dimension:
                dimension=max(line)
        print dimension
        vector=[]
        fout=open(path+file_name)
        for line in fout:
            line=line[:-1].split(' ')
            v=numpy.zeros((dimension+1))
            for item in map(lambda d:d.split(':'),line):
                v[int(item[0])]=int(item[1])
            vector.append(v)
        return vector
    print 'Fail to load vector'
    print 'Vector type should be list or numpy.ndarray'
    return None

def doc2vec_embedding(file_name):
    import sys
    import gensim
    from pymongo import Connection

    users=Connection().jd.jd_users
    dimensionality_size=200
    window_size=8
    workers=5
    min_count=5

    # load sentences
    finish_count=0
    total_count=users.find({'got_review':True}).count()
    #total_count=users.count()
    sentences = []
    print total_count
    old_review=''
    for user in users.find({'got_review':True}):
    #for user in users.find():
        if finish_count%10000==0:
            sys.stdout.write("\r%f"%(finish_count*1.0/total_count))
            sys.stdout.flush()
        finish_count+=1
        content=[]
        for behavior in user['behaviors']:
            #content.append(str(behavior['item']))
            #content.append(behavior['item_class'][0])
            review=' '.join(behavior['review']['parsed_review_general'])
            if review==old_review:
                continue
            old_review==review
            content+=review.split()
        for ch in [' ','\n','\r','\u3000']:
            while 1:
                try:
                    content.remove(ch)
                except:
                    break
        #print ' '.join(content)
        if len(content)<10:
            continue
        sentence = gensim.models.doc2vec.LabeledSentence(words=content,labels=['USER_%d'%user['_id']])
        sentences.append(sentence)

    print 'load corpus completed...'

    # train word2vc
    model = gensim.models.Doc2Vec(sentences,size=200,window=7, workers=20,min_count=3,sample=1e-3)
    model.save_word2vec_format('/mnt/data1/adoni/jd_data/vectors/'+file_name+'.data',binary=False)
    print 'embedding done'
    return model

def load_doc2vec_embedding(file_name):
    import gensim
    print 'Loading user embedding'
    embedding=gensim.models.Word2Vec.load_word2vec_format('/mnt/data1/adoni/jd_data/'+file_name+'.data',binary=False)
    print 'Done'
    return embedding

if __name__=='__main__':
    load_vector_from_text('x.matrix','jd_user_simple','LightArray')
