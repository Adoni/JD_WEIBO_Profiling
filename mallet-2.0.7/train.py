import os
<<<<<<< HEAD
commands=[]
data_dir='/Users/sunxiaofei/workspace/TMPDATA/jd_data/matrixes/mallet/data.mallet'
commands.append("bin/mallet import-file --token-regex '[0-9]+' --input %s --output data.mallet"%data_dir)
commands.append("bin/mallet train-classifier --input data.mallet --trainer MaxEnt --trainer NaiveBayes --training-portion 0.9 --num-trials 10")
for command in commands:
    os.system(command)
=======
def convert():
    mentions=[line[:-1].split(' ') for line in open('./mention_with_number.data')]
    mentions=dict(mentions)
    review_constraint_words=[line[:-1].split(' ') for line in open('./review_constraint_words.constraints')]
    fout=open('review.constraints','w')
    for c in review_constraint_words:
        if c[0] in mentions:
            fout.write('%s %s\n'%(mentions[c[0]],' '.join(c[1:])))

def train():
    commands=[]
    data_dir='/mnt/data1/adoni/jd_data/matrixes/mallet'

    commands.append("bin/mallet import-file \
            --input %s/review_%s.mallet \
            --token-regex '[0-9]+'\
            --output train_data.mallet"%(data_dir,'train'))

    commands.append("bin/mallet import-file \
            --input %s/review_%s.mallet \
            --token-regex '[0-9]+'\
            --use-pipe-from train_data.mallet \
            --output test_data.mallet"%(data_dir,'test'))

    commands.append("bin/mallet train-classifier \
            --training-file train_data.mallet \
            --testing-file test_data.mallet \
            --trainer NaiveBayes")

    for command in commands:
        os.system(command)

def train_unlabel():
    commands=[]

    commands.append("bin/vectors2vectors \
            --input train_data.mallet \
            --output unlabeled_data.mallet \
            --hide-targets")

    commands.append("bin/mallet train-classifier\
            --training-file   unlabeled_data.mallet \
            --testing-file    train_data.mallet \
            --trainer 'MaxEntGETrainer,gaussianPriorVariance=0.1,constraintsFile=\"review.constraints\"'\
            --report test:accuracy")
    for command in commands:
        os.system(command)

if __name__=='__main__':
    #convert()
    train()
    train_unlabel()
>>>>>>> f82e8d5f92eb2574d9101b29d7d69ce90d10ebc1
