import numpy
from my_progress_bar import progress_bar
from utils import *
import re
import mmap
class LogisticRegression:
    def __init__(self,fpath,n_in,n_out,window_size):
        from my_vector_reader import read_vectors
        self.starting_alpha = 0.025
        self.vocab,self.embedding=read_vectors(fpath,'utf8')
        self.W = numpy.zeros((n_in, n_out))  # initialize W 0
        self.b = numpy.zeros(n_out)          # initialize bias 0
        self.sentence_len=1000
        self.window_size=window_size

    def file2ws(self,fpath):
        """
        file to wordstream: lazily read words from a file as an iterator
        """
        with open(fpath) as fin:
            word_pattern = re.compile(r'(.*?)\s')
            mf = mmap.mmap(fin.fileno(), 0, access = mmap.ACCESS_READ)
            for match in word_pattern.finditer(mf):
                word = match.group(1)
                if word: yield word

    def train_single(self,x,y,lr=0.1,L2_reg=0.00):
        p_y_given_x = softmax(numpy.dot(x, self.W) + self.b)
        d_y = y - p_y_given_x
        pass

    def get_y(self,attribute):
        from pymongo import Connection
        from collections import Counter
        users=Connection().jd.weibo_users
        y=dict()
        for user in users.find():
            value=numpy.array([user['profile'][attribute]])
            if not value.any():
                continue
            y[user['_id']]=value
        return y

    def train(self,x_path,attribute):
        train_words = list(self.file2ws(x_path))
        Y=self.get_y(attribute)
        ntotal = len(train_words)
        nprocessed = 0
        bar=progress_bar(ntotal)
        alpha=self.starting_alpha
        while nprocessed<ntotal:
            alpha = max(self.starting_alpha * (1-nprocessed/(ntotal+1.)),
                                        self.starting_alpha * 0.0001)
            sentence = []
            while nprocessed < ntotal and len(sentence) < self.sentence_len:
                word = train_words[nprocessed]
                nprocessed += 1
                try:
                    word_index = self.vocab.index(word)
                except:
                    word_index=-1
                sentence.append(word_index)
            for ipivot, pivot in enumerate(sentence):
                left = max(0, ipivot - self.window_size)
                right = min(len(sentence)-1, ipivot+self.window_size)
                neighborhood = [sentence[n] for n in range(left, right+1) if sentence[n] >= 0]
                neu1 = numpy.sum(self.embedding[neighborhood,:], axis = 0)
                neu1=numpy.array([neu1])
                p_y_given_x = softmax(numpy.dot(neu1, self.W) + self.b)
                if pivot not in self.vocab:
                    continue
                y=Y[self.vocab[pivot]]
                d_y = y - p_y_given_x
                self.W += alpha * numpy.dot(neu1.T, d_y)# - alpha * L2_reg * self.W
                self.b += alpha * numpy.mean(d_y, axis=0)
                neu1e = alpha*numpy.dot(d_y,self.W.T)
                self.embedding[neighborhood, :]+=neu1e
            bar.draw(nprocessed)
    def dump_embedding(self):
        fout=open('new_embedding.data','w')
        for index,w in enumerate(self.vocab):
            fout.write(str(w))
            for num in self.embedding[i]:
                fout.write(' %f'%num)
            fout.write('\n')

if __name__=='__main__':
    fpath='/Users/sunxiaofei/workspace/TMPDATA/jd_data/vectors/user_embedding_from_path_with_attributes_0.00.data'
    lr=LogisticRegression(fpath,n_in=100,n_out=2,window_size=5)
    fpath='/Users/sunxiaofei/workspace/TMPDATA/jd_data/vectors/user_path_with_attributes_0.00.data'
    lr.train(fpath,'gender')
    lr.dump_embedding()
